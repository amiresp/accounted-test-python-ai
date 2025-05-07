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

def get_reports_file():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, 'reports.json')

def get_default_date_range():
    today = datetime.now()
    # Set to first day of current month
    current_month_start = today.replace(day=1)
    # Set to first day of previous month
    previous_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
    # Set to last day of current month
    current_month_end = (current_month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    return previous_month_start.strftime('%Y-%m-%d'), current_month_end.strftime('%Y-%m-%d')

@reports_bp.route('/income-expenses', methods=['GET'])
def get_income_expenses():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # If dates are not provided, use default range (previous month to current month)
        if not start_date or not end_date:
            start_date, end_date = get_default_date_range()

        # Convert ISO format dates to datetime objects
        try:
            # Remove timezone info and parse date
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00').split('T')[0])
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00').split('T')[0])
        except ValueError as e:
            print(f"Date parsing error: {str(e)}")
            return jsonify({
                'income': 0,
                'expenses': 0,
                'net': 0,
                'start_date': start_date,
                'end_date': end_date,
                'invoice_count': 0,
                'message': 'Invalid date format, using default values'
            })

        # Ensure data files exist
        ensure_data_files()

        # Read invoices data
        try:
            with open(INVOICES_FILE, 'r') as f:
                invoices = json.load(f)
                if not isinstance(invoices, list):
                    print("Error: Invalid data format in invoices file")
                    invoices = []
        except json.JSONDecodeError:
            print("Error: Invalid JSON in invoices file")
            invoices = []
        except Exception as e:
            print(f"Error reading invoices file: {str(e)}")
            invoices = []

        # Filter invoices by date range
        filtered_invoices = []
        for invoice in invoices:
            try:
                if not isinstance(invoice, dict):
                    continue
                    
                invoice_date = datetime.strptime(invoice.get('date', ''), '%Y-%m-%d')
                if start <= invoice_date <= end:
                    filtered_invoices.append(invoice)
            except (ValueError, TypeError) as e:
                print(f"Error processing invoice date: {str(e)}")
                continue

        # Calculate totals with error handling
        income = 0
        expenses = 0
        for invoice in filtered_invoices:
            try:
                total = float(invoice.get('total', 0))
                invoice_type = invoice.get('type', '').lower()
                if invoice_type == 'income':
                    income += total
                elif invoice_type == 'expense':
                    expenses += total
            except (ValueError, TypeError) as e:
                print(f"Error processing invoice total: {str(e)}")
                continue

        net = income - expenses

        response = {
            'income': income,
            'expenses': expenses,
            'net': net,
            'start_date': start_date,
            'end_date': end_date,
            'invoice_count': len(filtered_invoices)
        }

        # Add message if no data
        if len(filtered_invoices) == 0:
            response['message'] = 'No data available for the selected period'

        return jsonify(response)

    except Exception as e:
        print(f"Error in income-expenses report: {str(e)}")
        return jsonify({
            'income': 0,
            'expenses': 0,
            'net': 0,
            'start_date': start_date if 'start_date' in locals() else None,
            'end_date': end_date if 'end_date' in locals() else None,
            'invoice_count': 0,
            'message': 'Error generating report'
        }) 