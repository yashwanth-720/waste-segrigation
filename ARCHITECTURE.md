# 🏗️ System Architecture & Flow Diagrams

## 📊 Overall System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE (Browser)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Upload     │  │    Camera    │  │     Live     │     │
│  │    Image     │  │   Capture    │  │  Detection   │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          │   HTTP/AJAX      │   WebRTC        │   Video Stream
          │                  │                  │
┌─────────▼──────────────────▼──────────────────▼─────────────┐
│                    FLASK WEB SERVER                          │
│  ┌────────────────────────────────────────────────────┐     │
│  │              API ENDPOINTS                          │     │
│  │  • /predict (Upload)                               │     │
│  │  • /predict_base64 (Camera)                        │     │
│  │  • /video_feed (Live Stream)                       │     │
│  └────────────────┬───────────────────────────────────┘     │
└───────────────────┼─────────────────────────────────────────┘
                    │
                    │   Image Processing
                    │
┌───────────────────▼─────────────────────────────────────────┐
│              IMAGE PREPROCESSING                             │
│  • Resize to 224x224                                        │
│  • Normalize (0-1)                                          │
│  • Convert to array                                         │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    │   Preprocessed Image
                    │
┌───────────────────▼─────────────────────────────────────────┐
│              CNN MODEL (EfficientNetB3)                      │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Input Layer (224x224x3)                          │     │
│  │         ↓                                          │     │
│  │  EfficientNetB3 (Pre-trained)                     │     │
│  │         ↓                                          │     │
│  │  GlobalAveragePooling2D                           │     │
│  │         ↓                                          │     │
│  │  Dense Layer (256 neurons)                        │     │
│  │         ↓                                          │     │
│  │  Output Layer (2 classes)                         │     │
│  │         ↓                                          │     │
│  │  [Organic, Recyclable]                            │     │
│  └────────────────────────────────────────────────────┘     │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    │   Predictions
                    │
┌───────────────────▼─────────────────────────────────────────┐
│              RESULT PROCESSING                               │
│  • Get class with highest probability                       │
│  • Calculate confidence percentage                          │
│  • Format response                                          │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    │   JSON Response
                    │
┌───────────────────▼─────────────────────────────────────────┐
│              DISPLAY RESULTS                                 │
│  • Category: Organic / Recyclable                           │
│  • Confidence: XX.XX%                                       │
│  • Icon & Description                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow - Upload Mode

```
User Selects Image
       ↓
JavaScript reads file
       ↓
Display preview
       ↓
User clicks "Analyze"
       ↓
FormData created
       ↓
POST to /predict
       ↓
Flask receives file
       ↓
Open with PIL
       ↓
Preprocess image
       ↓
Model prediction
       ↓
Get class & confidence
       ↓
Return JSON response
       ↓
JavaScript displays result
       ↓
Show category, confidence, icon
```

---

## 📸 Data Flow - Camera Mode

```
User clicks "Start Camera"
       ↓
Request camera permission
       ↓
getUserMedia() API
       ↓
Video stream to <video> element
       ↓
User clicks "Capture"
       ↓
Draw video frame to canvas
       ↓
Convert canvas to base64
       ↓
Display captured image
       ↓
POST base64 to /predict_base64
       ↓
Flask decodes base64
       ↓
Convert to PIL Image
       ↓
Preprocess & predict
       ↓
Return JSON response
       ↓
Display results
```

---

## 🎥 Data Flow - Live Detection Mode

```
User clicks "Start Live Detection"
       ↓
Request /video_feed endpoint
       ↓
Flask opens camera (cv2.VideoCapture)
       ↓
Continuous loop:
  ├─ Read frame from camera
  ├─ Convert BGR to RGB
  ├─ Create PIL Image
  ├─ Preprocess image
  ├─ Model prediction
  ├─ Get category & confidence
  ├─ Draw text on frame
  ├─ Encode frame as JPEG
  └─ Yield frame to stream
       ↓
Browser displays video stream
       ↓
Real-time classification overlay
```

---

## 🧠 Model Training Flow

```
Dataset Preparation
       ↓
Load images from folders
       ↓
Apply data augmentation
  • Rotation
  • Zoom
  • Flip
  • Shift
       ↓
Split: Train/Valid/Test
       ↓
Load EfficientNetB3
       ↓
Freeze early layers
       ↓
Add custom layers
       ↓
Compile model
       ↓
Training loop (50 epochs)
  ├─ Forward pass
  ├─ Calculate loss
  ├─ Backpropagation
  ├─ Update weights
  └─ Validate
       ↓
Save best model
       ↓
Evaluate on test set
       ↓
Save final model (.h5)
```

