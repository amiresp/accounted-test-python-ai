from flask import Flask, jsonify
from flask_cors import CORS
from flask_login import LoginManager
import os
from dotenv import load_dotenv
from routes.auth import User, auth_bp
from routes.accounts import accounts_bp
from routes.customers import customers_bp
from routes.invoices import invoices_bp
from routes.reports import reports_bp
from routes.data import data_bp

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Session configuration
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY', 'dev-key-please-change-in-production'),
    SESSION_COOKIE_SECURE=False,  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_PATH='/',
    PERMANENT_SESSION_LIFETIME=2592000,  # 30 days
    SESSION_REFRESH_EACH_REQUEST=True,
    SESSION_TYPE='filesystem'
)

# Configure CORS with more specific settings
CORS(app, 
     resources={r"/api/*": {
         "origins": ["http://localhost:3000"],
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization"],
         "expose_headers": ["Content-Type"],
         "supports_credentials": True,
         "max_age": 3600
     }},
     supports_credentials=True)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = None  # Disable default login view
login_manager.session_protection = 'strong'

@login_manager.user_loader
def load_user(user_id):
    print(f"Loading user with ID: {user_id}")
    user = User.get(user_id)
    print(f"Loaded user: {user.username if user else 'None'}")
    return user

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(accounts_bp)
app.register_blueprint(customers_bp)
app.register_blueprint(invoices_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(data_bp)

@app.route('/api/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000) 