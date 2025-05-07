from flask import Blueprint, request, jsonify
from flask_login import login_required
import json
import os

bp = Blueprint('accounts', __name__, url_prefix='/api/accounts')

ACCOUNTS_FILE = 'data/accounts.json'

def ensure_accounts_file():
    os.makedirs('data', exist_ok=True)
    if not os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, 'w') as f:
            json.dump([], f)

@bp.route('/', methods=['GET'])
@login_required
def get_accounts():
    ensure_accounts_file()
    with open(ACCOUNTS_FILE, 'r') as f:
        accounts = json.load(f)
    return jsonify(accounts), 200

@bp.route('/', methods=['POST'])
@login_required
def create_account():
    data = request.get_json()
    required_fields = ['name', 'type', 'number']
    
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    ensure_accounts_file()
    
    with open(ACCOUNTS_FILE, 'r') as f:
        accounts = json.load(f)

    # Generate a simple ID (in a real app, use UUID)
    account_id = str(len(accounts) + 1)
    
    new_account = {
        'id': account_id,
        'name': data['name'],
        'type': data['type'],
        'number': data['number'],
        'zone': data.get('zone', '')
    }
    
    accounts.append(new_account)
    
    with open(ACCOUNTS_FILE, 'w') as f:
        json.dump(accounts, f, indent=2)
    
    return jsonify(new_account), 201

@bp.route('/<account_id>', methods=['PUT'])
@login_required
def update_account(account_id):
    data = request.get_json()
    
    ensure_accounts_file()
    
    with open(ACCOUNTS_FILE, 'r') as f:
        accounts = json.load(f)
    
    for account in accounts:
        if account['id'] == account_id:
            account.update({
                'name': data.get('name', account['name']),
                'type': data.get('type', account['type']),
                'number': data.get('number', account['number']),
                'zone': data.get('zone', account['zone'])
            })
            
            with open(ACCOUNTS_FILE, 'w') as f:
                json.dump(accounts, f, indent=2)
            
            return jsonify(account), 200
    
    return jsonify({'error': 'Account not found'}), 404

@bp.route('/<account_id>', methods=['DELETE'])
@login_required
def delete_account(account_id):
    ensure_accounts_file()
    
    with open(ACCOUNTS_FILE, 'r') as f:
        accounts = json.load(f)
    
    for i, account in enumerate(accounts):
        if account['id'] == account_id:
            del accounts[i]
            
            with open(ACCOUNTS_FILE, 'w') as f:
                json.dump(accounts, f, indent=2)
            
            return jsonify({'message': 'Account deleted successfully'}), 200
    
    return jsonify({'error': 'Account not found'}), 404 