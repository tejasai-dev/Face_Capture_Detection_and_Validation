# Face Capture & Detection System

A web application that captures and validates face images for face detection and recognition.

## Features
- **Live Camera Capture**
  - Uses device camera to capture face images
  - Shows circular guide for face alignment
  - Captures photo with one click
  - Validates captured image instantly

- **Image Upload Support**
  - Accepts image files (JPG/JPEG/PNG)
  - Shows image preview before upload
  - Validates image format and size
  - Processes uploaded image for face detection

- **Face Detection & Validation**
  - Detects single face in image
  - Shows error if multiple faces detected
  - Validates face visibility (eyes, nose, ears)
  - Displays error messages with visual feedback

- **Guru Dev Image Filtering**
  - Compares face with Guru Dev database
  - Blocks Guru Dev images
  - Shows specific error for Guru Dev matches
  - Uses face embedding comparison

- **Modern, Responsive UI**
  - Shows loading during processing
  - Displays success/error dialogs
  - Provides clear user instructions
  - Works on both desktop and mobile

## Requirements
- Python 3.8 to 3.9
- Dependencies listed in `requirements.txt`

## Setup
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
uvicorn backend.app:app --reload
```

3. Open browser and navigate to `http://localhost:8000`

## Usage
- Click "Take Photo" to use camera
- Click "Upload Photo" to upload an image
- Follow on-screen instructions for face capture
- System will validate the image and provide feedback 