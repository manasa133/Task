# app.py
from flask import Flask
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required,  get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from textblob import TextBlob
from flask_cors import CORS



app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

app.config['MONGO_URI'] = 'mongodb+srv://manasa:466C1c8q9pFnkb8g@cluster0.jv1lemt.mongodb.net/users?retryWrites=true&w=majority&appName=Cluster0'
mongo = PyMongo(app)
try:
    mongo = PyMongo(app)
    print("Successfully connected to MongoDB")
except Exception as e:
    print("Failed to connect to MongoDB", e)
    mongo = None




app.config['JWT_SECRET_KEY'] = 'your_secret_key'
jwt = JWTManager(app)


@app.route('/register', methods=['POST'])
def register():
    user_data = request.json
    if not user_data or not 'username' in user_data or not 'password' in user_data:
        return jsonify({'error': 'Invalid data'}), 400

    existing_user = mongo.db.users.find_one({'username': user_data['username']})
    if existing_user:
        return jsonify({'error': 'User already exists'}), 400

    hashed_password = generate_password_hash(user_data['password'])
    new_user = {
        'username': user_data['username'],
        'email': user_data.get('email', ''),
        'password': hashed_password
    }
    mongo.db.users.insert_one(new_user)
    return jsonify({'message': 'User registered successfully'}), 201




# app.py
@app.route('/login', methods=['POST'])
def login():
    if mongo is None:
        return jsonify({'error': 'Database connection failed'}), 500

    login_data = request.json
    if not login_data or not 'username' in login_data or not 'password' in login_data:
        return jsonify({'error': 'Invalid data'}), 400

    user = mongo.db.users.find_one({'username': login_data['username']})
    if not user or not check_password_hash(user['password'], login_data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401

    access_token = create_access_token(identity=login_data['username'])
    return jsonify({'access_token': access_token}), 200
    


@app.route('/profile', methods=['GET', 'PUT'])
@jwt_required()
def profile():
    if mongo is None:
        return jsonify({'error': 'Database connection failed'}), 500

    current_user = get_jwt_identity()
    user = mongo.db.users.find_one({'username': current_user})

    if request.method == 'GET':
        if user:
            user_data = {
                'username': user['username'],
                'email': user['email']
            }
            return jsonify(user_data), 200
        else:
            return jsonify({'error': 'User not found'}), 404

    if request.method == 'PUT':
        updated_data = request.json
        mongo.db.users.update_one({'username': current_user}, {'$set': updated_data})
        return jsonify({'message': 'User profile updated successfully'}), 200

@app.route('/analyze', methods=['POST'])
def analyze():
    text_data = request.json
    if not text_data or not 'text' in text_data:
        return jsonify({'error': 'Invalid data'}), 400

    text = text_data['text']
    analysis = TextBlob(text)
    sentiment = {
        'polarity': analysis.sentiment.polarity,
        'subjectivity': analysis.sentiment.subjectivity
    }

    return jsonify(sentiment), 200


if __name__ == '__main__':
    app.run(debug=True)