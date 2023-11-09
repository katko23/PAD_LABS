# Car Sharing App

Car Sharing App is a platform that allows users to share rides, create ride offers, and engage in real-time chat with other users. This README provides an overview of the project, installation instructions, and usage guidelines.

## Features

- User Registration: Register as a new user with a username, email, and password.
- User Login: Authenticate users with email and password.
- Ride Booking: Users can book a ride by providing details like user ID, driver ID, origin, and destination.
- Create Ride Offer: Create a new ride offer with details such as driver ID, origin, destination, departure time, available seats, and fare.
- Real-Time Chat: Users can engage in real-time chat with other users.
- Store Data: Data from user registration, ride booking, and ride offers are stored in a PostgreSQL database.

## Installation and Setup

### Prerequisites

- Docker
- Docker Compose

### Steps

1. Clone the project repository to your local machine:

   ```bash
   git clone https://github.com/katko23/PAD_LABS.git

2. Navigate to the project directory:

   ```bash
   cd PAD_LABS
   ```
   
3. Build and run the Docker containers:

   ```bash
   docker-compose up -d
   ```
   
4. Access the app by opening a web browser and navigating to http://localhost:3000 (for the API Gateway).


