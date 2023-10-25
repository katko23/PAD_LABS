from flask import Flask
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

# WebSocket Endpoint for Real-time Chat
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('chat_message')
def handle_chat_message(data):
    message = data['message']
    user_id = data['userId']
    emit('chat_message', {'message': message, 'userId': user_id}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)