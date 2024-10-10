from flask import Flask, redirect, url_for, render_template, request, jsonify, session
from flask_pymongo import PyMongo
from bson import ObjectId

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/my_app"
app.secret_key = 'secret_key'
db = PyMongo(app).db

@app.route('/')
def sign_up():
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    print(f'Received username is {username}\nReceived password is {password}')
    # Query
    user = db.users.find_one({'username': username, 'password': password})
    
    if user is None:
        print('User not found')
        return jsonify({"message": "User not found"}), 404
    
    session['user_id'] = str(user['_id'])
    print(f"User's object id is {session.get('user_id')}")
    return jsonify({"message": "Login successful", "is_enter_dashboard": True}), 200


@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    
    fullname = data.get('fullname')
    username = data.get('username')
    password = data.get('password')
    print(f'Received fullname is {fullname}\nReceived username is {username}\nReceived password is {password}')
    # Insert
    
    try:
        user = db.users.insert_one({ 'fullname': fullname, 'username': username, 'password': password })
    except:
        print('User not inserted')
        return jsonify({"message": "User not inserted"}), 404
    
    session['user_id'] = str(user.inserted_id)
    print(f"User's object id is {session.get('user_id')}")
    return jsonify({"message": "Sign Up successful", "is_enter_dashboard": True}), 200


@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    print('Entering the dashboard')
    if not user_id:
        return redirect(url_for('login'))
    
    user = db.users.find_one({'_id': ObjectId(user_id)})  # Ensure ObjectId is used

    if user is None:
        return "User not found", 404  # Handle case where user is not found
    
    return render_template('dashboard.html', fullname = user['fullname'], username = user['username'])




'''
@app.route('/login', methods = ['POST'])
def login():
    if request.method == "POST":
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')

        #username = request.form['username']
        #password = request.form['password']

        user = db.users.find_one({'username': username, 'password': password})
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user_id = str(user.inserted_id)
        return redirect(url_for('enter', entered = 'True', object_id = user_id))


@app.route('/enter')
def enter():
    entered = request.args.get('entered', 'False')
    print(f'Success {entered}')

'''

#---

'''
@app.route('/submit', methods = ['POST', 'GET'])
def submit():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
    user = db.users.insert_one({ 'name': name, 'username': username, 'password': password })
    user_id = str(user.inserted_id)
    ###

    return redirect(url_for('enter', entered = 'True', oid = user_id))

@app.route('/enter')
def enter():
    entered = request.args.get('entered', 'False')
    oid = request.args.get('oid', '')
    if oid:
        user = db.users.find_one({'_id': ObjectId(oid)})

    if entered.lower() == 'true':
        res = 'welcome'
    else:
        res = 'not welcome.'
    return render_template('enter.html', result = res, objectid = oid, username = user['username'], password = user['password'])
'''



app.run(debug=True)


