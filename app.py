from flask import Flask, request, render_template, jsonify, flash, redirect, url_for
import os
from werkzeug.utils import secure_filename
import passporteye
from mrz.checker.td3 import TD3CodeChecker
from pdf2image import convert_from_path  # For PDF to image conversion
import tempfile

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secure-random-key'  # Generate a strong key
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()  # Use temp dir for security
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'pdf'}
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB limit

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def convert_pdf_to_image(pdf_path):
    # Convert first page of PDF to image
    images = convert_from_path(pdf_path, first_page=1, last_page=1)
    if images:
        temp_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_image.png')
        images[0].save(temp_image_path, 'PNG')
        return temp_image_path
    return None

def extract_mrz_data(file_path):
    # Handle PDFs by converting to image
    if file_path.lower().endswith('.pdf'):
        image_path = convert_pdf_to_image(file_path)
        if not image_path:
            raise ValueError("Failed to convert PDF")
    else:
        image_path = file_path
    
    # Extract MRZ
    mrz = passporteye.read_mrz(image_path)
    if mrz is None:
        raise ValueError("MRZ not detected")
    
    mrz_code = TD3CodeChecker(mrz)
    if not mrz_code:
        raise ValueError("Invalid MRZ format")
    
    # Parse names
    last_name = mrz_code.fields['surname']
    first_name = mrz_code.fields['name']
    name_parts = first_name.split(' ')
    first = name_parts[0] if name_parts else ''
    middle = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
    
    # Other fields
    doc_number = mrz_code.fields['document_number']
    nationality = mrz_code.fields['nationality']
    dob = mrz_code.fields['birth_date']
    expiration = mrz_code.fields['expiry_date']
    gender = mrz_code.fields['sex']
    
    # Clean up temp image if created
    if file_path.lower().endswith('.pdf') and os.path.exists(image_path):
        os.remove(image_path)
    
    return {
        'first_name': first,
        'middle_name': middle,
        'last_name': last_name,
        'doc_number': doc_number,
        'nationality': nationality,
        'dob': dob,
        'expiration': expiration,
        'gender': gender
    }

def generate_amadeus_docs(data):
    def format_date(date_str):  # YYMMDD to DDMMMYY
        year = '20' + date_str[:2] if int(date_str[:2]) < 50 else '19' + date_str[:2]
        month_map = {'01':'JAN', '02':'FEB', '03':'MAR', '04':'APR', '05':'MAY', '06':'JUN',
                     '07':'JUL', '08':'AUG', '09':'SEP', '10':'OCT', '11':'NOV', '12':'DEC'}
        month = month_map[date_str[2:4]]
        day = date_str[4:]
        return f"{day}{month}{year[-2:]}"
    
    dob_formatted = format_date(data['dob'])
    exp_formatted = format_date(data['expiration'])
    issuing_country = data['nationality']
    
    docs_line = f"SRCOS YY HK1-{issuing_country}-{data['doc_number']}-{data['nationality']}-{dob_formatted}-{data['gender']}-{exp_formatted}-{data['last_name']}/{data['first_name']} {data['middle_name']}".strip()
    return docs_line

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        data = extract_mrz_data(filepath)
        docs_command = generate_amadeus_docs(data)
        os.remove(filepath)  # Delete after processing
        return jsonify({
            'first_name': data['first_name'],
            'middle_name': data['middle_name'],
            'last_name': data['last_name'],
            'command': docs_command
        })
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
