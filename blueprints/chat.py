from quart import Blueprint, request
import os
from mistralai.client import Mistral
from dotenv import load_dotenv

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