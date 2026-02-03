let uploadedFiles = [];
let cameraConnected = false;

// Tab switching
function showTab(tabName) {
    const tabs = document.querySelectorAll('.tab-content');
    const buttons = document.querySelectorAll('.tab-btn');
    
    tabs.forEach(tab => tab.classList.remove('active'));
    buttons.forEach(btn => btn.classList.remove('active'));
    
    document.getElementById(tabName).classList.add('active');
    event.target.closest('.tab-btn').classList.add('active');
    
    document.getElementById('results').style.display = 'none';
}

// Drag and Drop
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');

dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    handleFiles(Array.from(e.dataTransfer.files));
});

fileInput.addEventListener('change', (e) => {
    handleFiles(Array.from(e.target.files));
});

function handleFiles(files) {
    uploadedFiles = files.filter(file => file.type.startsWith('image/'));
    displayUploadedFiles();
}

function displayUploadedFiles() {
    const preview = document.getElementById('uploadPreview');
    preview.innerHTML = '';
    
    uploadedFiles.forEach((file, index) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const item = document.createElement('div');
            item.className = 'preview-item';
            item.innerHTML = `
                <img src="${e.target.result}" alt="Preview">
                <div class="preview-actions">
                    <span>${file.name}</span>
                    <button class="btn-analyze" onclick="analyzeFile(${index})">
                        <i class="fas fa-search"></i> Analyze
                    </button>
                </div>
            `;
            preview.appendChild(item);
        };
        reader.readAsDataURL(file);
    });
}

async function analyzeFile(index) {
    const file = uploadedFiles[index];
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showLoading();
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        hideLoading();
        
        if (result.success) {
            displayResults(result);
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        hideLoading();
        alert('Error: ' + error.message);
    }
}

// Optimized IP Camera - Zero Lag
function connectIPCamera() {
    const url = document.getElementById('ipCameraUrl').value.trim();
    if (!url) {
        alert('Please enter IP camera URL');
        return;
    }
    
    const img = document.getElementById('cameraStream');
    
    img.onload = () => {
        cameraConnected = true;
        // Immediately load next frame for smooth video
        if (cameraConnected) {
            img.src = url + (url.includes('?') ? '&' : '?') + 't=' + Date.now();
        }
    };
    
    img.onerror = () => {
        alert('❌ Cannot connect to camera.\n\nTroubleshooting:\n1. Check URL format (e.g., http://192.168.1.100:8080/shot.jpg)\n2. Ensure phone and PC are on same WiFi\n3. Camera app is running\n4. Try /shot.jpg or /video for IP Webcam app');
        cameraConnected = false;
    };
    
    img.style.display = 'block';
    img.src = url + (url.includes('?') ? '&' : '?') + 't=' + Date.now();
}

function disconnectCamera() {
    cameraConnected = false;
    const img = document.getElementById('cameraStream');
    img.onload = null;
    img.onerror = null;
    img.style.display = 'none';
    img.src = '';
}

function captureImage() {
    if (!cameraConnected) {
        alert('Please connect to camera first');
        return;
    }
    
    const img = document.getElementById('cameraStream');
    const canvas = document.getElementById('canvas');
    
    canvas.width = img.naturalWidth || 640;
    canvas.height = img.naturalHeight || 480;
    
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    
    const imageData = canvas.toDataURL('image/jpeg', 0.7);
    
    const preview = document.getElementById('cameraPreview');
    preview.innerHTML = `
        <div class="preview-item">
            <img src="${imageData}" alt="Captured">
            <div class="preview-actions">
                <span>Captured Image</span>
            </div>
        </div>
    `;
    
    predictFromCamera(imageData);
}

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
            displayResults(result);
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        hideLoading();
        alert('Error: ' + error.message);
    }
}

let chartInstance = null;

function displayResults(result) {
    const { category, confidence, probabilities, details } = result;
    const resultsDiv = document.getElementById('results');
    const icon = document.getElementById('resultIcon');
    const categoryEl = document.getElementById('resultCategory');
    const confidenceEl = document.getElementById('resultConfidence');
    const confidenceFill = document.getElementById('confidenceFill');
    
    const confidenceValue = parseFloat(confidence);
    
    // Set icon and category
    icon.innerHTML = category === 'Organic' ? '🌱' : '♻️';
    categoryEl.textContent = category;
    confidenceEl.textContent = confidence;
    confidenceFill.style.width = confidenceValue + '%';
    
    // Display detailed info
    document.getElementById('disposal').textContent = details.disposal;
    document.getElementById('decomposition').textContent = details.decomposition;
    document.getElementById('impact').textContent = details.environmental_impact;
    document.getElementById('tips').textContent = details.tips;
    
    // Display examples
    const examplesDiv = document.getElementById('examples');
    examplesDiv.innerHTML = details.examples.map(ex => 
        `<span class="example-tag">${ex}</span>`
    ).join('');
    
    // Create probability chart
    createProbabilityChart(probabilities);
    
    resultsDiv.style.display = 'block';
    resultsDiv.scrollIntoView({ behavior: 'smooth' });
}

function createProbabilityChart(probabilities) {
    const ctx = document.getElementById('probabilityChart').getContext('2d');
    
    // Destroy previous chart if exists
    if (chartInstance) {
        chartInstance.destroy();
    }
    
    const labels = Object.keys(probabilities);
    const data = Object.values(probabilities);
    
    chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Probability (%)',
                data: data,
                backgroundColor: [
                    'rgba(102, 126, 234, 0.8)',
                    'rgba(118, 75, 162, 0.8)'
                ],
                borderColor: [
                    'rgba(102, 126, 234, 1)',
                    'rgba(118, 75, 162, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.parsed.y.toFixed(2) + '%';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        },
                        color: 'rgba(255, 255, 255, 0.8)'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.8)'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    });
}

function showLoading() {
    document.body.style.cursor = 'wait';
}

function hideLoading() {
    document.body.style.cursor = 'default';
}

window.addEventListener('beforeunload', () => {
    disconnectCamera();
});
