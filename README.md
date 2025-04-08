# Face Capture & Detection System

A web application for capturing and validating face images with multiple validation checks.

## Features

- **Face Detection**: Ensures that a face is present in the uploaded image
- **Multiple Face Detection**: Prevents uploading images with multiple faces
- **Face Size Validation**: Ensures the face is not too small or far away
- **Guru Dev Detection**: Prevents uploading images of Guru Dev
- **AI-Generated Image Detection**: Prevents uploading AI-generated images
- **Camera Capture**: Allows capturing photos directly from the camera
- **Image Upload**: Supports uploading images from the device

## Technical Implementation

### Backend

- **FastAPI**: Web framework for building the API
- **InsightFace**: Face detection and recognition
- **Transformers**: AI image detection using the "hchcsuim/FaceAIorNot" model
- **OpenCV**: Image processing
- **Pillow**: Image handling

### Frontend

- **HTML/CSS/JavaScript**: Frontend implementation
- **Responsive Design**: Works on various screen sizes

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

1. Start the application:
   ```
   uvicorn backend.app:app --reload
   ```
2. Open your browser and navigate to `http://localhost:8000`

## Usage

1. Choose between "Take Photo" or "Upload Photo"
2. Follow the guidelines for capturing or uploading a photo
3. The system will validate the image and provide feedback
4. If successful, the image will be saved

## Validation Checks

1. **Image Format**: Ensures the image is in a supported format (JPG, JPEG, PNG)
2. **Face Detection**: Ensures a face is present in the image
3. **Multiple Face Detection**: Ensures only one face is present
4. **Face Size Validation**: Ensures the face is not too small or far away
5. **Guru Dev Detection**: Ensures the image is not of Guru Dev
6. **AI-Generated Detection**: Checks if the image is AI-generated

## Troubleshooting

If you encounter dependency conflicts during installation, try the following:

1. Upgrade pip to the latest version: `python -m pip install --upgrade pip`
2. Install dependencies with the `--no-deps` flag for problematic packages:
   ```
   pip install --no-deps package_name
   ```
3. If issues persist, try installing packages one by one to identify conflicts

