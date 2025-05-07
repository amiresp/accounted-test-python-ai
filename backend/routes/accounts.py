from flask import Blueprint, jsonify, request
from flask_login import login_required
import json
import os

accounts_bp = Blueprint('accounts', __name__)

def get_accounts_file():
    return 'data/accounts.json'

def ensure_accounts_file():
    os.makedirs('data', exist_ok=True)
    if not os.path.exists(get_accounts_file()):
        with open(get_accounts_file(), 'w') as f:
            json.dump([], f)

@accounts_bp.route('/api/accounts', methods=['GET'])
@login_required
def get_accounts():
    ensure_accounts_file()
    with open(get_accounts_file(), 'r') as f:
        accounts = json.load(f)
    return jsonify(accounts)

@accounts_bp.route('/api/accounts', methods=['POST'])
@login_required
def create_account():
    ensure_accounts_file()
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'type', 'number', 'zone']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Generate a unique ID
    with open(get_accounts_file(), 'r') as f:
        accounts = json.load(f)
        new_id = str(len(accounts) + 1)
    
    # Create new account
    new_account = {
        'id': new_id,
        'name': data['name'],
        'type': data['type'],
        'number': data['number'],
        'zone': data['zone']
    }
    
    # Save to file
    accounts.append(new_account)
    with open(get_accounts_file(), 'w') as f:
        json.dump(accounts, f, indent=2)
    
    return jsonify(new_account), 201

@accounts_bp.route('/api/accounts/<account_id>', methods=['PUT'])
@login_required
def update_account(account_id):
    ensure_accounts_file()
    data = request.get_json()
    
    with open(get_accounts_file(), 'r') as f:
        accounts = json.load(f)
    
    # Find and update account
    for account in accounts:
        if account['id'] == account_id:
            account.update({
                'name': data.get('name', account['name']),
                'type': data.get('type', account['type']),
                'number': data.get('number', account['number']),
                'zone': data.get('zone', account['zone'])
            })
            
            with open(get_accounts_file(), 'w') as f:
                json.dump(accounts, f, indent=2)
            
            return jsonify(account)
    
    return jsonify({'error': 'Account not found'}), 404

@accounts_bp.route('/api/accounts/<account_id>', methods=['DELETE'])
@login_required
def delete_account(account_id):
    ensure_accounts_file()
    
    with open(get_accounts_file(), 'r') as f:
        accounts = json.load(f)
    
    # Find and remove account
    for i, account in enumerate(accounts):
        if account['id'] == account_id:
            accounts.pop(i)
            
            with open(get_accounts_file(), 'w') as f:
                json.dump(accounts, f, indent=2)
            
            return jsonify({'message': 'Account deleted successfully'})
    
    return jsonify({'error': 'Account not found'}), 404 