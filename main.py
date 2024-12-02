from flask import Flask, render_template, request, jsonify, session
from flask_pymongo import PyMongo
from flask_cors import CORS
import speech_recognition as sr
import os
from pydub import AudioSegment
import uuid
from openai import OpenAI
from transformers import pipeline, RobertaTokenizerFast, TFRobertaForSequenceClassification
from datetime import datetime, timezone, timedelta
from pytz import timezone
from collections import Counter



# Flask initialization
app = Flask(__name__)

# Database initialization
app.config["MONGO_URI"] = "mongodb://localhost:27017/my_app"
db = PyMongo(app).db
messages_collection = db['logs']  # Ensure this is the correct collection name


# ------------------------------------------------------------------------------------
# CORS is hella annoying. Better not touch these safeguards
app.secret_key = 'BAD_SEKRET_KEY'
CORS(app, 
     resources={r"/*": {
         "origins": "*",
         "supports_credentials": True,
         "allow_headers": ["Origin", "X-Requested-With", "Content-Type", "Accept"],
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
     }})
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True
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
    print()
    print("Received login data:", data)
    try:
        user = db.users.find_one({"username": data['username'], "password": data['password']})
        if user:
            session.clear()
            session['username'] = user['username']

            print(f"\n\n\n{session}\n\n\n")
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
        
        session.clear()
        session['username'] = data['username']
        print(new_user)
        return jsonify({
            "firstname": new_user['firstname'],
            "username": new_user['username']

        }), 201

    except Exception as e:
        print('failed:', str(e))
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/logout_endpoint', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200

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
@app.route('/api/events_endpoint', methods=['GET'])
def get_user_logs_endpoint():
    if 'user_logs' not in session:
        session['user_logs'] = get_user_logs()
    return jsonify(session.get('user_logs'))

def get_user_logs():
    username = session.get('username')
    logs = list(db.logs.find({"username": username}))  # Convert cursor to list
    if not logs:
        return []

    # Group emotions by date
    emotions_by_date = {}
    for log in logs:
        log_date = strip_time_from_timestamp(log['timestamp'])
        emotion = log['emotion'].lower()
        if log_date not in emotions_by_date:
            emotions_by_date[log_date] = []
        emotions_by_date[log_date].append(emotion)

    # Find the most common emotion for each day
    most_common_emotions = []
    for log_date, emotions in emotions_by_date.items():
        most_common_emotion = Counter(emotions).most_common(1)[0][0]  # Get the emotion with the highest count
        most_common_emotions.append({
            "date": log_date,
            "emotion": most_common_emotion.title(),
            "color": emotion_colors.get(most_common_emotion, "hsl(0, 0%, 50%)")  # Default is 0 0 50% if no match
        })

    # Format the logs for calendar events
    formatted_logs = [
        {
            "title": f"{log['emotion']}",
            "date": log['date'],
            "color": log["color"]
        }
        for index, log in enumerate(most_common_emotions)
    ]
    return formatted_logs

    
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

    ''' 
    EMOTION TYPES IF DETERMINED BY AUDIO:
        'angry', 'calm', 'disgust', 'fearful', 'happy', 'neutral', 'sad', 'surprised'
    '''

    assistant_response = generate_chatgpt_response(transcription, detected_emotion)
    
    insert_emotion(username, detected_emotion, transcription, "audio", assistant_response)

    user_message = transcription
    
    update_session(user_message, assistant_response, detected_emotion)

    return create_json_response("The audio message has been processed", detected_emotion, user_message, assistant_response)
# ------------------------------------------------------------------------------------

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# Both handle_audio_message and handle_text_message uses functions in this X block
def insert_emotion(username, emotion_verdict, user_message, type, assistant_response):
    timestamp = datetime.now()
    db.logs.insert_one({
        "username": username,
        "emotion": emotion_verdict,
        "user_message": user_message,
        "timestamp": timestamp,
        "type": type, # audio or text
        "assistant_response": assistant_response,
    })
    print(f"Log inserted. User: {username} with emotion: {emotion_verdict} this day: {timestamp}")

