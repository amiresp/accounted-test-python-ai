from flask import Blueprint, request, jsonify
from flask_login import login_required
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

bp = Blueprint('reports', __name__, url_prefix='/api/reports')

def load_data():
    data = {}
    files = {
        'invoices': 'data/invoices.json',
        'customers': 'data/customers.json',
        'accounts': 'data/accounts.json'
    }
    
    for key, file_path in files.items():
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data[key] = json.load(f)
        else:
            data[key] = []
    
    return data

@bp.route('/profit-loss', methods=['GET'])
@login_required
def get_profit_loss():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    data = load_data()
    invoices = data['invoices']
    
    # Filter invoices by date range if provided
    if start_date and end_date:
        invoices = [
            inv for inv in invoices
            if start_date <= inv['date'] <= end_date
        ]
    
    # Calculate totals
    total_income = sum(inv['total'] for inv in invoices)
    total_expenses = 0  # In a real app, this would come from expense records
    
    profit_loss = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_profit': total_income - total_expenses,
        'period': {
            'start_date': start_date,
            'end_date': end_date
        }
    }
    
    return jsonify(profit_loss), 200

@bp.route('/income-expenses', methods=['GET'])
@login_required
def get_income_expenses():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    data = load_data()
    invoices = data['invoices']
    
    # Filter invoices by date range if provided
    if start_date and end_date:
        invoices = [
            inv for inv in invoices
            if start_date <= inv['date'] <= end_date
        ]
    
    # Group by month
    monthly_data = defaultdict(lambda: {'income': 0, 'expenses': 0})
    
    for invoice in invoices:
        date = datetime.fromisoformat(invoice['date'])
        month_key = date.strftime('%Y-%m')
        monthly_data[month_key]['income'] += invoice['total']
    
    # Convert to list format for chart.js
    chart_data = {
        'labels': sorted(monthly_data.keys()),
        'datasets': [
            {
                'label': 'Income',
                'data': [monthly_data[month]['income'] for month in sorted(monthly_data.keys())]
            },
            {
                'label': 'Expenses',
                'data': [monthly_data[month]['expenses'] for month in sorted(monthly_data.keys())]
            }
        ]
    }
    
    return jsonify(chart_data), 200

@bp.route('/top-customers', methods=['GET'])
@login_required
def get_top_customers():
    limit = int(request.args.get('limit', 5))
    
    data = load_data()
    invoices = data['invoices']
    customers = {c['id']: c for c in data['customers']}
    
    # Calculate revenue by customer
    customer_revenue = defaultdict(float)
    for invoice in invoices:
        customer_revenue[invoice['customer_id']] += invoice['total']
    
    # Sort customers by revenue
    top_customers = sorted(
        [
            {
                'id': cid,
                'name': f"{customers[cid]['first_name']} {customers[cid]['last_name']}",
                'revenue': revenue
            }
            for cid, revenue in customer_revenue.items()
        ],
        key=lambda x: x['revenue'],
        reverse=True
    )[:limit]
    
    return jsonify(top_customers), 200 