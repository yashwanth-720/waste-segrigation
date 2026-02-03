from flask import Flask, render_template, request, jsonify, Response, session
from flask_cors import CORS
import tensorflow as tf
import numpy as np
import cv2
import base64
from PIL import Image
import io
import os
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'waste-ai-secret-key-2024')
CORS(app)

from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions

base_model = MobileNetV2(weights='imagenet', include_top=True)

CLASS_LABELS = ['Biomedical', 'E-Waste', 'Glass', 'Hazardous', 'Metal', 'Organic', 'Paper', 'Plastic']
IMG_SIZE = (224, 224)

analytics_data = {
    'total_predictions': 0,
    'category_counts': defaultdict(int),
    'predictions_history': []
}

def track_prediction(category, confidence):
    analytics_data['total_predictions'] += 1
    analytics_data['category_counts'][category] += 1
    analytics_data['predictions_history'].append({
        'category': category,
        'confidence': confidence,
        'timestamp': datetime.now().isoformat()
    })
    if len(analytics_data['predictions_history']) > 100:
        analytics_data['predictions_history'].pop(0)

def preprocess_image(image):
    img = image.resize(IMG_SIZE)
    img_array = np.array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    return img_array

def predict_waste(image):
    processed_img = preprocess_image(image)
    predictions = base_model.predict(processed_img, verbose=0)
    decoded = decode_predictions(predictions, top=10)[0]
    
    print(f"Top 10 ImageNet predictions: {[(name, score) for _, name, score in decoded]}")
    
    category_scores = {label: 0.0 for label in CLASS_LABELS}
    
    for _, class_name, score in decoded:
        class_lower = class_name.lower()
        score_val = float(score) * 100
        
        # Direct keyword matching with higher weights
        if any(k in class_lower for k in ['bottle', 'pop', 'water_bottle', 'beer_bottle', 'wine_bottle']):
            if 'beer' in class_lower or 'wine' in class_lower:
                category_scores['Glass'] += score_val * 1.5
            else:
                category_scores['Plastic'] += score_val * 1.5
        elif any(k in class_lower for k in ['can', 'tin', 'soup_bowl']):
            category_scores['Metal'] += score_val * 1.5
        elif any(k in class_lower for k in ['banana', 'orange', 'lemon', 'apple', 'strawberry', 'broccoli', 'mushroom', 'cucumber', 'fruit', 'vegetable']):
            category_scores['Organic'] += score_val * 1.5
        elif any(k in class_lower for k in ['cardboard', 'carton', 'envelope', 'notebook', 'book', 'paper']):
            category_scores['Paper'] += score_val * 1.5
        elif any(k in class_lower for k in ['jar', 'goblet', 'cup', 'glass', 'vase']):
            category_scores['Glass'] += score_val * 1.5
        elif any(k in class_lower for k in ['cellular', 'laptop', 'computer', 'monitor', 'keyboard', 'mouse', 'remote', 'ipod', 'television', 'printer']):
            category_scores['E-Waste'] += score_val * 1.5
        elif any(k in class_lower for k in ['syringe', 'stethoscope', 'mask', 'bandage']):
            category_scores['Biomedical'] += score_val * 1.5
        elif any(k in class_lower for k in ['battery', 'lighter', 'spray', 'aerosol']):
            category_scores['Hazardous'] += score_val * 1.5
        elif any(k in class_lower for k in ['bag', 'container', 'wrapper', 'tray']):
            category_scores['Plastic'] += score_val * 0.8
        elif any(k in class_lower for k in ['food', 'plant', 'leaf']):
            category_scores['Organic'] += score_val * 0.8
        elif any(k in class_lower for k in ['metal', 'steel', 'iron']):
            category_scores['Metal'] += score_val * 0.8
    
    # Add minimum baseline to prevent all zeros
    for label in CLASS_LABELS:
        if category_scores[label] == 0:
            category_scores[label] = 1.0
    
    total = sum(category_scores.values())
    probabilities = {k: (v/total)*100 for k, v in category_scores.items()}
    
    category = max(probabilities, key=probabilities.get)
    confidence = probabilities[category]
    
    print(f"Final scores: {probabilities}")
    print(f"Predicted: {category} ({confidence:.2f}%)")
    
    waste_details = {
        'Organic': {
            'disposal': 'Compost bin or organic waste collection',
            'decomposition': 'Biodegradable (2-6 months)',
            'environmental_impact': 'Low - Can be composted into nutrient-rich soil',
            'examples': ['Food scraps', 'Garden waste', 'Fruits', 'Vegetables', 'Wood'],
            'tips': 'Separate from other waste to enable composting',
            'color': '#4CAF50'
        },
        'Paper': {
            'disposal': 'Paper recycling bin (blue bin)',
            'decomposition': 'Biodegradable (2-6 weeks)',
            'environmental_impact': 'Low - Highly recyclable, saves trees',
            'examples': ['Newspapers', 'Cardboard', 'Books', 'Magazines', 'Office paper'],
            'tips': 'Keep dry and clean, remove plastic windows from envelopes',
            'color': '#2196F3'
        },
        'Plastic': {
            'disposal': 'Plastic recycling bin (check recycling codes 1-7)',
            'decomposition': 'Non-biodegradable (450-1000 years)',
            'environmental_impact': 'High - Major ocean pollutant, recycle or reduce usage',
            'examples': ['Bottles', 'Bags', 'Containers', 'Packaging', 'Straws', 'Cups'],
            'tips': 'Check recycling codes, rinse before recycling, avoid single-use',
            'color': '#FF9800'
        },
        'Metal': {
            'disposal': 'Metal recycling bin or scrap collection',
            'decomposition': 'Non-biodegradable (50-500 years)',
            'environmental_impact': 'Medium - Highly recyclable, saves mining resources',
            'examples': ['Cans', 'Foil', 'Wire', 'Appliances', 'Tools', 'Nails'],
            'tips': 'Rinse containers, separate ferrous and non-ferrous metals',
            'color': '#9E9E9E'
        },
        'Glass': {
            'disposal': 'Glass recycling bin (separate by color)',
            'decomposition': 'Non-biodegradable (1 million years)',
            'environmental_impact': 'Low - 100% recyclable without quality loss',
            'examples': ['Bottles', 'Jars', 'Windows', 'Mirrors', 'Glassware'],
            'tips': 'Remove caps/lids, separate by color (clear, green, brown)',
            'color': '#00BCD4'
        },
        'E-Waste': {
            'disposal': 'E-waste collection center or authorized recycler',
            'decomposition': 'Non-biodegradable (contains toxic materials)',
            'environmental_impact': 'CRITICAL - Contains heavy metals, must be recycled properly',
            'examples': ['Phones', 'Laptops', 'TVs', 'Batteries', 'Chargers', 'Keyboards'],
            'tips': 'NEVER throw in regular bins! Take to e-waste recycling centers',
            'color': '#9C27B0'
        },
        'Hazardous': {
            'disposal': 'Special hazardous waste facility (DO NOT mix with regular waste)',
            'decomposition': 'Toxic - Never decomposes safely',
            'environmental_impact': 'CRITICAL - Extremely dangerous to environment and health',
            'examples': ['Chemicals', 'Paint', 'Pesticides', 'Motor oil', 'Cleaning agents'],
            'tips': 'NEVER throw in regular bins! Contact local hazardous waste facility',
            'color': '#F44336'
        },
        'Biomedical': {
            'disposal': 'Yellow biomedical waste bag - Hospital/clinic disposal only',
            'decomposition': 'Infectious - Requires incineration',
            'environmental_impact': 'CRITICAL - Biohazard risk, requires specialized treatment',
            'examples': ['Syringes', 'Bandages', 'Medical gloves', 'Surgical waste', 'Expired medicines'],
            'tips': 'BIOHAZARD! Use yellow bags, contact healthcare waste management',
            'color': '#FFEB3B'
        }
    }
    
    return category, confidence, probabilities, waste_details.get(category, waste_details['Paper'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        image = Image.open(file.stream).convert('RGB')
        
        category, confidence, probabilities, details = predict_waste(image)
        track_prediction(category, confidence)
        
        return jsonify({
            'category': category,
            'confidence': f'{confidence:.2f}%',
            'probabilities': probabilities,
            'details': details,
            'success': True
        })
    except Exception as e:
        print(f"Error in predict: {str(e)}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/predict_base64', methods=['POST'])
def predict_base64():
    try:
        data = request.get_json()
        image_data = data['image'].split(',')[1]
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        category, confidence, probabilities, details = predict_waste(image)
        track_prediction(category, confidence)
        
        return jsonify({
            'category': category,
            'confidence': f'{confidence:.2f}%',
            'probabilities': probabilities,
            'details': details,
            'success': True
        })
    except Exception as e:
        print(f"Error in predict_base64: {str(e)}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/analytics')
def get_analytics():
    return jsonify({
        'total_predictions': analytics_data['total_predictions'],
        'category_counts': dict(analytics_data['category_counts']),
        'recent_predictions': analytics_data['predictions_history'][-10:],
        'success': True
    })

@app.route('/camera_proxy')
def camera_proxy():
    import requests as req
    url = request.args.get('url')
    if not url:
        return 'No URL provided', 400
    try:
        response = req.get(url, stream=True, timeout=5)
        return Response(response.iter_content(chunk_size=1024), 
                       content_type=response.headers.get('content-type'))
    except:
        return 'Camera connection failed', 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port, threaded=True)