def generate_chatgpt_response(new_user_message, detected_emotion):
    how_far_to_remember = 5 # ChatGPT will remember last N messages
    
    user_messages = session.get('todays_messages')
    last_N_messages = user_messages[-how_far_to_remember:]
    
    messages = [
            {"role": "system", "content": f"""You are an emotional support assistant designed to monitor and support the user's emotional well-being.
    The user is currently feeling {detected_emotion}. Your goal is to provide empathetic, supportive, and relevant responses that help the user navigate their emotions.
    Ensure that all responses are centered around emotional health, mental well-being, and related topics.
    Do **NOT** engage in conversations unrelated to emotional support or health monitoring. 
    All conversations are logged and monitored for emotional analysis, so please stay on-topic and avoid straying into irrelevant or non-pertinent subjects. 
    If the user begins to discuss topics that don't pertain to their emotions or well-being, gently guide them back to the conversation about their feelings or emotional state."""}
    ]
    
    for message in last_N_messages:
            # User message
            messages.append({"role": "user", "content": message['user_message']})
            # Assistant response
            messages.append({"role": "assistant", "content": message['assistant_response']})
    
    # Add the newesest user message
    messages.append({"role": "user", "content": new_user_message})
    
    print(messages)
    try:
        chat_completion = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
        chatgpt_response = chat_completion.choices[0].message.content
        print(f"ChatGPT respose is: {chatgpt_response}")

        return chatgpt_response
    
    except Exception as e:
        print("ChatGPT UNEXPECTED ERROR")
        return "An unexpected error occurred. Please try again"
    
def create_json_response(message, detected_emotion, user_message, assistant_response):
    return jsonify({
        "message": message,
        "detected_emotion": detected_emotion,
        "user_message": user_message,
        "assistant_response": assistant_response
    }), 200
    
def update_session(user_message, assistant_response, detected_emotion):
    print(f"CALLED UPDATE SESSION \n\n\n{session}\n\n\n")
    new_message = {
        'user_message': user_message,
        'assistant_response': assistant_response,
        'detected_emotion': detected_emotion,
    }
    session['todays_messages'].append(new_message)
    session.modified = True # Save session
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

    ''' 
    EMOTION TYPES IF DETERMINED BY TEXT:
        admiration, amusement, anger, annoyance, approval, caring, confusion,
        curiosity, desire, disappointment, disapproval, disgust, embarrassment,
        excitement, fear, gratitude, grief, joy, love, nervousness, optimism,
        pride,realization, relief, remorse, sadness, surprise + neutral
    '''
    

    assistant_response = generate_chatgpt_response(user_message, detected_emotion)
    
    insert_emotion(username, detected_emotion, user_message, "text", assistant_response)

    update_session(user_message, assistant_response, detected_emotion)
    
    return create_json_response("The text message has been processed", detected_emotion, user_message, assistant_response)
# ------------------------------------------------------------------------------------



# ------------------------------------------------------------------------------------
# PIE CHART FETCH
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
                "color": emotion_colors.get(emotion, "hsl(0, 0%, 50%)")  # Default is 0 0 50% if no match
            }
            for emotion, count in emotion_counts.items()
        ]
        return jsonify(formatted_emotions), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Internal server error

# Dictionary
emotion_colors = {
    "angry": "hsl(344, 70%, 50%)",        # Red
    "calm": "hsl(200, 70%, 50%)",         # Blue
    "disgust": "hsl(120, 70%, 50%)",      # Green
    "fearful": "hsl(0, 70%, 50%)",        # Dark red
    "happy": "hsl(291, 70%, 50%)",        # Pink
    "neutral": "hsl(104, 70%, 50%)",      # Neutral green
    "sad": "hsl(229, 70%, 50%)",          # Blue
    "surprised": "hsl(344, 70%, 50%)",    # Red
    "admiration": "hsl(200, 70%, 50%)",   # Light blue
    "amusement": "hsl(40, 70%, 50%)",     # Yellow
    "anger": "hsl(344, 70%, 50%)",        # Red
    "annoyance": "hsl(30, 70%, 50%)",     # Orange
    "approval": "hsl(120, 70%, 50%)",     # Green
    "caring": "hsl(150, 70%, 50%)",       # Light green
    "confusion": "hsl(240, 70%, 50%)",    # Purple
    "curiosity": "hsl(60, 70%, 50%)",     # Yellow
    "desire": "hsl(340, 70%, 50%)",       # Deep red
    "disappointment": "hsl(200, 70%, 50%)", # Blue
    "disapproval": "hsl(0, 70%, 50%)",    # Dark red
    "embarrassment": "hsl(350, 70%, 50%)", # Light red
    "excitement": "hsl(50, 70%, 50%)",    # Bright yellow
    "fear": "hsl(0, 70%, 50%)",           # Dark red
    "gratitude": "hsl(90, 70%, 50%)",     # Light green
    "grief": "hsl(230, 70%, 50%)",        # Dark blue
    "joy": "hsl(35, 70%, 50%)",           # Orange-yellow
    "love": "hsl(330, 70%, 50%)",         # Red
    "nervousness": "hsl(190, 70%, 50%)",  # Light blue
    "optimism": "hsl(60, 70%, 50%)",      # Yellow
    "pride": "hsl(300, 70%, 50%)",        # Purple
    "realization": "hsl(180, 70%, 50%)",  # Teal
    "relief": "hsl(160, 70%, 50%)",       # Light green
    "remorse": "hsl(280, 70%, 50%)",      # Purple
    "sadness": "hsl(230, 70%, 50%)",      # Dark blue
    "surprise": "hsl(344, 70%, 50%)",     # Red
}
# ------------------------------------------------------------------------------------



