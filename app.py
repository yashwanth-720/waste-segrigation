from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import tensorflow as tf
import numpy as np
import cv2
import base64
from PIL import Image
import io

app = Flask(__name__)
CORS(app)

# Load trained model
MODEL_PATH = 'waste_segregation_model.h5'
model = tf.keras.models.load_model(MODEL_PATH)

# Class labels
CLASS_LABELS = ['Organic', 'Recyclable']
IMG_SIZE = (224, 224)

def preprocess_image(image):
    """Preprocess image for model prediction"""
    img = image.resize(IMG_SIZE)
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def predict_waste(image):
    """Predict waste category"""
    processed_img = preprocess_image(image)
    predictions = model.predict(processed_img)
    class_idx = np.argmax(predictions[0])
    confidence = float(predictions[0][class_idx]) * 100
    return CLASS_LABELS[class_idx], confidence

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
        
        category, confidence = predict_waste(image)
        
        return jsonify({
            'category': category,
            'confidence': f'{confidence:.2f}%',
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
        
        category, confidence = predict_waste(image)
        
        return jsonify({
            'category': category,
            'confidence': f'{confidence:.2f}%',
            'success': True
        })
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

# Global variable for video stream
camera = None

def generate_frames():
    """Generate frames for live video stream with predictions"""
    global camera
    camera = cv2.VideoCapture(0)
    
    while True:
        success, frame = camera.read()
        if not success:
            break
        
        # Make prediction on frame
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)
        category, confidence = predict_waste(pil_image)
        
        # Draw prediction on frame
        color = (0, 255, 0) if category == 'Recyclable' else (0, 165, 255)
        cv2.putText(frame, f'{category}: {confidence:.1f}%', 
                    (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)
        
        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stop_camera')
def stop_camera():
    """Stop camera stream"""
    global camera
    if camera is not None:
        camera.release()
        camera = None
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
