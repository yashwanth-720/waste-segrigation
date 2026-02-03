let currentStream = null;
let uploadedImage = null;

// Tab switching
function showTab(tabName) {
    const tabs = document.querySelectorAll('.tab-content');
    const buttons = document.querySelectorAll('.tab-btn');
    
    tabs.forEach(tab => tab.classList.remove('active'));
    buttons.forEach(btn => btn.classList.remove('active'));
    
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
    
    // Hide results when switching tabs
    document.getElementById('results').style.display = 'none';
}

// Upload Image Handler
function handleFileUpload(event) {
    const file = event.target.files[0];
    if (file) {
        uploadedImage = file;
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('uploadPreview');
            preview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
            document.getElementById('uploadSubmit').style.display = 'inline-block';
        };
        reader.readAsDataURL(file);
    }
}

// Predict from uploaded image
async function predictUpload() {
    if (!uploadedImage) return;
    
    const formData = new FormData();
    formData.append('file', uploadedImage);
    
    try {
        showLoading();
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        hideLoading();
        
        if (result.success) {
            displayResults(result.category, result.confidence);
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        hideLoading();
        alert('Error processing image: ' + error);
    }
}

// Start mobile camera
async function startCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { facingMode: 'environment' } 
        });
        currentStream = stream;
        const video = document.getElementById('cameraStream');
        video.srcObject = stream;
        video.style.display = 'block';
    } catch (error) {
        alert('Error accessing camera: ' + error);
    }
}

// Capture image from camera
function captureImage() {
    const video = document.getElementById('cameraStream');
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0);
    
    const imageData = canvas.toDataURL('image/jpeg');
    
    // Display captured image
    const preview = document.getElementById('cameraPreview');
    preview.innerHTML = `<img src="${imageData}" alt="Captured">`;
    
    // Send for prediction
    predictFromCamera(imageData);
}

// Predict from camera capture
async function predictFromCamera(imageData) {
    try {
        showLoading();
        const response = await fetch('/predict_base64', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ image: imageData })
        });
        
        const result = await response.json();
        hideLoading();
        
        if (result.success) {
            displayResults(result.category, result.confidence);
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        hideLoading();
        alert('Error processing image: ' + error);
    }
}

// Stop camera
function stopCamera() {
    if (currentStream) {
        currentStream.getTracks().forEach(track => track.stop());
        currentStream = null;
        document.getElementById('cameraStream').style.display = 'none';
    }
}

// Start live stream
function startLiveStream() {
    const img = document.getElementById('liveStream');
    img.src = '/video_feed';
    img.style.display = 'block';
}

// Stop live stream
async function stopLiveStream() {
    const img = document.getElementById('liveStream');
    img.style.display = 'none';
    img.src = '';
    
    try {
        await fetch('/stop_camera');
    } catch (error) {
        console.error('Error stopping camera:', error);
    }
}

// Display results
function displayResults(category, confidence) {
    const resultsDiv = document.getElementById('results');
    const icon = document.getElementById('resultIcon');
    const categoryEl = document.getElementById('resultCategory');
    const confidenceEl = document.getElementById('resultConfidence');
    const descriptionEl = document.getElementById('resultDescription');
    
    // Set icon and description based on category
    if (category === 'Organic') {
        icon.innerHTML = '🌱';
        descriptionEl.innerHTML = 'This waste is <strong>Organic</strong>. It should be composted or disposed in organic waste bins. Examples: food scraps, garden waste, paper.';
    } else if (category === 'Recyclable') {
        icon.innerHTML = '♻️';
        descriptionEl.innerHTML = 'This waste is <strong>Recyclable</strong>. Please dispose in recycling bins. Examples: plastic bottles, metal cans, glass, cardboard.';
    }
    
    categoryEl.textContent = category;
    confidenceEl.textContent = confidence;
    resultsDiv.style.display = 'block';
    
    // Scroll to results
    resultsDiv.scrollIntoView({ behavior: 'smooth' });
}

// Loading indicator
function showLoading() {
    // Simple loading implementation
    document.body.style.cursor = 'wait';
}

function hideLoading() {
    document.body.style.cursor = 'default';
}

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    stopCamera();
    stopLiveStream();
});
