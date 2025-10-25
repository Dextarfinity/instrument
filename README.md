# Musical Instrument Detection API - Cloud Deployment

This folder contains the cloud deployment version of the Musical Instrument Detection API using FastAPI and Railway.

## Features

- 🎵 Musical instrument detection using YOLO
- 🌐 CORS enabled for cross-origin requests
- 📱 Optimized for cloud deployment
- 🚀 Ready for Railway deployment
- 📊 Batch processing support (up to 10 images)
- 🔄 Health check endpoints
- 📋 Comprehensive error handling

## API Endpoints

- `GET /` - API information and available endpoints
- `GET /health` - Health check for monitoring
- `GET /model_info` - Information about the loaded model
- `POST /predict` - Single image prediction
- `POST /predict_batch` - Batch image prediction (max 10 images)
- `GET /docs` - Interactive API documentation

## Local Testing

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the API:
```bash
python main.py
```

3. Visit `http://localhost:8000/docs` for interactive documentation

## Railway Deployment

### Method 1: GitHub Integration (Recommended)

1. Push this folder to a GitHub repository
2. Connect your GitHub repo to Railway
3. Railway will automatically detect the configuration
4. Your API will be deployed and accessible via the Railway URL

### Method 2: Railway CLI

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Login to Railway:
```bash
railway login
```

3. Initialize and deploy:
```bash
railway init
railway up
```

### Method 3: Direct Deploy

1. Create a new Railway project
2. Upload this folder to Railway
3. Railway will automatically build and deploy

## Environment Variables

Railway will automatically set the `PORT` environment variable. No additional configuration needed.

## Model Management

The API will try to:
1. Load a local model file (yolo11n.pt or yolov8s.pt)
2. If no local model is found, download yolo11n.pt automatically

## Usage Examples

### Single Image Prediction

```python
import requests

url = "YOUR_RAILWAY_URL/predict"
files = {"file": open("image.jpg", "rb")}
response = requests.post(url, files=files)
result = response.json()
```

### Batch Prediction

```python
import requests

url = "YOUR_RAILWAY_URL/predict_batch"
files = [
    ("files", open("image1.jpg", "rb")),
    ("files", open("image2.jpg", "rb"))
]
response = requests.post(url, files=files)
result = response.json()
```

### JavaScript/Web Usage

```javascript
// Single image
const formData = new FormData();
formData.append('file', imageFile);

fetch('YOUR_RAILWAY_URL/predict', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

## Response Format

### Single Prediction Response

```json
{
  "success": true,
  "filename": "image.jpg",
  "image_size": {"width": 640, "height": 480},
  "predictions": [
    {
      "class_name": "guitar",
      "class_id": 0,
      "confidence": 0.8521,
      "bbox": {
        "x1": 100.5,
        "y1": 150.2,
        "x2": 300.8,
        "y2": 400.1,
        "width": 200.3,
        "height": 249.9
      }
    }
  ],
  "count": 1
}
```

## Monitoring

Use the `/health` endpoint for monitoring:

```bash
curl YOUR_RAILWAY_URL/health
```

Response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "service": "musical-instrument-detection",
  "version": "1.0.0"
}
```

## Security Notes

- CORS is currently set to allow all origins (`*`) for development
- For production, update the CORS settings in `main.py` to specific domains
- Consider adding authentication for production use

## Troubleshooting

1. **Model not loading**: Check Railway logs for model download/loading errors
2. **Memory issues**: Consider using a smaller YOLO model (yolo11n.pt instead of yolo11x.pt)
3. **Timeout errors**: Increase Railway's timeout settings for large image processing

## Railway Configuration

The included files handle Railway deployment:
- `requirements.txt`: Python dependencies
- `Procfile`: Start command for Railway
- `railway.json`: Railway-specific configuration

Railway will automatically:
- Install Python dependencies
- Build the application
- Start the FastAPI server
- Provide a public URL for access