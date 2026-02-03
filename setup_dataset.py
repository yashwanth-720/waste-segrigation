import os
import urllib.request
import zipfile
from pathlib import Path

def create_dataset_structure():
    """Create dataset folder structure"""
    folders = [
        'dataset/train/Organic',
        'dataset/train/Recyclable',
        'dataset/valid/Organic',
        'dataset/valid/Recyclable',
        'dataset/test/Organic',
        'dataset/test/Recyclable'
    ]
    
    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)
    
    print("✅ Dataset folder structure created!")

def download_sample_dataset():
    """
    Download a sample waste dataset
    Note: You can replace this with your preferred dataset
    """
    print("📥 To download a dataset, please visit:")
    print("1. Kaggle: https://www.kaggle.com/datasets/techsash/waste-classification-data")
    print("2. TrashNet: https://github.com/garythung/trashnet")
    print("\nAfter downloading, organize images into the dataset folders:")
    print("- dataset/train/Organic/")
    print("- dataset/train/Recyclable/")
    print("- dataset/valid/Organic/")
    print("- dataset/valid/Recyclable/")
    print("- dataset/test/Organic/")
    print("- dataset/test/Recyclable/")

if __name__ == "__main__":
    print("🗂️  Setting up dataset structure...")
    create_dataset_structure()
    print("\n" + "="*50)
    download_sample_dataset()
    print("="*50)
    print("\n✨ Setup complete! Add your images to the dataset folders.")
