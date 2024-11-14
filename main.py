from flask import Flask, redirect, url_for, render_template, request, jsonify, session, make_response
from flask_pymongo import PyMongo
from bson import ObjectId
from flask_cors import CORS,cross_origin
from werkzeug.utils import secure_filename
import speech_recognition as sr
import os
from pydub import AudioSegment
import uuid
from openai import OpenAI
from transformers import pipeline, RobertaTokenizerFast, TFRobertaForSequenceClassification
from datetime import datetime

emotion_recognition = pipeline("audio-classification", model="ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition")

'''
from transformers import AutoProcessor, AutoModelForAudioClassification

pipe = pipeline("audio-classification", model="ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition")
processor = AutoProcessor.from_pretrained("ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition")
model = AutoModelForAudioClassification.from_pretrained("ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition")
'''

tokenizer = RobertaTokenizerFast.from_pretrained("arpanghoshal/EmoRoBERTa")
model = TFRobertaForSequenceClassification.from_pretrained("arpanghoshal/EmoRoBERTa")
emotion = pipeline('sentiment-analysis', 
                    model='arpanghoshal/EmoRoBERTa')

with open("API_KEY", "r") as file:
        api_key = file.read().strip()
client = OpenAI(api_key=api_key)




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
         "origins": "*",  # Change this to your frontend's origin
         "supports_credentials": True,  # Allow credentials to be sent
         "allow_headers": ["Origin", "X-Requested-With", "Content-Type", "Accept"],
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
     }})
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True if using HTTPS in production

'''
CORS(app,
     resources={r"/*": {
         "origins": ["http://localhost:3000"],
         "supports_credentials": True
     }},
     supports_credentials=True)
'''



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
            }), 200
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
'''
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
    try:
        # Attempt transcription
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_filename) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            print("Transcribed text:", text)  # Debugging line
    except sr.UnknownValueError:
        text = "Could not understand audio"
    except sr.RequestError:
        text = "Speech recognition service error"
    except Exception as e:
        print(f"Unexpected error during transcription: {e}")
        text = "Unexpected error during transcription"

    # Prepare response
    response = jsonify({
        "message": "Audio uploaded successfully",
        "transcription": text,
        "username": username
    })
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return response, 200
'''

# AUDIO RECEIVE
@app.route('/api/upload_audio', methods=['POST']) 
def upload_audio():
    if 'audio' not in request.files or 'username' not in request.form:
        return jsonify({"error": "Audio file or username missing"}), 400

    audio_file = request.files['audio']
    username = request.form['username']  # Get the username from the form data

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
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_filename) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            print("Transcribed text:", text)
    except sr.UnknownValueError:
        text = "Could not understand audio"
    except sr.RequestError:
        text = "Speech recognition service error"
    except Exception as e:
        print(f"Unexpected error during transcription: {e}")
        text = "Unexpected error during transcription"

    # Emotion recognition
    emotion_results = emotion_recognition(audio_filename)
    print(emotion_results)
    emotion = max(emotion_results, key=lambda x: x['score'])['label']  # Get the top emotion by score
    print("Detected emotion:", emotion)

    # Prepare response
    response = jsonify({
        "message": "Audio uploaded successfully",
        "transcription": text,
        "emotion": emotion,
        "username": username
    })
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return response, 200





import openai

@app.route('/api/handle_message', methods=['POST']) 
def handle_message():
    global emotion
    if 'message' not in request.form or 'username' not in request.form:
        return jsonify({"error": "Message or username missing"}), 400
    
    user_message = request.form['message']
    username = request.form['username']
    print(user_message)

    
    
    emotion_label = emotion(user_message)
    emotion_detected = emotion_label[0]['label']
    print(f"Trying CHATGPT. The emotion is {emotion_detected}")
    
    insert = db.logs.insert_one({
        "username": username,
        "user_message": user_message,
        "emotion": emotion_detected,
        "dateANDtime": datetime.now()
    })
    print(insert)

    try:
        chat_completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
                {"role": "system", "content": f"""You are a emotional support. We detected that the user is feeling {emotion_detected}.
                                                Please respond shortly to continue the conversation going
                                                so that it would lead us to know user's emotional state"""},
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )
        chatgpt_response = chat_completion.choices[0].message.content
        print(chatgpt_response)

        response = jsonify({
            "message": "Message processed successfully",
            "response": chatgpt_response,
            "username": username
        })
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        return response, 200

    except Exception as e:
        # Handle any other unexpected errors
        print("Unexpected error during ChatGPT API call:", str(e))
        return jsonify({"error": "An unexpected error occurred. Please try again."}), 500

# TO DO PIE CHART FETCH
'''
@app.route('/api/fetchPieChartData', methods=['GET'])
def fetchPieChartData():
    username = request.args.get('username')
    print("Received username for pie chart extraction: ", username)
    if not username:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        user_log = db.logs.find({"username": username}) # Convert cursor to list
        if not user_log:
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
'''   


if __name__ == '__main__':
    app.run(port=5000, debug=True)

