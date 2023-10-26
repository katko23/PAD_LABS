import datetime
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import pymongo
import pika
import time


app = Flask(__name__)
socketio = SocketIO(app)

time.sleep(100)

# Set up a connection to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()

# Declare a RabbitMQ queue for chat messages
channel.queue_declare(queue='chat_messages')


# MongoDB connection setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["chat_db"]
collection = db["chat_messages"]

@app.route('/')
def index():
    return 'Chat Microservice is running'

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('join')
def handle_join(data):
    room = data['room']
    join_room(room)
    print(f'User joined room {room}')

@socketio.on('leave')
def handle_leave(data):
    room = data['room']
    leave_room(room)
    print(f'User left room {room}')


@socketio.on('chat_message')
def handle_chat_message(data):
    message = data['message']
    user_id = data['userId']

    # Publish the message to RabbitMQ
    channel.basic_publish(exchange='', routing_key='chat_messages', body=message)

    emit('chat_message', {'message': message, 'userId': user_id}, broadcast=True)


@socketio.on('send_message')
def handle_send_message(data):
    sender = data['sender']
    receiver = data['receiver']
    message = data['message']

    # Insert the message into the MongoDB collection
    chat_message = {
        "sender": sender,
        "receiver": receiver,
        "message": message,
        "timestamp": datetime.datetime.now()
    }
    collection.insert_one(chat_message)

    # Broadcast the message to both sender and receiver in the room
    room1 = f'{sender}_{receiver}'
    room2 = f'{receiver}_{sender}'
    emit('receive_message', chat_message, room=room1)
    emit('receive_message', chat_message, room=room2)

if __name__ == '__main__':
    socketio.run(app, debug=True)
