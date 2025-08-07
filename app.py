import os
import logging
from flask import Flask, render_template, request, jsonify
from mock_data import get_offender_data_by_zip

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_zip():
    """Search for offenders by ZIP code"""
    try:
        data = request.get_json()
        zip_code = data.get('zip_code', '').strip()
        
        # Validate ZIP code format
        if not zip_code:
            return jsonify({
                'success': False,
                'error': 'ZIP code is required'
            }), 400
            
        if not zip_code.isdigit() or len(zip_code) != 5:
            return jsonify({
                'success': False,
                'error': 'Please enter a valid 5-digit ZIP code'
            }), 400
        
        # Get mock data for the ZIP code
        offender_data = get_offender_data_by_zip(zip_code)
        
        response = {
            'success': True,
            'zip_code': zip_code,
            'offender_count': offender_data['count'],
            'has_offenders': offender_data['count'] > 0,
            'offenders': offender_data['offenders'],
            'message': f"Found {offender_data['count']} registered offender(s) in ZIP code {zip_code}" if offender_data['count'] > 0 else f"No registered offenders found in ZIP code {zip_code}"
        }
        
        return jsonify(response)
        
    except Exception as e:
        logging.error(f"Error processing search request: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while processing your request. Please try again.'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error. Please try again later.'
    }), 500
