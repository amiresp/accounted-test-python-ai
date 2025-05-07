from flask import Blueprint, request, jsonify
from flask_login import login_required
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

reports_bp = Blueprint('reports', __name__, url_prefix='/api/reports')

INVOICES_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'invoices.json')
CUSTOMERS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'customers.json')

def ensure_data_files():
    os.makedirs(os.path.dirname(INVOICES_FILE), exist_ok=True)
    if not os.path.exists(INVOICES_FILE):
        with open(INVOICES_FILE, 'w') as f:
            json.dump([], f)
    if not os.path.exists(CUSTOMERS_FILE):
        with open(CUSTOMERS_FILE, 'w') as f:
            json.dump([], f)

def load_data():
    ensure_data_files()
    try:
        with open(INVOICES_FILE, 'r') as f:
            invoices = json.load(f)
        with open(CUSTOMERS_FILE, 'r') as f:
            customers = json.load(f)
        return invoices, customers
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return [], []

@reports_bp.route('/profit-loss', methods=['GET'])
@login_required
def get_profit_loss():
    try:
        invoices, _ = load_data()
        
        # Get date range from query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Filter invoices by date range if provided
        if start_date and end_date:
            try:
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                invoices = [
                    inv for inv in invoices
                    if start_date <= datetime.fromisoformat(inv['date'].replace('Z', '+00:00')) <= end_date
                ]
            except ValueError as e:
                print(f"Date parsing error: {str(e)}")
                return jsonify({'error': 'Invalid date format'}), 400
        
        # Calculate totals
        total_income = sum(inv['total'] for inv in invoices if inv['status'] == 'paid')
        total_expenses = 0  # In a real app, this would come from expense records
        
        profit_loss = {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_profit': total_income - total_expenses,
            'period': {
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None
            }
        }
        
        return jsonify(profit_loss), 200
    except Exception as e:
        print(f"Error in profit-loss: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@reports_bp.route('/top-customers', methods=['GET'])
@login_required
def get_top_customers():
    try:
        invoices, customers = load_data()
        
        # Get date range from query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Filter invoices by date range if provided
        if start_date and end_date:
            try:
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                invoices = [
                    inv for inv in invoices
                    if start_date <= datetime.fromisoformat(inv['date'].replace('Z', '+00:00')) <= end_date
                ]
            except ValueError as e:
                print(f"Date parsing error: {str(e)}")
                return jsonify({'error': 'Invalid date format'}), 400
        
        # Calculate customer totals
        customer_totals = {}
        for invoice in invoices:
            if invoice['status'] == 'paid':
                customer_id = invoice['customer_id']
                customer_totals[customer_id] = customer_totals.get(customer_id, 0) + invoice['total']
        
        # Sort customers by total revenue
        sorted_customers = sorted(customer_totals.items(), key=lambda x: x[1], reverse=True)
        
        # Get top 5 customers with their details
        top_customers = []
        for customer_id, total in sorted_customers[:5]:
            customer = next((c for c in customers if c['id'] == customer_id), None)
            if customer:
                top_customers.append({
                    'id': customer['id'],
                    'name': f"{customer['first_name']} {customer['last_name']}",
                    'revenue': total
                })
        
        return jsonify(top_customers), 200
    except Exception as e:
        print(f"Error in top-customers: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@reports_bp.route('/income-expenses', methods=['GET'])
@login_required
def get_income_expenses():
    try:
        invoices, _ = load_data()
        
        # Get date range from query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({'error': 'Start date and end date are required'}), 400
        
        try:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError as e:
            print(f"Date parsing error: {str(e)}")
            return jsonify({'error': 'Invalid date format'}), 400
        
        # Initialize data structure for daily totals
        daily_data = {}
        current_date = start_date
        while current_date <= end_date:
            daily_data[current_date.isoformat()] = {
                'income': 0,
                'expenses': 0
            }
            current_date += timedelta(days=1)
        
        # Process invoices
        for invoice in invoices:
            try:
                invoice_date = datetime.fromisoformat(invoice['date'].replace('Z', '+00:00'))
                if start_date <= invoice_date <= end_date:
                    date_key = invoice_date.isoformat()
                    if invoice['status'] == 'paid':
                        daily_data[date_key]['income'] += invoice['total']
            except (ValueError, KeyError) as e:
                print(f"Error processing invoice: {str(e)}")
                continue
        
        # Convert to array format for chart.js
        chart_data = {
            'labels': list(daily_data.keys()),
            'datasets': [
                {
                    'label': 'Income',
                    'data': [day['income'] for day in daily_data.values()],
                    'borderColor': 'rgb(75, 192, 192)',
                    'tension': 0.1
                },
                {
                    'label': 'Expenses',
                    'data': [day['expenses'] for day in daily_data.values()],
                    'borderColor': 'rgb(255, 99, 132)',
                    'tension': 0.1
                }
            ]
        }
        
        return jsonify(chart_data), 200
    except Exception as e:
        print(f"Error in income-expenses: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500 