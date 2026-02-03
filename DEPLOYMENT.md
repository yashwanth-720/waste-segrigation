# Deployment Guide 🚀

This guide covers multiple deployment options for the AI Waste Segregation System.

## Prerequisites ✅

- Trained model file: `waste_segregation_model.h5`
- All dependencies installed
- Git repository (for cloud deployments)

---

## Option 1: Local Deployment (Development)

### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

Access at: `http://localhost:5000`

### Access from Mobile Devices (Same Network)
```bash
# Find your IP address
# Windows: ipconfig
# Linux/Mac: ifconfig

# Run with host binding
python app.py
```

Access from mobile: `http://YOUR_IP_ADDRESS:5000`

---

## Option 2: Heroku Deployment (Free Tier Available)

### Step 1: Install Heroku CLI
Download from: https://devcenter.heroku.com/articles/heroku-cli

### Step 2: Login and Create App
```bash
heroku login
heroku create your-waste-app-name
```

### Step 3: Add Buildpacks
```bash
heroku buildpacks:add --index 1 heroku/python
```

### Step 4: Deploy
```bash
git init
git add .
git commit -m "Initial commit"
git push heroku main
```

### Step 5: Open App
```bash
heroku open
```

**Note**: Upload your trained model to the repository before deploying.

---

## Option 3: AWS EC2 Deployment

### Step 1: Launch EC2 Instance
- Choose Ubuntu Server 20.04 LTS
- Instance type: t2.medium (minimum)
- Configure security group: Allow HTTP (80), HTTPS (443), Custom TCP (5000)

### Step 2: Connect to Instance
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### Step 3: Install Dependencies
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx -y

# Clone your repository
git clone your-repo-url
cd your-repo

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
pip install gunicorn
```

### Step 4: Run with Gunicorn
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
```

### Step 5: Setup Nginx (Optional)
```bash
sudo nano /etc/nginx/sites-available/waste-app

# Add configuration:
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/waste-app /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

### Step 6: Setup as Service (Keep Running)
```bash
sudo nano /etc/systemd/system/waste-app.service

# Add:
[Unit]
Description=Waste Segregation App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/your-repo
Environment="PATH=/home/ubuntu/your-repo/venv/bin"
ExecStart=/home/ubuntu/your-repo/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 app:app

[Install]
WantedBy=multi-user.target

# Start service
sudo systemctl start waste-app
sudo systemctl enable waste-app
```

---

## Option 4: Docker Deployment

### Step 1: Build Image
```bash
docker build -t waste-segregation .
```

### Step 2: Run Container
```bash
docker run -p 5000:5000 waste-segregation
```

### Step 3: Docker Compose (Optional)
Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./waste_segregation_model.h5:/app/waste_segregation_model.h5
    environment:
      - FLASK_ENV=production
```

Run:
```bash
docker-compose up -d
```

---

## Option 5: Google Cloud Platform (GCP)

### Using Cloud Run

1. **Install Google Cloud SDK**
```bash
gcloud init
```

2. **Build and Deploy**
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/waste-app
gcloud run deploy waste-app --image gcr.io/YOUR_PROJECT_ID/waste-app --platform managed
```

---

## Option 6: Azure Web App

### Step 1: Install Azure CLI
Download from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

### Step 2: Login and Deploy
```bash
az login
az webapp up --name your-waste-app --runtime "PYTHON:3.9"
```

---

## Option 7: DigitalOcean App Platform

1. Connect your GitHub repository
2. Select Python as runtime
3. Set build command: `pip install -r requirements.txt`
4. Set run command: `gunicorn --bind 0.0.0.0:8080 app:app`
5. Deploy

---

## Option 8: Vercel (Serverless)

Create `vercel.json`:
```json
{
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

Deploy:
```bash
npm i -g vercel
vercel
```

---

## Production Checklist ✅

Before deploying to production:

- [ ] Set `debug=False` in app.py
- [ ] Use environment variables for sensitive data
- [ ] Enable HTTPS/SSL
- [ ] Set up proper logging
- [ ] Configure CORS properly
- [ ] Add rate limiting
- [ ] Set up monitoring (e.g., Sentry)
- [ ] Optimize model size if needed
- [ ] Test on multiple devices
- [ ] Set up backup for model file
- [ ] Configure CDN for static files (optional)

---

## Environment Variables

Create `.env` file:
```
FLASK_ENV=production
MODEL_PATH=waste_segregation_model.h5
SECRET_KEY=your-secret-key
```

Update `app.py` to use:
```python
from dotenv import load_dotenv
load_dotenv()

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
```

---

## Performance Optimization 🚀

### 1. Model Optimization
```python
# Convert to TensorFlow Lite
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()
```

### 2. Caching
```python
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
```

### 3. Load Balancing
Use multiple workers with Gunicorn:
```bash
gunicorn --workers 4 --threads 2 app:app
```

---

## Monitoring & Logging

### Setup Logging
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### Use Sentry for Error Tracking
```bash
pip install sentry-sdk[flask]
```

```python
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

---

## Troubleshooting 🔧

### Issue: Model file too large for Git
**Solution**: Use Git LFS
```bash
git lfs install
git lfs track "*.h5"
git add .gitattributes
```

### Issue: Out of memory on server
**Solution**: 
- Use smaller model (MobileNetV2)
- Increase server RAM
- Use model quantization

### Issue: Slow predictions
**Solution**:
- Use TensorFlow Lite
- Enable GPU if available
- Reduce image size
- Use caching

---

## Cost Estimates 💰

| Platform | Free Tier | Paid (Monthly) |
|----------|-----------|----------------|
| Heroku | 550 hours | $7+ |
| AWS EC2 | 750 hours (1 year) | $10+ |
| GCP Cloud Run | 2M requests | $5+ |
| DigitalOcean | $0 | $5+ |
| Azure | $200 credit | $10+ |

---

## Support 📧

For deployment issues:
1. Check logs: `heroku logs --tail` or `docker logs container-id`
2. Verify all files are uploaded
3. Check environment variables
4. Ensure model file exists

---

**Happy Deploying! 🎉**
