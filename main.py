from flask import Flask, redirect, url_for, render_template, request, jsonify, session
from flask_pymongo import PyMongo
from bson import ObjectId
from flask_cors import CORS

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/my_app"
db = PyMongo(app).db

app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.secret_key = 'BAD_SEKRET_KEY'
CORS(app, supports_credentials=True)

@app.route('/')
def sign_up():
    return render_template('index.html')


@app.route('/api/login', methods=['POST'])
def get_user():
    data = request.json
    print("Received login data:", data)
    try:
        user = db.users.find_one({"username": data['username'], "password": data['password']})
        if user:
            session['username'] = user['username']
            print(f"Session's username is {session['username']}")
            return jsonify({
                "firstname": user['firstname'],
                "username": user['username']
            }), 200  # OK status
        else:
            return jsonify({"error": "Invalid username or password"}), 401  # Unauthorized
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Internal server error


@app.route('/api/signup', methods=['POST'])
def create_user():
    data = request.json
    print("Received signup data:", data)
    try:
        # Insert the user data into the 'users' collection
        result = db.users.insert_one({
            "username": data['username'],
            "password": data['password'],
            "firstname": data['firstname'],
            "lastname": data['lastname'],
            "email": data['email'],
            "phonenumber": data['phonenumber'],
            "address1": data['address1'],
            "address2": data['address2'],
        }) 
        print(result)
        # Return the created user data with the new user ID
        new_user = db.users.find_one({'_id': result.inserted_id})
        print(new_user)
        return jsonify({
            "firstname": new_user['firstname'],
            "username": new_user['username']

        }), 201  # Created status

    except Exception as e:
        print('failed:', str(e))  # Print the actual exception message
        return jsonify({"error": str(e)}), 500  # Internal server error


@app.route('/api/lastname', methods=['GET']) 
def get_user_lastname():
    username = request.args.get('username')
    print("Received username for lastname extraction: ", username)
    if not username:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        user = db.users.find_one({"username": username})  # Find the user by username
        if user:
            return jsonify({
                "lastname": user['lastname'],
            }), 200  # OK status
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Internal server error
    
    
@app.route('/api/events', methods=['GET'])
def get_user_logs():
    username = request.args.get('username')
    print("Received username for vents extraction: ", username)
    if not username:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        # Fetch events for the logged-in user
        events = db.logs.find({"username": username})  # Adjust the collection name as needed
        formatted_events = [
            {
                "id": str(event["_id"]),
                "title": f"Score: {event['score']}",
                "date": event['date'].isoformat(),  # Ensure this is in a valid date format
                "score": event["score"]
            }
            for event in events
        ]
        return jsonify(formatted_events), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Internal server error




app.run(debug=True)


