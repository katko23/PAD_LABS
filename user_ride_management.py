import datetime
import jwt
import pika
import psycopg2
import time
from flask import Flask, request, jsonify
from threading import Thread


app = Flask(__name__)

time.sleep(100)

# Set up a connection to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()

# Declare the same RabbitMQ queue for chat messages
channel.queue_declare(queue='chat_messages')

# Callback function to handle received chat messages
def handle_chat_message(ch, method, properties, body):
    print(f"Received chat message: {body}")
    # Handle the received chat message here

# Set up a consumer to receive chat messages in a separate thread
def consume_messages():
    channel.basic_consume(queue='chat_messages', on_message_callback=handle_chat_message, auto_ack=True)
    print('Chat message consumer is running')
    channel.start_consuming()

# Start the message consumer in a separate thread
message_consumer_thread = Thread(target=consume_messages)
message_consumer_thread.start()

# Database connection setup
conn = psycopg2.connect(
    dbname="padmicro1",
    user="client",
    password="client",
    host="postgres",  # Update host to the service name of the PostgreSQL container
    port=5432  # Default PostgreSQL port
)

cursor = conn.cursor()

# Endpoint for User Registration
@app.route('/api/users/register', methods=['POST'])
def user_register():
    data = request.json
    username = data['username']
    email = data['email']
    password = data['password']

    # Hash the password for security (use a proper password hashing library)
    hashed_password = "hash_password_here"

    # Insert user data into the 'users' table
    cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                   (username, email, hashed_password))
    conn.commit()

    return jsonify({'message': 'User registered successfully'}), 201

# Endpoint for User Login
@app.route('/api/users/login', methods=['POST'])
def user_login():
    data = request.json
    email = data['email']
    password = data['password']

    # Verify user credentials (validate email and password)
    cursor.execute("SELECT user_id, username, password FROM users WHERE email = %s", (email,))
    user_data = cursor.fetchone()

    if user_data and user_data[2] == "hash_password_here":  # Replace with actual password validation
        user_id, username, _ = user_data
        token = jwt.encode({'user_id': user_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
                           app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token, 'userId': user_id, 'username': username}), 200

    return jsonify({'message': 'Invalid email or password'}), 401

# Endpoint for Booking a Ride
@app.route('/api/rides/book', methods=['POST'])
def book_ride():
    data = request.json
    user_id = data['userId']
    driver_id = data['driverId']
    origin = data['origin']
    destination = data['destination']

    # Insert ride booking data into the 'rides' table
    cursor.execute("INSERT INTO rides (user_id, driver_id, origin, destination, status) VALUES (%s, %s, %s, %s, %s)",
                   (user_id, driver_id, origin, destination, 'pending'))
    conn.commit()

    return jsonify({'message': 'Ride booked successfully'}), 201

# Endpoint for Creating a New Ride Offer
@app.route('/api/rides/create', methods=['POST'])
def create_ride_offer():
    data = request.json
    driver_id = data['driverId']
    origin = data['origin']
    destination = data['destination']
    departure_time = data['departureTime']
    seats_available = data['seatsAvailable']
    fare = data['fare']

    # Insert ride offer data into the 'rides' table
    cursor.execute("INSERT INTO rides (user_id, driver_id, origin, destination, departure_time, seats_available, fare, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                   (driver_id, origin, destination, departure_time, seats_available, fare, 'available'))
    conn.commit()

    return jsonify({'message': 'Ride offer created successfully'}), 201

# Endpoint for Viewing Available Rides
@app.route('/api/rides/available', methods=['GET'])
def get_available_rides():
    # Retrieve available rides from the 'rides' table
    cursor.execute("SELECT * FROM rides WHERE status = 'available'")
    available_rides = cursor.fetchall()

    # Convert the query result to a list of dictionaries
    rides_data = []
    for row in available_rides:
        ride_id, user_id, driver_id, origin, destination, departure_time, seats_available, fare, status = row
        rides_data.append({
            'rideId': ride_id,
            'userId': user_id,
            'driverId': driver_id,
            'origin': origin,
            'destination': destination,
            'departureTime': departure_time.isoformat(),
            'seatsAvailable': seats_available,
            'fare': fare,
        })

    return jsonify(rides_data), 200

if __name__ == '__main__':
    app.run(debug=True)
