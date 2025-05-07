from flask import Blueprint, request, jsonify
from flask_login import login_required
import json
import os
from datetime import datetime

invoices_bp = Blueprint('invoices', __name__)

INVOICES_FILE = 'data/invoices.json'

def ensure_invoices_file():
    os.makedirs('data', exist_ok=True)
    if not os.path.exists(INVOICES_FILE):
        with open(INVOICES_FILE, 'w') as f:
            json.dump([], f)

@invoices_bp.route('/api/invoices', methods=['GET'])
@login_required
def get_invoices():
    ensure_invoices_file()
    with open(INVOICES_FILE, 'r') as f:
        invoices = json.load(f)
    return jsonify(invoices), 200

@invoices_bp.route('/api/invoices', methods=['POST'])
@login_required
def create_invoice():
    data = request.get_json()
    required_fields = ['customer_id', 'items']
    
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    ensure_invoices_file()
    
    with open(INVOICES_FILE, 'r') as f:
        invoices = json.load(f)

    # Generate a simple ID (in a real app, use UUID)
    invoice_id = str(len(invoices) + 1)
    
    # Calculate total and tax
    subtotal = sum(item['quantity'] * item['unit_price'] for item in data['items'])
    tax_rate = data.get('tax_rate', 0.1)  # Default 10% tax
    tax_amount = subtotal * tax_rate
    total = subtotal + tax_amount
    
    new_invoice = {
        'id': invoice_id,
        'date': data.get('date', datetime.now().isoformat()),
        'customer_id': data['customer_id'],
        'items': data['items'],
        'subtotal': subtotal,
        'tax_rate': tax_rate,
        'tax_amount': tax_amount,
        'total': total,
        'status': data.get('status', 'pending'),
        'payment_date': data.get('payment_date'),
        'payment_info': data.get('payment_info')
    }
    
    invoices.append(new_invoice)
    
    with open(INVOICES_FILE, 'w') as f:
        json.dump(invoices, f, indent=2)
    
    return jsonify(new_invoice), 201

@invoices_bp.route('/api/invoices/<invoice_id>', methods=['PUT'])
@login_required
def update_invoice(invoice_id):
    data = request.get_json()
    
    ensure_invoices_file()
    
    with open(INVOICES_FILE, 'r') as f:
        invoices = json.load(f)
    
    for invoice in invoices:
        if invoice['id'] == invoice_id:
            # Recalculate totals if items are updated
            if 'items' in data:
                subtotal = sum(item['quantity'] * item['unit_price'] for item in data['items'])
                tax_rate = data.get('tax_rate', invoice['tax_rate'])
                tax_amount = subtotal * tax_rate
                total = subtotal + tax_amount
                
                invoice.update({
                    'items': data['items'],
                    'subtotal': subtotal,
                    'tax_rate': tax_rate,
                    'tax_amount': tax_amount,
                    'total': total
                })
            
            # Update other fields
            invoice.update({
                'date': data.get('date', invoice['date']),
                'customer_id': data.get('customer_id', invoice['customer_id']),
                'status': data.get('status', invoice['status']),
                'payment_date': data.get('payment_date', invoice.get('payment_date')),
                'payment_info': data.get('payment_info', invoice.get('payment_info'))
            })
            
            with open(INVOICES_FILE, 'w') as f:
                json.dump(invoices, f, indent=2)
            
            return jsonify(invoice), 200
    
    return jsonify({'error': 'Invoice not found'}), 404

@invoices_bp.route('/api/invoices/<invoice_id>', methods=['DELETE'])
@login_required
def delete_invoice(invoice_id):
    ensure_invoices_file()
    
    with open(INVOICES_FILE, 'r') as f:
        invoices = json.load(f)
    
    for i, invoice in enumerate(invoices):
        if invoice['id'] == invoice_id:
            del invoices[i]
            
            with open(INVOICES_FILE, 'w') as f:
                json.dump(invoices, f, indent=2)
            
            return jsonify({'message': 'Invoice deleted successfully'}), 200
    
    return jsonify({'error': 'Invoice not found'}), 404 