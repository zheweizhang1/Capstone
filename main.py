from flask import Flask, redirect, url_for, render_template, request, jsonify, session
from flask_pymongo import PyMongo
from bson import ObjectId
from flask_cors import CORS,cross_origin
from werkzeug.utils import secure_filename
import speech_recognition as sr
import os
from pydub import AudioSegment
import uuid



app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/my_app"
db = PyMongo(app).db
'''
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'None'

CORS(app, origins="http://localhost:3000", supports_credentials=True)  # Allow only localhost:3000 to access

'''
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.secret_key = 'BAD_SEKRET_KEY'

CORS(app, 
     resources={r"/*": {
         "origins": "http://localhost:3000",  # Change this to your frontend's origin
         "supports_credentials": True,  # Allow credentials to be sent
         "allow_headers": ["Origin", "X-Requested-With", "Content-Type", "Accept"],
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
     }})


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
    
# CALENDAR
@app.route('/api/events', methods=['GET'])
def get_user_logs():
    username = request.args.get('username')
    print("Received username for vents extraction: ", username)
    if not username:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Fetch events for the logged-in user
        events = db.logs.find({"username": username}) # Convert cursor to list
        #events = db.logs.find({"username": username})  # Adjust the collection name as needed
        if not events:
            return jsonify([]), 200
        
        formatted_events = [
                {
                    "id": str(event["_id"]),
                    "title": f"Score: {event['score']}",
                    "date": event['date'],
                    "score": event["score"]
                }
                for event in events
            ]
        return jsonify(formatted_events), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Internal server error

# AUDIO RECEIVE
@app.route('/api/upload_audio', methods=['POST']) 
def upload_audio():
    if 'audio' not in request.files or 'username' not in request.form:
        return jsonify({"error": "Audio file or username missing"}), 400

    audio_file = request.files['audio']
    username = request.form['username']  # Get the username from the form data

    # Add your logic to handle the audio file and transcription here


    audio_filename = os.path.join("recordings", f"audio_{uuid.uuid4()}.wav") 
    with open(audio_filename, "wb") as aud:
        aud_stream = audio_file.read()
        aud.write(aud_stream)

    print(f"Saved audio file size: {os.path.getsize(audio_filename)} bytes")

    # Optional: Convert to WAV format if necessary
    
    try:
        audio_segment = AudioSegment.from_file(audio_filename)
        audio_segment.export(audio_filename, format="wav")
    except Exception as e:
        print(f"Error converting audio file: {e}")

    # Check audio duration before transcription
    audio_segment = AudioSegment.from_wav(audio_filename)
    if audio_segment.duration_seconds < 0.5:  # Threshold for silence or very short audio
        return jsonify({"error": "Audio too short or silent"}), 400

# Transcription logic
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_filename) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            print(text)
            return jsonify({"message": "Audio uploaded successfully", "transcription": text, "username": username}), 200
        except sr.UnknownValueError:
            return jsonify({"error": "Could not understand audio"}), 400
        except sr.RequestError:
            return jsonify({"error": "Speech recognition service error"}), 500
        except Exception as e:
            print(f"Unexpected error during transcription: {e}")
        return jsonify({"error": "Unexpected error during transcription"}), 500
        
@app.route('/api/handle_message', methods=['POST']) 
def handle_message():
    if 'message' not in request.form or 'username' not in request.form:
        return jsonify({"error": "Message or username missing"}), 400
    
    message = request.form['message']
    username = request.form['username']
    print(message)
    return jsonify({"message": "Message sent successfully", "text": message, "username": username}), 200
    
            
'''        
@app.route('/audiorecog', methods = ['GET', 'POST'])
def audiorecog():
   if request.method == 'POST':
      print("Recieved Audio File")
      file = request.files['file']
      recognizer = sr.Recognizer()
      with sr.AudioFile(temp_path) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)

            # Insert into database (example placeholder)
            # db.collection.insert_one({"username": username, "transcription": text})

            return jsonify({"transcription": text, "username": username})
        except sr.UnknownValueError:
            return jsonify({"error": "Could not understand audio"}), 400
        except sr.RequestError:
            return jsonify({"error": "Speech recognition service error"}), 500
'''

if __name__ == '__main__':
    app.run(debug=True, port=5000)

