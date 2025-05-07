from flask import Blueprint, jsonify, request, session
from flask_login import login_user, logout_user, login_required, current_user, UserMixin
import json
import os
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

# Get the absolute path to the data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')

def ensure_users_file():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump([{
                "id": "1",
                "username": "admin",
                "password": "admin123"
            }], f, indent=2)

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    @staticmethod
    def get(user_id):
        try:
            ensure_users_file()
            with open(USERS_FILE, 'r') as f:
                users = json.load(f)
                user_data = next((u for u in users if u['id'] == user_id), None)
                if user_data:
                    return User(user_data['id'], user_data['username'], user_data['password'])
        except Exception as e:
            print(f"Error in get user: {str(e)}")
            return None
        return None

    @staticmethod
    def get_by_username(username):
        try:
            ensure_users_file()
            with open(USERS_FILE, 'r') as f:
                users = json.load(f)
                print(f"Looking for user {username} in users: {users}")
                user_data = next((u for u in users if u['username'] == username), None)
                if user_data:
                    print(f"Found user data: {user_data}")
                    return User(user_data['id'], user_data['username'], user_data['password'])
                print(f"No user found with username: {username}")
        except Exception as e:
            print(f"Error in get_by_username: {str(e)}")
            return None
        return None

@auth_bp.route('/api/auth/test-users', methods=['GET'])
def test_users():
    try:
        ensure_users_file()
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
            return jsonify(users)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    try:
        print("Login route called")
        print(f"Request headers: {dict(request.headers)}")
        print(f"Request data: {request.get_data()}")
        
        data = request.get_json()
        print(f"Parsed JSON data: {data}")
        
        username = data.get('username')
        password = data.get('password')

        print(f"Username: {username}")
        print(f"Password: {password}")

        if not username or not password:
            print("Missing username or password")
            return jsonify({'error': 'Username and password are required'}), 400

        user = User.get_by_username(username)
        print(f"User object: {user.__dict__ if user else None}")
        
        if user and user.password == password:  # In production, use proper password hashing
            print("Password match successful")
            login_user(user)
            print("Login successful")
            return jsonify({
                'id': user.id,
                'username': user.username
            })
        
        print("Invalid credentials")
        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        print(f"Error in login route: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'})

@auth_bp.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user():
    return jsonify({
        'id': current_user.id,
        'username': current_user.username
    }) 