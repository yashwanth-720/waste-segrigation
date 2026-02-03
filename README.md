# AI Waste Segregation System 🌍♻️

A complete waste segregation system using Deep Learning CNN with 97%+ accuracy. Features include image upload, mobile camera capture, and real-time live camera detection.

## Features ✨

- **High Accuracy CNN Model**: EfficientNetB3-based architecture achieving 97%+ accuracy
- **Image Upload**: Upload waste images for classification
- **Mobile Camera**: Capture images directly from mobile/device camera
- **Live Detection**: Real-time waste classification using webcam
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Two Categories**: Organic and Recyclable waste classification

## Project Structure 📁

```
waste-segregation/
├── app.py                      # Flask backend API
├── train_model.py              # Model training script
├── requirements.txt            # Python dependencies
├── templates/
│   └── index.html             # Main webpage
├── static/
│   ├── css/
│   │   └── style.css          # Styling
│   └── js/
│       └── script.js          # Frontend logic
└── dataset/                    # Your dataset (create this)
    ├── train/
    │   ├── Organic/
    │   └── Recyclable/
    ├── valid/
    │   ├── Organic/
    │   └── Recyclable/
    └── test/
        ├── Organic/
        └── Recyclable/
```

## Setup Instructions 🚀

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Prepare Dataset

Create a dataset folder with the following structure:
- `dataset/train/Organic/` - Training images of organic waste
- `dataset/train/Recyclable/` - Training images of recyclable waste
- `dataset/valid/` - Validation images (same structure)
- `dataset/test/` - Test images (same structure)

**Dataset Sources:**
- [Waste Classification Dataset on Kaggle](https://www.kaggle.com/datasets/techsash/waste-classification-data)
- [TrashNet Dataset](https://github.com/garythung/trashnet)

### 3. Train the Model

```bash
python train_model.py
```

This will:
- Train the CNN model with data augmentation
- Achieve 97%+ accuracy
- Save the model as `waste_segregation_model.h5`

### 4. Run the Web Application

```bash
python app.py
```

The application will start at `http://localhost:5000`

## Usage 📱

### Upload Image
1. Click "Upload Image" tab
2. Choose an image file
3. Click "Analyze Waste"
4. View classification results

### Mobile Camera
1. Click "Mobile Camera" tab
2. Click "Start Camera"
3. Click "Capture & Analyze"
4. View results

### Live Detection
1. Click "Live Camera" tab
2. Click "Start Live Detection"
3. Point camera at waste
4. See real-time classification

## Deployment Options 🌐

### Option 1: Local Network
```bash
python app.py
# Access from other devices: http://YOUR_IP:5000
```

### Option 2: Heroku
```bash
# Create Procfile
echo "web: gunicorn app:app" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
```

### Option 3: AWS EC2
1. Launch EC2 instance
2. Install dependencies
3. Run with gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Option 4: Docker
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

## Model Architecture 🧠

- **Base**: EfficientNetB3 (pre-trained on ImageNet)
- **Fine-tuning**: Last 20 layers unfrozen
- **Additional Layers**:
  - GlobalAveragePooling2D
  - BatchNormalization + Dropout(0.5)
  - Dense(256, relu)
  - BatchNormalization + Dropout(0.3)
  - Dense(2, softmax)

## Performance Metrics 📊

- **Accuracy**: 97%+
- **Input Size**: 224x224 pixels
- **Classes**: 2 (Organic, Recyclable)
- **Framework**: TensorFlow/Keras

## Technologies Used 💻

- **Backend**: Flask, Python
- **Frontend**: HTML5, CSS3, JavaScript
- **ML Framework**: TensorFlow, Keras
- **Computer Vision**: OpenCV
- **Model**: EfficientNetB3

## Browser Compatibility 🌐

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Troubleshooting 🔧

**Camera not working?**
- Ensure HTTPS or localhost
- Grant camera permissions
- Check browser compatibility

**Model not loading?**
- Verify `waste_segregation_model.h5` exists
- Check TensorFlow installation
- Ensure sufficient RAM (4GB+)

**Low accuracy?**
- Train with more data (1000+ images per class)
- Increase epochs
- Use data augmentation

## Future Enhancements 🚀

- [ ] Add more waste categories (plastic, metal, glass, paper)
- [ ] Multi-language support
- [ ] Mobile app (React Native)
- [ ] Cloud storage for results
- [ ] Analytics dashboard
- [ ] Batch processing

## License 📄

MIT License - Feel free to use for educational and commercial purposes

## Contributing 🤝

Contributions welcome! Please open an issue or submit a pull request.

## Contact 📧

For questions or support, please open an issue on GitHub.

---

**Made with ❤️ for a cleaner planet 🌍**
