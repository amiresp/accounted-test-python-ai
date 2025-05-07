from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
import json
import os

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# In a real application, this would be in a database
USERS_FILE = 'data/users.json'

class User(UserMixin):
    def __init__(self, username, password_hash, role):
        self.id = username
        self.password_hash = password_hash
        self.role = role

    @staticmethod
    def get(user_id):
        if not os.path.exists(USERS_FILE):
            return None
        
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
            if user_id in users:
                user_data = users[user_id]
                return User(
                    username=user_id,
                    password_hash=user_data['password'],
                    role=user_data['role']
                )
        return None

def ensure_users_file():
    os.makedirs('data', exist_ok=True)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({
                'admin': {
                    'password': generate_password_hash('admin123'),
                    'role': 'admin'
                }
            }, f)

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    ensure_users_file()
    
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)

    if username not in users or not check_password_hash(users[username]['password'], password):
        return jsonify({'error': 'Invalid username or password'}), 401

    user = User.get(username)
    login_user(user)
    return jsonify({'message': 'Logged in successfully'}), 200

@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

@bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    return jsonify({
        'username': current_user.id,
        'role': current_user.role
    }), 200 