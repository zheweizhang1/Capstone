from flask import Flask, redirect, url_for, render_template, request
from flask_pymongo import PyMongo
from bson import ObjectId

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/health_app_db"
db = PyMongo(app).db

@app.route('/')
def sign_up():
    return render_template('index.html')

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




app.run(debug=True)


