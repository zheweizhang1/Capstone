from flask import Flask, render_template, request, jsonify, session
from flask_pymongo import PyMongo
from flask_cors import CORS
import speech_recognition as sr
import os
from pydub import AudioSegment
import uuid
from openai import OpenAI
from transformers import pipeline, RobertaTokenizerFast, TFRobertaForSequenceClassification
from datetime import datetime


# Flask initialization
app = Flask(__name__)

# Database initialization
app.config["MONGO_URI"] = "mongodb://localhost:27017/my_app"
db = PyMongo(app).db
messages_collection = db['logs']  # Ensure this is the correct collection name


# ------------------------------------------------------------------------------------
# CORS is hella annoying. Better not touch these safeguards
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.secret_key = 'BAD_SEKRET_KEY'
CORS(app, 
     resources={r"/*": {
         "origins": "*",
         "supports_credentials": True,
         "allow_headers": ["Origin", "X-Requested-With", "Content-Type", "Accept"],
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
     }})
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = False
# ------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------
# This reads the string in API_KEY file for token. It's needed for ChatGPT to work
# Don't send ChatGPT big or many messages because it's not free
with open("API_KEY", "r") as file:
        api_key = file.read().strip()
client = OpenAI(api_key=api_key)
# ------------------------------------------------------------------------------------

# This initializes audio emotion recognition pipeline
emotion_recognition = pipeline("audio-classification", model="ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition")

# This initializes text emotion recognition pipeline
tokenizer = RobertaTokenizerFast.from_pretrained("arpanghoshal/EmoRoBERTa")
model = TFRobertaForSequenceClassification.from_pretrained("arpanghoshal/EmoRoBERTa")
emotion = pipeline('sentiment-analysis', 
                    model='arpanghoshal/EmoRoBERTa')




@app.route('/')
def sign_up():
    return render_template('index.html')

# ------------------------------------------------------------------------------------
# Login functionality
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
        return jsonify({"error": str(e)}), 500
# ------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------
# Signup functionality
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

        }), 201

    except Exception as e:
        print('failed:', str(e))
        return jsonify({"error": str(e)}), 500
# ------------------------------------------------------------------------------------


# Not needed
@app.route('/api/lastname', methods=['GET']) 
def get_user_lastname():
    username = request.args.get('username')
    print("Received username for lastname extraction: ", username)

    user = db.users.find_one({"username": username})  # Find the user by username
    if user:
        return jsonify({
            "lastname": user['lastname'],
        }), 200
    else:
        return jsonify({"message": f"No lastname found for user {username}"}), 500

# ------------------------------------------------------------------------------------
# Fetches logs from database for a specific user
@app.route('/api/events', methods=['GET'])
def get_user_logs():
    username = request.args.get('username')
    
    try:
        logs = list(db.logs.find({"username": username}))  # Convert cursor to list
        if not logs:
            return jsonify([]), 200

        formatted_logs = [
                {
                    "id": str(log["_id"]),
                    "title": f"Date: {strip_time_from_timestamp(log['timestamp'])}. Emotion: {log['emotion']}",
                    "date": strip_time_from_timestamp(log['timestamp']),

                }
                for log in logs
            ]
        return jsonify(formatted_logs), 200

    except Exception as e:
        return jsonify({"message": "Unexpected error duting fetching of calendar logs"}), 500
    
def strip_time_from_timestamp(date_value):
    return date_value.date().isoformat()
