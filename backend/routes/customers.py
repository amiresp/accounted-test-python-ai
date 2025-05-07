from flask import Blueprint, request, jsonify
from flask_login import login_required
import json
import os

customers_bp = Blueprint('customers', __name__)

CUSTOMERS_FILE = 'data/customers.json'

def ensure_customers_file():
    os.makedirs('data', exist_ok=True)
    if not os.path.exists(CUSTOMERS_FILE):
        with open(CUSTOMERS_FILE, 'w') as f:
            json.dump([], f)

@customers_bp.route('/api/customers', methods=['GET'])
@login_required
def get_customers():
    ensure_customers_file()
    with open(CUSTOMERS_FILE, 'r') as f:
        customers = json.load(f)
    return jsonify(customers), 200

@customers_bp.route('/api/customers', methods=['POST'])
@login_required
def create_customer():
    data = request.get_json()
    required_fields = ['first_name', 'last_name']
    
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    ensure_customers_file()
    
    with open(CUSTOMERS_FILE, 'r') as f:
        customers = json.load(f)

    # Generate a simple ID (in a real app, use UUID)
    customer_id = str(len(customers) + 1)
    
    new_customer = {
        'id': customer_id,
        'first_name': data['first_name'],
        'last_name': data['last_name'],
        'company': data.get('company', ''),
        'mobile': data.get('mobile', ''),
        'address': data.get('address', ''),
        'credit_cards': data.get('credit_cards', []),
        'bank_accounts': data.get('bank_accounts', [])
    }
    
    customers.append(new_customer)
    
    with open(CUSTOMERS_FILE, 'w') as f:
        json.dump(customers, f, indent=2)
    
    return jsonify(new_customer), 201

@customers_bp.route('/api/customers/<customer_id>', methods=['PUT'])
@login_required
def update_customer(customer_id):
    data = request.get_json()
    
    ensure_customers_file()
    
    with open(CUSTOMERS_FILE, 'r') as f:
        customers = json.load(f)
    
    for customer in customers:
        if customer['id'] == customer_id:
            customer.update({
                'first_name': data.get('first_name', customer['first_name']),
                'last_name': data.get('last_name', customer['last_name']),
                'company': data.get('company', customer['company']),
                'mobile': data.get('mobile', customer['mobile']),
                'address': data.get('address', customer['address']),
                'credit_cards': data.get('credit_cards', customer['credit_cards']),
                'bank_accounts': data.get('bank_accounts', customer['bank_accounts'])
            })
            
            with open(CUSTOMERS_FILE, 'w') as f:
                json.dump(customers, f, indent=2)
            
            return jsonify(customer), 200
    
    return jsonify({'error': 'Customer not found'}), 404

@customers_bp.route('/api/customers/<customer_id>', methods=['DELETE'])
@login_required
def delete_customer(customer_id):
    ensure_customers_file()
    
    with open(CUSTOMERS_FILE, 'r') as f:
        customers = json.load(f)
    
    for i, customer in enumerate(customers):
        if customer['id'] == customer_id:
            del customers[i]
            
            with open(CUSTOMERS_FILE, 'w') as f:
                json.dump(customers, f, indent=2)
            
            return jsonify({'message': 'Customer deleted successfully'}), 200
    
    return jsonify({'error': 'Customer not found'}), 404 