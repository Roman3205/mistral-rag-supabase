from quart import Quart, make_response, jsonify
from blueprints.chat import chat_bp
import database

app = Quart(__name__)

app.register_blueprint(chat_bp, url_prefix='/chat')

@app.before_serving
async def db_connect():
    await database.init_db()

@app.before_request
async def check_db_connection():
    if database.supabase is None:
        return jsonify({"error": "Database not initialized"}), 500

@app.route('/ping', methods=['GET'])
async def test():
    response = await make_response('pong')
    response.headers['Content-Type'] = 'text/plain'
    response.status_code = 200
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3011)