# ------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------
# Receives audio message from a user. Audio message gets transcribed
# If no error, audio message gets evaluated for its emotion
# Emotion is sent to ChatGPT to generate a response to continue the conversation going
# Returns ChatGPT response
@app.route('/api/handle_audio_message', methods=['POST']) 
def handle_audio_message():
    # Get info from form
    username = request.form['username']
    audio_file = request.files['audio']
    transcription = "" # for displaying audio related issues in case of error
    transcription_error_occured = False

    # Create recordings folder if it doesn't exist
    if not os.path.exists("recordings"):
        print("Creating recordings folder")
        os.makedirs("recordings")

    # Save audio_file to recordings
    audio_filename = os.path.join("recordings", f"audio_{uuid.uuid4()}.wav") 
    with open(audio_filename, "wb") as aud:
        aud_stream = audio_file.read()
        aud.write(aud_stream)

    print(f"Audio file saved. The filename is {audio_filename}")

    # Try statement below is for converting the file into wav format
    # We already specify to record file in wav format in react
    # but without code below, it breaks
    try:
        audio_segment = AudioSegment.from_file(audio_filename)
        audio_segment.export(audio_filename, format="wav")
    except Exception as e:
        transcription += "Error converting audio file into wav format.\n"
        transcription_error_occured = True

    # Check audio duration. If too short, discard as error
    audio_segment = AudioSegment.from_wav(audio_filename)
    if audio_segment.duration_seconds < 0.5:
        transcription += "The audio is too short or silent.\n"
        transcription_error_occured = True

    # Transcription happens here
    if not transcription:
        try:
            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_filename) as source:
                audio_data = recognizer.record(source)
                transcription = recognizer.recognize_google(audio_data)
                print("The text of transcribed audio file is: ", transcription)
        except sr.UnknownValueError:
            transcription = "Could not understand audio\n"
            transcription_error_occured = True
        except sr.RequestError:
            transcription = "Speech recognition service error\n"
            transcription_error_occured = True
        except Exception as e:
            transcription = "Unexpected error during transcription\n"
            transcription_error_occured = True

    if transcription_error_occured:
        return create_json_response("The audio message has been processed", transcription, "N/A", "N/A")

    # Emotion recognition
    emotion_list = emotion_recognition(audio_filename)
    detected_emotion = max(emotion_list, key=lambda x: x['score'])['label']  # Get the top emotion

    insert_emotion_verdict(username, detected_emotion, "audio")

    server_response = generate_chatgpt_response(transcription, detected_emotion)

    return create_json_response("The audio message has been processed", transcription, detected_emotion, server_response)
# ------------------------------------------------------------------------------------

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# Both handle_audio_message and handle_text_message uses functions in this X block
def insert_emotion_verdict(username, emotion_verdict, type):
    timestamp = datetime.now()
    db.logs.insert_one({
        "username": username,
        "emotion": emotion_verdict,
        "timestamp": timestamp,
        "type": type, # audio or text
    })
    print(f"Log inserted. User: {username} with emotion: {emotion_verdict} this day: {timestamp}")

def generate_chatgpt_response(user_message, detected_emotion):
    try:
        chat_completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
                {"role": "system", "content": f"""You are a emotional support. We detected that the user is feeling {detected_emotion}.
                                                Please respond shortly to continue the conversation going
                                                so that it would lead us to know user's emotional state"""},
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )
        chatgpt_response = chat_completion.choices[0].message.content
        print(f"ChatGPT respose is: {chatgpt_response}")

        return chatgpt_response
    
    except Exception as e:
        # Handle any other unexpected errors
        print("ChatGPT UNEXPECTED ERROR")
        return "An unexpected error occurred. Please try again"
    
def create_json_response(message, user_message, detected_emotion, server_response):
    return jsonify({
        "message": message,
        "user_message": user_message,
        "detected_emotion": detected_emotion,
        "response": server_response
    }), 200
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# ------------------------------------------------------------------------------------
# Receives text message from a user and evaluates its emotion
# Text message and emotion is sent to ChatGPT to generate a response to continue the conversation going
# Returns ChatGPT response
@app.route('/api/handle_text_message', methods=['POST']) 
def handle_text_message():
    # Get info from form
    username = request.form['username']
    user_message = request.form['message']

    emotion_list = emotion(user_message)
    detected_emotion = emotion_list[0]['label']
    
    insert_emotion_verdict(username, detected_emotion, "text")

    server_response = generate_chatgpt_response(user_message, detected_emotion)

    return create_json_response("The text message has been processed", user_message, detected_emotion, server_response)
