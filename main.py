from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import numpy as np
from ultralytics import YOLO
import io
from PIL import Image
import os
import sys
from typing import List

app = FastAPI(
    title="Musical Instrument Detection API - Cloud",
    description="Cloud deployment for YOLO musical instrument detection using Railway",
    version="1.0.0"
)

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable for model
model = None

def load_model():
    """Load the YOLO model"""
    global model
    try:
        # Try to load model from different possible paths (prioritize custom trained model)
        model_paths = [
            "best.pt",  # Custom trained model (PRIORITY)
            "last.pt",  # Last checkpoint of custom model
            os.path.join("runs", "detect", "musical_instrument_10x_aug", "weights", "best.pt"),
            "./best.pt",
            "./last.pt",
            os.path.join(os.getcwd(), "best.pt"),
            os.path.join(os.getcwd(), "last.pt"),
            "yolov8s.pt",  # Base model fallback
            "yolo11n.pt",
            "./yolo11n.pt",
            "./yolov8s.pt",
            os.path.join(os.getcwd(), "yolo11n.pt"),
            os.path.join(os.getcwd(), "yolov8s.pt")
        ]
        
        for path in model_paths:
            if os.path.exists(path):
                model = YOLO(path)
                print(f"Model loaded successfully from: {path}")
                if hasattr(model, 'names'):
                    print(f"Model classes: {list(model.names.values())}")
                return True
        
        # If no local model found, try to download a default model
        print("No local model found, downloading yolo11n.pt...")
        model = YOLO("yolo11n.pt")  # This will download if not present
        print("Model downloaded and loaded successfully")
        return True
        
    except Exception as e:
        print(f"Error loading model: {e}")
        return False

# Load model on startup
model_loaded = load_model()

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    global model_loaded
    if not model_loaded:
        model_loaded = load_model()
    print(f"Application started. Model loaded: {model_loaded}")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Musical Instrument Detection API - Cloud Version",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "single_prediction": "/predict",
            "batch_prediction": "/predict_batch",
            "model_info": "/model_info"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "service": "musical-instrument-detection",
        "version": "1.0.0"
    }

@app.get("/model_info")
async def model_info():
    """Get information about the loaded model"""
    if model is None:
        return {"error": "Model not loaded"}
    
    try:
        return {
            "model_type": "YOLO",
            "classes": model.names if hasattr(model, 'names') else "Unknown",
            "input_size": "Dynamic",
            "framework": "Ultralytics"
        }
    except Exception as e:
        return {"error": f"Error getting model info: {str(e)}"}

@app.post("/predict")
async def predict_image(file: UploadFile = File(...)):
    """
    Predict musical instruments in an uploaded image
    Returns predictions with bounding boxes and confidence scores
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not available. Please check model loading.")
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image (JPEG, PNG, etc.)")
    
    try:
        # Read and process image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert PIL image to numpy array
        image_np = np.array(image)
        
        # Run inference with 40% confidence threshold
        results = model(image_np, conf=0.40)
        
        # Process results
        predictions = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    confidence = box.conf[0].item()
                    class_id = int(box.cls[0].item())
                    
                    # Get class name safely
                    class_name = "unknown"
                    if hasattr(model, 'names') and class_id in model.names:
                        class_name = model.names[class_id]
                    
                    predictions.append({
                        "class_name": class_name,
                        "class_id": class_id,
                        "confidence": round(confidence, 4),
                        "bbox": {
                            "x1": round(x1, 2),
                            "y1": round(y1, 2),
                            "x2": round(x2, 2),
                            "y2": round(y2, 2),
                            "width": round(x2 - x1, 2),
                            "height": round(y2 - y1, 2)
                        }
                    })
        
        return {
            "success": True,
            "filename": file.filename,
            "image_size": {
                "width": image.width,
                "height": image.height
            },
            "predictions": predictions,
            "count": len(predictions),
            "processing_time": "N/A"  # Could add timing if needed
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.post("/predict_batch")
async def predict_batch(files: List[UploadFile] = File(...)):
    """
    Predict musical instruments in multiple uploaded images
    Returns predictions for each image
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not available. Please check model loading.")
    
    if len(files) > 10:  # Limit batch size for cloud deployment
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed per batch")
    
    results = []
    
    for file in files:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            results.append({
                "filename": file.filename,
                "success": False,
                "error": "File must be an image"
            })
            continue
        
        try:
            # Read and process image
            contents = await file.read()
            image = Image.open(io.BytesIO(contents))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert PIL image to numpy array
            image_np = np.array(image)
            
            # Run inference with 40% confidence threshold
            model_results = model(image_np, conf=0.40)
            
            # Process results
            predictions = []
            for result in model_results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        confidence = box.conf[0].item()
                        class_id = int(box.cls[0].item())
                        
                        # Get class name safely
                        class_name = "unknown"
                        if hasattr(model, 'names') and class_id in model.names:
                            class_name = model.names[class_id]
                        
                        predictions.append({
                            "class_name": class_name,
                            "class_id": class_id,
                            "confidence": round(confidence, 4),
                            "bbox": {
                                "x1": round(x1, 2),
                                "y1": round(y1, 2),
                                "x2": round(x2, 2),
                                "y2": round(y2, 2),
                                "width": round(x2 - x1, 2),
                                "height": round(y2 - y1, 2)
                            }
                        })
            
            results.append({
                "filename": file.filename,
                "success": True,
                "image_size": {
                    "width": image.width,
                    "height": image.height
                },
                "predictions": predictions,
                "count": len(predictions)
            })
            
        except Exception as e:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": f"Error processing image: {str(e)}"
            })
    
    return {
        "success": True,
        "results": results,
        "total_files": len(files),
        "processed_files": len([r for r in results if r.get("success", False)])
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "available_endpoints": ["/", "/health", "/predict", "/predict_batch", "/docs"]}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "message": str(exc)}
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)