# ------------------------------------------------------------------------------------
# Line Chart
@app.route('/api/get_messages_counts_for_line_chart', methods=['GET'])
def get_messages_counts_for_line_chart():
    # username = request.args.get('username')
    
    # TO DO: CHANGE EVERY INFO REQUEST TO SESSION GET
    username = session.get('username')

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

# ------------------------------------------------------------------------------------
# For lasting messages
@app.route('/api/get_todays_messages', methods=['GET'])
def get_todays_messages():
    if 'todays_messages' in session:
        return session['todays_messages']
    
    tz = timezone('EST')
    now = datetime.now(tz)
    start_of_day = datetime(now.year, now.month, now.day)

    todays_messages = get_user_messages_in_time_range(
            start_of_day,
            now,
            fields=["user_message", "assistant_response"]
        )
    session['todays_messages'] = todays_messages
    return jsonify(session.get('todays_messages'))


# Getting user messages within a specific time range
def get_user_messages_in_time_range(start_date, end_date, fields=None):
    """
        fields (list): Needs to be specified to get database field that is needed like fields=["user_message", "assistant_response"]
    """
    username = session.get('username')
    if not username:
        return []

    print("Building a query")
    query = {
        "username": username,
        "timestamp": {"$gte": start_date, "$lt": end_date}
    }
    print(f"The query is {query}")
    print("Building a projection")

    projection = {"_id": 0}  # Do not include _id. NOT NEEDED
    if fields:
        for field in fields:
            projection[field] = 1
    print(f"The projection is {projection}")
    
    cursor = messages_collection.find(query, projection).sort("timestamp", 1)
    cursor_results = list(cursor)
    print(f"The query and projection return {cursor_results}")
    return cursor_results
# ------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------
# For analytics like most common emotion last 30 days, 7 days, today 
@app.route('/api/get_analytics', methods=['GET'])
def get_user_analytics():
    scope = request.args.get('days', 1)  # Default is 1 day
    print("The SCOPE IS ", scope)
    scope = int(scope)
    print("The SCOPE IS ", scope)

    tz = timezone('EST')
    now = datetime.now(tz)

    if scope == 1:
        start_date = datetime(now.year, now.month, now.day)
    elif scope == 7:
        start_date = now - timedelta(days=7)
    elif scope == 30:
        start_date = now - timedelta(days=30)
    else:
        return jsonify({"error": "Invalid scope"}), 400

    print(f"Start date: {start_date} and end date: {now}")
    messages = get_user_messages_in_time_range(start_date, now, fields=["emotion"])
    print(f"Messages are: {messages}")

    most_common_emotion = get_most_common_emotion(messages)
    print(f"Most_common_emotion are: {messages}")

    print(f"For scope {scope} the most common emotion is {most_common_emotion}")
    return jsonify({
        "most_common_emotion": most_common_emotion,
    })

def get_most_common_emotion(messages):
    emotions = [message.get('emotion') for message in messages if 'emotion' in message]
    print(f"All emotions {emotions}")
    if emotions:
        most_common = Counter(emotions).most_common(1)
        return most_common[0][0] if most_common else None
    return None
# ------------------------------------------------------------------------------------

    
if __name__ == '__main__':
    app.run(port=5000, debug=True)