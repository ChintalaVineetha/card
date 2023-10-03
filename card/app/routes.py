from app import app
from flask import jsonify, render_template, request
import cv2
import pytesseract
from PIL import Image
import numpy as np
import re

@app.route('/')
def index():
    return render_template('index.html')

def extract_information(image):
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    extracted_text = pytesseract.image_to_string(image)
    return extracted_text

def parser(text, label):
    if label == 'PHONE':
        text = text.lower()
        text = re.sub(r'\D', '', text)

    elif label == 'EMAIL':
        text = text.lower()
        allow_special_char = '@_.\-'
        text = re.sub(r'[^A-Za-z0-9{} ]'.format(allow_special_char), '', text)

    elif label == 'WEB':
        text = text.lower()
        allow_special_char = ':/.%#\-'
        text = re.sub(r'[^A-Za-z0-9{} ]'.format(allow_special_char), '', text)

    elif label in ('NAME', 'DES'):
        text = text.lower()
        text = re.sub(r'[^a-z ]', '', text)
        text = text.title()

    elif label == 'ORG':
        text = text.lower()
        text = re.sub(r'[^a-z0-9 ]', '', text)
        text = text.title()

    return text

def process_extracted_text(extracted_text):
    
    address_pattern = r'(?i)(?:\b(?:address|add|addr)\b[\w\s:,.#-/]+)'
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    name_pattern = r'(?i)(?:\b(?:name|nm)\b[\w\s]+)'
    phone_pattern = r'(?i)(?:\b(?:phone|ph|mob|mobile)\b\s*[:-]?\s*[0-9()\s-]+)'

    extracted_info = {
        'address': re.search(address_pattern, extracted_text),
        'email': re.search(email_pattern, extracted_text),
        'name': re.search(name_pattern, extracted_text),
        'phone': re.search(phone_pattern, extracted_text)
    }

    if extracted_info['name']:
        print("Extracted Name:", extracted_info['name'].group())

    for label, match in extracted_info.items():
        if match:
            extracted_info[label] = parser(match.group(), label)
        else:
            extracted_info[label] = None

    return extracted_info


@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"})

    image = request.files['image']
    image = Image.open(image)
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Apply image processing and OCR here
    extracted_text = pytesseract.image_to_string(image)
    simplified_text = re.sub(r'\n+', '\n', extracted_text).strip()

    # Process the extracted text to get name, email, and phone
    extracted_info = process_extracted_text(simplified_text)

    return render_template('information.html',address=extracted_info['address'], name=extracted_info['name'], email=extracted_info['email'], phone=extracted_info['phone'])


