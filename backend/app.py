from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import cv2
import numpy as np
from insightface.app import FaceAnalysis
from insightface.model_zoo import get_model
from numpy.linalg import norm
import tempfile
import uuid
import shutil
import asyncio
from datetime import datetime, timedelta

# Get the base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")
UPLOADS_DIR = os.path.join(BASE_DIR, "..", "uploads")
MODEL_DIR = os.path.join(BASE_DIR, "..")

# Create uploads directory if it doesn't exist
os.makedirs(UPLOADS_DIR, exist_ok=True)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Mount static directories
app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

# Initialize face detection and recognition models
detector = FaceAnalysis(name="antelopev2", root=MODEL_DIR, providers=["CPUExecutionProvider"])
detector.prepare(ctx_id=-1, det_thresh=0.35)
recognizer = get_model(os.path.join(MODEL_DIR, "models", "antelopev2", "glintr100.onnx"))
recognizer.prepare(ctx_id=-1)

# Load Guru Dev embeddings
GURUDEV_EMBEDDING_PATH = os.path.join(BASE_DIR, "..", "Gurudev_Embedding", "gurudev_embedding.npy")
gurudev_embeddings = np.load(GURUDEV_EMBEDDING_PATH, allow_pickle=True).item()
gurudev_embedding_list = list(gurudev_embeddings.values())

def cosine_similarity(emb1, emb2):
    """Calculate cosine similarity between two embeddings"""
    return np.dot(emb1, emb2) / (norm(emb1) * norm(emb2))

def get_face_embedding(image_path):
    """Extract face embedding from an image"""
    img = cv2.imread(image_path)
    if img is None:
        return None, "Invalid image file.", None
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    faces = detector.get(img_rgb)
    
    if not faces:
        return None, "No face detected. Please upload or capture an image where your facial features (eyes, nose, ears, lips, forehead, and chin) are clearly visible.", None
    
    # Check for small/faraway face
    face = faces[0]
    bbox = face.bbox.astype(int)
    face_width = bbox[2] - bbox[0]
    face_height = bbox[3] - bbox[1]
    face_area = face_width * face_height
    image_area = img.shape[0] * img.shape[1]
    face_ratio = face_area / image_area
    
    # If face takes up less than 5% of the image, consider it too small/far away
    if face_ratio < 0.05:
        # Draw bounding box around the small face
        cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 10)
        return None, "Your face is detected, but it is too far from the camera. Please move closer or upload a clearer, close-up photo for better detection.", img
    
    if len(faces) > 1:
        # Draw bounding boxes around detected faces
        for face in faces:
            bbox = face.bbox.astype(int)
            cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 10)
        return None, "Multiple faces detected in the image.", img

    embedding = recognizer.get(img_rgb, face)
    return embedding, None, img

@app.get("/")
async def serve_homepage():
    """Serve the main index.html file"""
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.post("/validate-image")
async def validate_image(file: UploadFile = File(...)):
    try:
        # 1. Validate image format
        if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "Unsupported file format. Please upload a JPG, JPEG, or PNG image.",
                    "type": "format_error"
                }
            )
        
        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[-1]) as temp:
            temp.write(file.file.read())
            temp_image_path = temp.name

        if not os.path.exists(temp_image_path) or os.path.getsize(temp_image_path) == 0:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "Invalid or empty image file.",
                    "type": "file_error"
                }
            )

        # 2. Check for face presence and handle multiple faces
        embedding, error, img = get_face_embedding(temp_image_path)
        
        if error:
            if isinstance(error, str) and img is not None:
                # Determine error type and filename prefix
                if "Multiple faces" in error:
                    error_type = "multiple_faces"
                    filename_prefix = "multiple_faces_"
                elif "too far from the camera" in error:
                    error_type = "small_face"
                    filename_prefix = "small_face_"
                else:
                    error_type = "face_detection_error"
                    filename_prefix = "face_error_"
                
                # Save the image with bounding boxes
                unique_filename = f"{filename_prefix}{uuid.uuid4()}.jpg"
                output_image_path = os.path.join(tempfile.gettempdir(), unique_filename)
                cv2.imwrite(output_image_path, img, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
                
                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "message": error,
                        "type": error_type,
                        "image_with_bboxes": unique_filename
                    }
                )
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": error,
                    "type": "face_detection_error"
                }
            )
            
        # 3. Check against Guru Dev
        threshold = 0.45
        for guru_embedding in gurudev_embedding_list:
            similarity = cosine_similarity(embedding, guru_embedding)
            if similarity > threshold:
                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "message": "The Uploaded Image belongs to \"Gurudev\". We cannot process it. Please upload your own image.",
                        "type": "guru_dev_match"
                    }
                )

        # If all checks pass, save the image to uploads directory
        unique_filename = f"face_{uuid.uuid4()}{os.path.splitext(file.filename)[-1]}"
        upload_path = os.path.join(UPLOADS_DIR, unique_filename)
        shutil.copy2(temp_image_path, upload_path)

        # Clean up temp file
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Image validation successful. Your image has been saved.",
                "type": "success",
                "image_path": f"/uploads/{unique_filename}"
            }
        )
    
    except Exception as e:
        if 'temp_image_path' in locals() and os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"An error occurred: {str(e)}",
                "type": "server_error"
            }
        )

@app.get("/temp_image/{image_name}")
async def get_temp_image(image_name: str):
    """Serve temporary images (like multiple face detection results)"""
    image_path = os.path.join(tempfile.gettempdir(), image_name)
    if os.path.exists(image_path):
        return FileResponse(image_path)
    else:
        raise HTTPException(status_code=404, detail="Image not found")

@app.on_event("startup")
async def setup_periodic_cleanup():
    """Setup periodic cleanup of temporary files"""
    async def cleanup_temp_images():
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                now = datetime.now()
                temp_dir = tempfile.gettempdir()
                
                # Cleanup face detection error images
                for filename in os.listdir(temp_dir):
                    if (filename.startswith(("multiple_faces_", "small_face_", "face_error_")) and 
                        filename.endswith(".jpg")):
                        file_path = os.path.join(temp_dir, filename)
                        file_creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
                        
                        # Remove files older than 1 hour
                        if now - file_creation_time > timedelta(hours=1):
                            try:
                                os.remove(file_path)
                                print(f"Cleaned up old temporary file: {filename}")
                            except Exception as e:
                                print(f"Error cleaning up {filename}: {str(e)}")
            except Exception as e:
                print(f"Error in cleanup task: {str(e)}")
                await asyncio.sleep(60)  # Wait a minute before retrying if error occurs
    
    # Start the cleanup task
    asyncio.create_task(cleanup_temp_images())
