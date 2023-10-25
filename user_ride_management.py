import datetime
import jwt

from flask import Flask, request, jsonify

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a secure secret key


# Sample data to simulate user and ride management
users = {}
rides = {}
ride_id_counter = 1

# Endpoint for User Registration
@app.route('/api/users/register', methods=['POST'])
def user_register():
    global users
    data = request.json
    username = data['username']
    email = data['email']
    password = data['password']
    user_id = str(len(users) + 1)
    users[user_id] = {
        'userId': user_id,
        'username': username,
        'email': email,
        'createdAt': '2023-09-20T08:00:00Z'
    }
    return jsonify(users[user_id]), 201

# Endpoint for User Login
@app.route('/api/users/login', methods=['POST'])
def user_login():
    data = request.json
    email = data['email']
    password = data['password']

    for user_id, user_data in users.items():
        if user_data['email'] == email and password == 'password123':  # Replace with actual user password validation
            token = jwt.encode({'user_id': user_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
                               app.config['SECRET_KEY'], algorithm='HS256')
            return jsonify({'token': token, 'userId': user_id, 'username': user_data['username']}), 200

    return jsonify({'message': 'Invalid email or password'}), 401

# Endpoint for Booking a Ride
@app.route('/api/rides/book', methods=['POST'])
def book_ride():
    global ride_id_counter,rides
    data = request.json
    user_id = data['userId']
    driver_id = data['driverId']
    origin = data['origin']
    destination = data['destination']
    ride_id = 'ride' + str(ride_id_counter)
    ride_id_counter += 1
    rides[ride_id] = {
        'rideId': ride_id,
        'userId': user_id,
        'driverId': driver_id,
        'origin': origin,
        'destination': destination,
        'status': 'pending'
    }
    return jsonify(rides[ride_id]), 201

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
    ride_id = 'ride' + str(ride_id_counter)
    ride_id_counter += 1
    rides[ride_id] = {
        'rideId': ride_id,
        'driverId': driver_id,
        'origin': origin,
        'destination': destination,
        'departureTime': departure_time,
        'seatsAvailable': seats_available,
        'fare': fare
    }
    return jsonify(rides[ride_id]), 201

# Endpoint for Viewing Available Rides
@app.route('/api/rides/available', methods=['GET'])
def get_available_rides():
    # Implement filtering based on optional parameters
    return jsonify(list(rides.values())), 200

if __name__ == '__main__':
    app.run(debug=True)
