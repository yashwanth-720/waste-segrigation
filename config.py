# Configuration file for Waste Segregation System

# Model Configuration
MODEL_CONFIG = {
    'img_size': (224, 224),
    'batch_size': 32,
    'epochs': 50,
    'learning_rate': 0.0001,
    'model_path': 'waste_segregation_model.h5'
}

# Class Labels
CLASS_LABELS = ['Organic', 'Recyclable']

# Dataset Paths
DATASET_CONFIG = {
    'train_dir': 'dataset/train',
    'valid_dir': 'dataset/valid',
    'test_dir': 'dataset/test'
}

# Server Configuration
SERVER_CONFIG = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': True
}

# Camera Configuration
CAMERA_CONFIG = {
    'default_camera': 0,  # 0 for default camera
    'frame_width': 640,
    'frame_height': 480
}

# Waste Categories Information
WASTE_INFO = {
    'Organic': {
        'icon': '🌱',
        'description': 'This waste is Organic. It should be composted or disposed in organic waste bins. Examples: food scraps, garden waste, paper.',
        'color': '#4CAF50'
    },
    'Recyclable': {
        'icon': '♻️',
        'description': 'This waste is Recyclable. Please dispose in recycling bins. Examples: plastic bottles, metal cans, glass, cardboard.',
        'color': '#2196F3'
    }
}
