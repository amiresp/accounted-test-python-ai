from flask import Blueprint, jsonify, request, send_file
from flask_login import login_required
import json
import os
from datetime import datetime
import io
import traceback

data_bp = Blueprint('data', __name__, url_prefix='/api')

# Get the absolute path to the data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

def ensure_data_files():
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        data_files = ['accounts.json', 'customers.json', 'invoices.json', 'users.json']
        for file in data_files:
            file_path = os.path.join(DATA_DIR, file)
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False)
    except Exception as e:
        print(f"Error in ensure_data_files: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise

@data_bp.route('/export', methods=['GET'])
@login_required
def export_data():
    try:
        print(f"Starting export process...")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Data directory path: {DATA_DIR}")
        
        # Ensure data directory exists
        if not os.path.exists(DATA_DIR):
            print(f"Creating data directory: {DATA_DIR}")
            os.makedirs(DATA_DIR, exist_ok=True)
        
        ensure_data_files()
        
        # Create a dictionary to store all data
        export_data = {}
        
        # Read all data files
        for filename in ['accounts.json', 'customers.json', 'invoices.json']:
            file_path = os.path.join(DATA_DIR, filename)
            print(f"Reading file: {file_path}")
            
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        print(f"Data in {filename}: {data}")
                        export_data[filename] = data
                except json.JSONDecodeError as e:
                    print(f"Error reading {filename}: Invalid JSON format")
                    print(f"Error details: {str(e)}")
                    raise
                except Exception as e:
                    print(f"Error reading {filename}: {str(e)}")
                    print(f"Traceback: {traceback.format_exc()}")
                    raise
            else:
                print(f"File not found: {file_path}")
                export_data[filename] = []
        
        # Create a BytesIO object to store the JSON data
        memory_file = io.BytesIO()
        
        # Write the combined data to the BytesIO object
        try:
            json_data = json.dumps(export_data, indent=2, ensure_ascii=False)
            memory_file.write(json_data.encode('utf-8'))
            memory_file.seek(0)
        except Exception as e:
            print(f"Error writing to memory file: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            raise
        
        # Generate a filename with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d')
        filename = f'accounted-backup-{timestamp}.json'
        
        print(f"Export successful. File size: {memory_file.getbuffer().nbytes} bytes")
        
        # Return the JSON file
        return send_file(
            memory_file,
            mimetype='application/json; charset=utf-8',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        print(f"Error in export_data: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Failed to export data: {str(e)}'}), 500

@data_bp.route('/import', methods=['POST'])
@login_required
def import_data():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.json'):
            return jsonify({'error': 'Invalid file format. Please upload a JSON file'}), 400
        
        # Read and parse the JSON file
        try:
            import_data = json.loads(file.read().decode('utf-8'))
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON file'}), 400
        
        # Validate the import data structure
        if not isinstance(import_data, dict):
            return jsonify({'error': 'Invalid data format'}), 400
        
        # Import each data file
        for filename in ['accounts.json', 'customers.json', 'invoices.json']:
            if filename in import_data:
                file_path = os.path.join(DATA_DIR, filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(import_data[filename], f, indent=2, ensure_ascii=False)
        
        return jsonify({'message': 'Data imported successfully'}), 200
    except Exception as e:
        print(f"Error in import_data: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Failed to import data: {str(e)}'}), 500 