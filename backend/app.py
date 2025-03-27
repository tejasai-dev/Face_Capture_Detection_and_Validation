from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import cv2
import numpy as np
from insightface.app import FaceAnalysis
from insightface.model_zoo import get_model
from numpy.linalg import norm

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
        return None, "No Face Detected. Please Upload or Capture an Image Where Your Eyes, Nose, Ears, Lips, Forehead, and Chin are Clearly Visible", None
    
    if len(faces) > 1:
        # Draw bounding boxes around detected faces
        for face in faces:
            bbox = face.bbox.astype(int)
            cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 10)
        return None, "Multiple faces detected in the image.", img

    face = faces[0]
    embedding = recognizer.get(img_rgb, face)
    return embedding, None, img

@app.get("/")
async def serve_homepage():
    """Serve the main index.html file"""
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