---

## 🌐 Deployment Architecture

### Local Development
```
┌──────────────┐
│   Browser    │
│ localhost:5000│
└──────┬───────┘
       │
┌──────▼───────┐
│ Flask Server │
│  (Python)    │
└──────┬───────┘
       │
┌──────▼───────┐
│  CNN Model   │
│   (.h5)      │
└──────────────┘
```

### Production (Heroku)
```
┌──────────────┐
│   Browser    │
│ yourapp.com  │
└──────┬───────┘
       │ HTTPS
┌──────▼───────┐
│    Heroku    │
│   Dyno       │
│ ┌──────────┐ │
│ │ Gunicorn │ │
│ └────┬─────┘ │
│ ┌────▼─────┐ │
│ │  Flask   │ │
│ └────┬─────┘ │
│ ┌────▼─────┐ │
│ │   Model  │ │
│ └──────────┘ │
└──────────────┘
```

### Production (AWS EC2)
```
┌──────────────┐
│   Browser    │
│ yourapp.com  │
└──────┬───────┘
       │ HTTPS
┌──────▼───────┐
│    Nginx     │
│ (Port 80)    │
└──────┬───────┘
       │
┌──────▼───────┐
│  Gunicorn    │
│ (Port 5000)  │
└──────┬───────┘
       │
┌──────▼───────┐
│    Flask     │
└──────┬───────┘
       │
┌──────▼───────┐
│  CNN Model   │
└──────────────┘
```

---

## 📁 File Interaction Diagram

```
User Request
     ↓
┌────────────────┐
│   index.html   │ ← Main webpage
└────┬───────────┘
     │ loads
     ├─→ style.css    (Styling)
     └─→ script.js    (Logic)
          ↓
     User interaction
          ↓
     AJAX request
          ↓
┌────────────────┐
│     app.py     │ ← Flask backend
└────┬───────────┘
     │ imports
     ├─→ config.py    (Settings)
     │
     │ loads
     ├─→ waste_segregation_model.h5
     │
     │ uses
     ├─→ tensorflow
     ├─→ opencv
     └─→ PIL
          ↓
     Process & predict
          ↓
     Return JSON
          ↓
     script.js displays
```

---

## 🔐 Security Flow

```
User Upload
     ↓
File validation
  • Check file type
  • Check file size
     ↓
CORS check
     ↓
Process image
     ↓
Sanitize output
     ↓
Return safe JSON
```

---

## 📊 Performance Optimization

```
Request arrives
     ↓
Check cache (future)
     ↓
Load model (once)
     ↓
Preprocess (optimized)
     ↓
Batch prediction (if multiple)
     ↓
Return result
     ↓
Cache result (future)
```

---

## 🎯 Component Interaction

```
┌─────────────────────────────────────────────┐
│           Frontend (Browser)                 │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐    │
│  │  HTML   │  │   CSS   │  │   JS    │    │
│  └────┬────┘  └────┬────┘  └────┬────┘    │
└───────┼────────────┼────────────┼──────────┘
        │            │            │
        └────────────┴────────────┘
                     │
        ┌────────────▼────────────┐
        │      HTTP/AJAX          │
        └────────────┬────────────┘
                     │
┌────────────────────▼─────────────────────────┐
│           Backend (Flask)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Routes  │  │ Business │  │   Model  │  │
│  │          │→ │  Logic   │→ │  Layer   │  │
│  └──────────┘  └──────────┘  └──────────┘  │
└───────────────────────────────────────────────┘
```

---

## 🚀 Scaling Strategy

```
Single Server
     ↓
Add Load Balancer
     ↓
Multiple App Servers
     ↓
Separate Model Server
     ↓
Add Caching Layer
     ↓
CDN for Static Files
     ↓
Database for Results
```

---

## 📈 Monitoring Flow

```
User Request
     ↓
Log request
     ↓
Process
     ↓
Log response time
     ↓
Log accuracy
     ↓
Send to monitoring
  • Sentry (errors)
  • CloudWatch (metrics)
  • Custom dashboard
```

---

This architecture ensures:
✅ High performance
✅ Scalability
✅ Maintainability
✅ Security
✅ Easy deployment
