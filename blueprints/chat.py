from quart import Blueprint, request, jsonify
import os
from mistralai.client import Mistral
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
import database

load_dotenv()

client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/message', methods=['POST'])
async def handle_message():
    body = await request.get_json()

    if not body or 'message' not in body:
        return {'error': 'Invalid request, "message" field is required'}, 400
    
    chat_response = await client.chat.complete_async(
        model="mistral-medium-latest",
        messages=[{"role": "user", "content": body['message']}],
        # response_format={'type': 'json_object'},
        # stream=True
    )

    return chat_response.choices[0].message.content

@chat_bp.route('/rag/upload', methods=['POST'])
async def handle_rag():
    # local file testing
    # if os.path.exists('data/text.txt'):
    #     with open('data/text.txt', 'r') as file:
    #         data = file.read()

    files = await request.files
    if 'file' not in files:
        return jsonify({"error": "File not found"}), 400

    file = files['file']

    if file.filename == '':
        return jsonify({"error": "File was not choosen"}), 400
        
    if not file.filename.endswith('.txt'):
        return jsonify({"error": "Please upload file of .txt"}), 400

    try:
        data = file.read().decode('utf-8')

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)

        chunks = splitter.split_text(data)
        # alternative
        # chunks = splitter.create_documents([data])
        # chunkText = list(map(lambda c: c.page_content, chunks))

        embeddings = await client.embeddings.create_async(
            model="mistral-embed",
            inputs=chunks
        )

        processedChunks = list(map(lambda c: {'content': c, 'embedding': embeddings.data[chunks.index(c)].embedding}, chunks))
        await database.supabase.table('book_docs').insert(processedChunks).execute()

        return 'Uploaded successfully'
    except UnicodeDecodeError:
        return jsonify({"error": "Decoding error, ensure you saved file in UTF-8"}), 400

@chat_bp.route('/rag/retrieve', methods=["POST"])
async def handle_retrieve():
    body = await request.get_json()
    if not body or 'query' not in body:
        return jsonify({"error": "No message provided"}), 400
    
    query = body.get('query')

    embedding = await client.embeddings.create_async(
        model="mistral-embed",
        inputs=[query]
    )

    result = await database.supabase.rpc('match_book_docs', {'query_embedding': embedding.data[0].embedding, 'match_threshold': 0.6, 'match_count': 5}).execute()

    chunks = result.model_dump().get('data')

    context = list(map(lambda c: c.get('content'), chunks))
    print(context)
    chat_response = await client.chat.complete_async(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": f"Book context: {context} - Question: {query}"}],
        )

    return chat_response.choices[0].message.content