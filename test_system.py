import os
import sys
import requests
from PIL import Image
import io

def test_system():
    """Test the waste segregation system"""
    
    print("="*50)
    print("  Waste Segregation System - Test Suite")
    print("="*50)
    print()
    
    # Test 1: Check if model exists
    print("Test 1: Checking model file...")
    if os.path.exists('waste_segregation_model.h5'):
        print("✅ Model file found!")
    else:
        print("❌ Model file not found. Please train the model first.")
        print("   Run: python train_model.py")
        return False
    
    # Test 2: Check dependencies
    print("\nTest 2: Checking dependencies...")
    try:
        import tensorflow as tf
        import flask
        import cv2
        import numpy as np
        print("✅ All dependencies installed!")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    # Test 3: Check folder structure
    print("\nTest 3: Checking folder structure...")
    required_folders = ['templates', 'static', 'static/css', 'static/js']
    all_exist = True
    for folder in required_folders:
        if os.path.exists(folder):
            print(f"✅ {folder}/ exists")
        else:
            print(f"❌ {folder}/ missing")
            all_exist = False
    
    if not all_exist:
        return False
    
    # Test 4: Check required files
    print("\nTest 4: Checking required files...")
    required_files = [
        'app.py',
        'templates/index.html',
        'static/css/style.css',
        'static/js/script.js'
    ]
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            all_exist = False
    
    if not all_exist:
        return False
    
    # Test 5: Try loading model
    print("\nTest 5: Loading model...")
    try:
        model = tf.keras.models.load_model('waste_segregation_model.h5')
        print("✅ Model loaded successfully!")
        print(f"   Input shape: {model.input_shape}")
        print(f"   Output shape: {model.output_shape}")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False
    
    print("\n" + "="*50)
    print("  All tests passed! ✅")
    print("="*50)
    print("\nYou can now run the application:")
    print("  python app.py")
    print("\nOr use the quick start script:")
    print("  start.bat (Windows)")
    print()
    
    return True

def test_api_endpoint():
    """Test if the API is running"""
    print("\n" + "="*50)
    print("  Testing API Endpoints")
    print("="*50)
    
    base_url = "http://localhost:5000"
    
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("✅ Server is running!")
            print(f"   Status: {response.status_code}")
        else:
            print(f"⚠️  Server responded with status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running")
        print("   Start the server with: python app.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("\n🧪 Starting system tests...\n")
    
    if test_system():
        print("\n🎉 System is ready to use!")
        
        # Ask if user wants to test API
        test_api = input("\nIs the server running? Test API endpoints? (y/n): ")
        if test_api.lower() == 'y':
            test_api_endpoint()
    else:
        print("\n❌ System check failed. Please fix the issues above.")
        sys.exit(1)
