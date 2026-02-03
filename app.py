from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import tensorflow as tf
import numpy as np
import cv2
import base64
from PIL import Image
import io
import os

app = Flask(__name__)
CORS(app)

# Use pre-trained MobileNetV2 for feature extraction
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions

base_model = MobileNetV2(weights='imagenet', include_top=True)

# Class labels
CLASS_LABELS = ['Biomedical', 'Glass', 'Hazardous', 'Metal', 'Organic', 'Plastic', 'Recyclable']
IMG_SIZE = (224, 224)

# ImageNet class to waste category mapping
IMAGENET_TO_WASTE = {
    'bottle': 'Plastic', 'water_bottle': 'Plastic', 'pop_bottle': 'Plastic', 'pill_bottle': 'Plastic',
    'can': 'Metal', 'beer_bottle': 'Glass', 'wine_bottle': 'Glass',
    'plastic_bag': 'Plastic', 'shopping_basket': 'Plastic',
    'banana': 'Organic', 'orange': 'Organic', 'lemon': 'Organic', 'apple': 'Organic',
    'broccoli': 'Organic', 'mushroom': 'Organic', 'bell_pepper': 'Organic',
    'cardboard': 'Recyclable', 'carton': 'Recyclable', 'envelope': 'Recyclable',
    'syringe': 'Biomedical', 'stethoscope': 'Biomedical', 'mask': 'Biomedical',
    'battery': 'Hazardous', 'lighter': 'Hazardous', 'spray': 'Hazardous',
    'tin_can': 'Metal', 'soup_bowl': 'Glass', 'cup': 'Glass', 'coffee_mug': 'Glass',
    'paper_towel': 'Recyclable', 'tissue': 'Recyclable', 'toilet_tissue': 'Recyclable'
}

def preprocess_image(image):
    """Preprocess image for model prediction"""
    img = image.resize(IMG_SIZE)
    img_array = np.array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    return img_array

def predict_waste(image):
    """Predict waste category using ImageNet features"""
    processed_img = preprocess_image(image)
    predictions = base_model.predict(processed_img)
    decoded = decode_predictions(predictions, top=5)[0]
    
    # Map ImageNet predictions to waste categories
    category_scores = {label: 0.0 for label in CLASS_LABELS}
    
    for _, class_name, score in decoded:
        class_lower = class_name.lower().replace('_', ' ')
        
        # Check direct mapping
        for key, waste_type in IMAGENET_TO_WASTE.items():
            if key in class_lower:
                category_scores[waste_type] += float(score) * 100
                break
        else:
            # Heuristic classification
            if any(word in class_lower for word in ['bottle', 'container', 'bag', 'wrapper']):
                category_scores['Plastic'] += float(score) * 50
            elif any(word in class_lower for word in ['can', 'screw', 'nail', 'wire']):
                category_scores['Metal'] += float(score) * 50
            elif any(word in class_lower for word in ['fruit', 'vegetable', 'food', 'plant']):
                category_scores['Organic'] += float(score) * 50
            elif any(word in class_lower for word in ['glass', 'jar', 'vase']):
                category_scores['Glass'] += float(score) * 50
            elif any(word in class_lower for word in ['paper', 'cardboard', 'book']):
                category_scores['Recyclable'] += float(score) * 50
            elif any(word in class_lower for word in ['syringe', 'medical', 'pill']):
                category_scores['Biomedical'] += float(score) * 50
            elif any(word in class_lower for word in ['battery', 'chemical', 'toxic']):
                category_scores['Hazardous'] += float(score) * 50
    
    # Normalize scores
    total = sum(category_scores.values())
    if total > 0:
        probabilities = {k: v for k, v in category_scores.items()}
    else:
        # Default distribution if no match
        probabilities = {label: 100/7 for label in CLASS_LABELS}
    
    category = max(probabilities, key=probabilities.get)
    confidence = probabilities[category]
    
    # Detailed waste info
    waste_details = {
        'Organic': {
            'disposal': 'Compost bin or organic waste collection',
            'decomposition': 'Biodegradable (2-6 months)',
            'environmental_impact': 'Low - Can be composted into nutrient-rich soil',
            'examples': ['Food scraps', 'Garden waste', 'Paper products', 'Wood'],
            'tips': 'Separate from other waste to enable composting',
            'color': '#4CAF50'
        },
        'Recyclable': {
            'disposal': 'Recycling bin (blue/green bin)',
            'decomposition': 'Non-biodegradable (100-1000 years)',
            'environmental_impact': 'Medium - Can be recycled to reduce resource consumption',
            'examples': ['Cardboard', 'Paper', 'Aluminum foil', 'Tetra packs'],
            'tips': 'Clean and dry before recycling for better processing',
            'color': '#2196F3'
        },
        'Plastic': {
            'disposal': 'Plastic recycling bin (check recycling codes)',
            'decomposition': 'Non-biodegradable (450-1000 years)',
            'environmental_impact': 'High - Major ocean pollutant, recycle or reduce usage',
            'examples': ['Bottles', 'Bags', 'Containers', 'Packaging', 'Straws'],
            'tips': 'Check recycling codes (1-7), avoid single-use plastics',
            'color': '#FF9800'
        },
        'Metal': {
            'disposal': 'Metal recycling bin or scrap collection',
            'decomposition': 'Non-biodegradable (50-500 years)',
            'environmental_impact': 'Medium - Highly recyclable, saves mining resources',
            'examples': ['Cans', 'Foil', 'Wire', 'Appliances', 'Tools'],
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
        'Hazardous': {
            'disposal': 'Special hazardous waste facility (DO NOT mix with regular waste)',
            'decomposition': 'Toxic - Never decomposes safely',
            'environmental_impact': 'CRITICAL - Extremely dangerous to environment and health',
            'examples': ['Batteries', 'Chemicals', 'Paint', 'Electronics', 'Pesticides'],
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
    
    return category, confidence, probabilities, waste_details.get(category, waste_details['Recyclable'])

@app.route('/')
def index():
    """Serve main page"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Handle image upload and prediction"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        image = Image.open(file.stream).convert('RGB')
        
        category, confidence, probabilities, details = predict_waste(image)
        
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
    """Handle base64 image from camera"""
    try:
        data = request.get_json()
        image_data = data['image'].split(',')[1]
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        category, confidence, probabilities, details = predict_waste(image)
        
        return jsonify({
            'category': category,
            'confidence': f'{confidence:.2f}%',
            'probabilities': probabilities,
            'details': details,
            'success': True
        })
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/camera_proxy')
def camera_proxy():
    """Proxy for IP camera to avoid CORS issues"""
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
