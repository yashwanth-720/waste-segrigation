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

# Analytics storage (in-memory for demo, use database in production)
analytics_data = {
    'total_predictions': 0,
    'category_counts': defaultdict(int),
    'predictions_history': []
}

IMAGENET_TO_WASTE = {
    'bottle': 'Plastic', 'water_bottle': 'Plastic', 'pop_bottle': 'Plastic', 'pill_bottle': 'Plastic',
    'can': 'Metal', 'beer_bottle': 'Glass', 'wine_bottle': 'Glass', 'jar': 'Glass',
    'plastic_bag': 'Plastic', 'shopping_basket': 'Plastic', 'tray': 'Plastic',
    'banana': 'Organic', 'orange': 'Organic', 'lemon': 'Organic', 'apple': 'Organic', 'strawberry': 'Organic',
    'broccoli': 'Organic', 'mushroom': 'Organic', 'bell_pepper': 'Organic', 'cucumber': 'Organic',
    'cardboard': 'Paper', 'carton': 'Paper', 'envelope': 'Paper', 'notebook': 'Paper', 'book': 'Paper',
    'syringe': 'Biomedical', 'stethoscope': 'Biomedical', 'mask': 'Biomedical', 'bandage': 'Biomedical',
    'battery': 'Hazardous', 'lighter': 'Hazardous', 'spray': 'Hazardous', 'aerosol': 'Hazardous',
    'tin_can': 'Metal', 'soup_bowl': 'Glass', 'cup': 'Glass', 'coffee_mug': 'Glass', 'goblet': 'Glass',
    'paper_towel': 'Paper', 'tissue': 'Paper', 'toilet_tissue': 'Paper',
    'cellular_telephone': 'E-Waste', 'laptop': 'E-Waste', 'computer': 'E-Waste', 'monitor': 'E-Waste',
    'mouse': 'E-Waste', 'keyboard': 'E-Waste', 'remote_control': 'E-Waste', 'ipod': 'E-Waste',
    'hard_disc': 'E-Waste', 'cd_player': 'E-Waste', 'television': 'E-Waste', 'printer': 'E-Waste'
}

def track_prediction(category, confidence):
    """Track prediction for analytics"""
    analytics_data['total_predictions'] += 1
    analytics_data['category_counts'][category] += 1
    analytics_data['predictions_history'].append({
        'category': category,
        'confidence': confidence,
        'timestamp': datetime.now().isoformat()
    })
    # Keep only last 100 predictions
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
    predictions = base_model.predict(processed_img)
    decoded = decode_predictions(predictions, top=10)[0]
    
    category_scores = {label: 0.0 for label in CLASS_LABELS}
    
    for _, class_name, score in decoded:
        class_lower = class_name.lower().replace('_', ' ')
        
        for key, waste_type in IMAGENET_TO_WASTE.items():
            if key in class_lower:
                category_scores[waste_type] += float(score) * 100
                break
        else:
            if any(word in class_lower for word in ['bottle', 'container', 'bag', 'wrapper', 'cup', 'straw']):
                category_scores['Plastic'] += float(score) * 40
            elif any(word in class_lower for word in ['can', 'screw', 'nail', 'wire', 'chain', 'hook']):
                category_scores['Metal'] += float(score) * 40
            elif any(word in class_lower for word in ['fruit', 'vegetable', 'food', 'plant', 'leaf']):
                category_scores['Organic'] += float(score) * 40
            elif any(word in class_lower for word in ['glass', 'jar', 'vase', 'goblet', 'wine']):
                category_scores['Glass'] += float(score) * 40
            elif any(word in class_lower for word in ['paper', 'cardboard', 'book', 'notebook', 'envelope']):
                category_scores['Paper'] += float(score) * 40
            elif any(word in class_lower for word in ['phone', 'laptop', 'computer', 'monitor', 'keyboard', 'mouse', 'electronic', 'circuit', 'chip']):
                category_scores['E-Waste'] += float(score) * 40
            elif any(word in class_lower for word in ['syringe', 'medical', 'pill', 'medicine', 'bandage', 'mask']):
                category_scores['Biomedical'] += float(score) * 40
            elif any(word in class_lower for word in ['battery', 'chemical', 'toxic', 'spray', 'aerosol']):
                category_scores['Hazardous'] += float(score) * 40
    
    total = sum(category_scores.values())
    if total > 0:
        probabilities = {k: v for k, v in category_scores.items()}
    else:
        probabilities = {label: 100/8 for label in CLASS_LABELS}
    
    category = max(probabilities, key=probabilities.get)
    confidence = probabilities[category]
    
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
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/analytics')
def get_analytics():
    """Get analytics data"""
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