# ------------------------------------------------------------------------------------



# ------------------------------------------------------------------------------------
# TO DO PIE CHART FETCH
@app.route('/api/get_emotion_counts_for_pie_chart', methods=['GET'])
def get_emotion_counts_for_pie_chart():
    username = request.args.get('username')
    print("Received username for pie chart extraction: ", username)

    try:
        logs = list(db.logs.find({"username": username}))
        if not logs:
            return jsonify([]), 200
        
        # Count occurrences of each emotion
        emotion_counts = {}
        for log in logs:
            emotion = log.get('emotion')
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # Format the response data
        formatted_emotions = [
            {
                "id": emotion,
                "label": emotion,
                "value": count,
                "color": get_color_for_emotion(emotion)  # Add a function to assign colors to emotions
            }
            for emotion, count in emotion_counts.items()
        ]
        return jsonify(formatted_emotions), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Internal server error

def get_color_for_emotion(emotion):
    """Assign a unique color to each emotion"""
    emotion_colors = {
        "neutral": "hsl(104, 70%, 50%)",
        "scary": "hsl(162, 70%, 50%)",
        "happy": "hsl(291, 70%, 50%)",
        "sad": "hsl(229, 70%, 50%)",
        "angry": "hsl(344, 70%, 50%)",
        "surprised": "hsl(344, 70%, 50%)",
        "Unknown": "hsl(0, 0%, 50%)",  # Default color for undefined emotions
    }
    return emotion_colors.get(emotion, "hsl(0, 0%, 50%)")  # Default color if no match
# ------------------------------------------------------------------------------------



# ------------------------------------------------------------------------------------
# Line Chart
@app.route('/api/get_messages_counts_for_line_chart', methods=['GET'])
def get_messages_counts_for_line_chart():
    username = request.args.get('username')

    pipeline = [
        {"$match": {"username": username}},
        {
            "$group": {
                "_id": {
                    "type": "$type",  # Message type (voice or text)
                    "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}}  # Only date part
                },
                "count": {"$sum": 1}  # Count messages
            }
        },
        {
            "$sort": {
                "_id.date": 1  # Sort by date ascending
            }
        }
    ]
    
    results = list(messages_collection.aggregate(pipeline))

    # Format the data as required by the line chart
    formatted_data = {
        "Total messages": [],
        "Audio messages": [],
        "Text messages": []
    }

    total_counts_per_date = {}

    for entry in results:
        date = entry["_id"]["date"]
        count = entry["count"]
        message_type = entry["_id"]["type"]

        # Add entries to the appropriate message type list
        if message_type == "audio":
            formatted_data["Audio messages"].append({"x": date, "y": count})

        elif message_type == "text":
            formatted_data["Text messages"].append({"x": date, "y": count})

        if date not in total_counts_per_date:
            total_counts_per_date[date] = 0
        total_counts_per_date[date] += count


    formatted_data["Total messages"] = [{"x": date, "y": total_counts_per_date[date]} for date in total_counts_per_date]

    # Construct the response data in the required format
    response_data = [
        {"id": "Total messages", "color": "hsl(220, 70%, 50%)", "data": formatted_data["Total messages"]},
        {"id": "Audio messages", "color": "hsl(162, 70%, 50%)", "data": formatted_data["Audio messages"]},
        {"id": "Text messages", "color": "hsl(291, 70%, 50%)", "data": formatted_data["Text messages"]}
    ]
    return jsonify(response_data)
# ------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------
# For line chart in Dashboard
@app.route('/api/get_total_messages', methods=['GET'])
def get_total_messages():
    # Get the username from query parameters (or from request headers/body if needed)
    username = request.args.get('username')

    # Query MongoDB for messages related to this specific user
    total_messages = messages_collection.count_documents({"username": username})

    print(f"Total messages for user {username} is {total_messages}")
    return jsonify({"totalMessages": total_messages}), 200
# ------------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(port=5000, debug=True)

