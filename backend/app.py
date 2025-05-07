from flask import Flask, jsonify
from flask_cors import CORS
from flask_login import LoginManager
import os
from dotenv import load_dotenv
from routes.auth import User

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=['http://localhost:3000'])

# Configure app
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-please-change-in-production')
app.config['JSON_SORT_KEYS'] = False

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Import routes after app initialization to avoid circular imports
from routes import auth, accounts, customers, invoices, reports

# Register blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(accounts.bp)
app.register_blueprint(customers.bp)
app.register_blueprint(invoices.bp)
app.register_blueprint(reports.bp)

@app.route('/api/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000) 