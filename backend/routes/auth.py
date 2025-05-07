from flask import Blueprint, jsonify, request, session
from flask_login import login_user, logout_user, login_required, current_user, UserMixin
import json
import os
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Get the absolute path to the data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')

def ensure_users_file():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump([{
                'id': '1',
                'username': 'admin',
                'password': 'admin123'
            }], f, ensure_ascii=False)

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def get_id(self):
        return str(self.id)

    @staticmethod
    def get(user_id):
        try:
            ensure_users_file()
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                users = json.load(f)
                user_data = next((u for u in users if str(u['id']) == str(user_id)), None)
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
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                users = json.load(f)
                user_data = next((u for u in users if u['username'] == username), None)
                if user_data:
                    return User(user_data['id'], user_data['username'], user_data['password'])
        except Exception as e:
            print(f"Error in get_by_username: {str(e)}")
            return None
        return None

@auth_bp.route('/test-users', methods=['GET'])
def test_users():
    try:
        ensure_users_file()
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
            return jsonify(users)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return jsonify({'error': 'Please use POST method for login'}), 405
        
    try:
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Missing username or password'}), 400

        username = data['username']
        password = data['password']

        user = User.get_by_username(username)
        if user and user.password == password:
            print(f"Logging in user: {user.username}")
            login_user(user, remember=True)
            session.permanent = True
            print(f"Session after login: {dict(session)}")
            return jsonify({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username
                }
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@auth_bp.route('/logout')
@login_required
def logout():
    print(f"Logging out user: {current_user.username if current_user else 'None'}")
    logout_user()
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/current-user')
@login_required
def get_current_user():
    print(f"Current user check - Session: {dict(session)}")
    print(f"Current user check - User: {current_user.username if current_user else 'None'}")
    print(f"Current user check - Is authenticated: {current_user.is_authenticated if current_user else False}")
    
    if not current_user.is_authenticated:
        return jsonify({'error': 'Not authenticated'}), 401
        
    return jsonify({
        'id': current_user.id,
        'username': current_user.username
    }), 200 