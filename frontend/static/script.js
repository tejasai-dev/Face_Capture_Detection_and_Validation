let stream = null;
let isCamera = true; // Track current mode
const videoElement = document.getElementById('videoElement');
const cameraContainer = document.getElementById('cameraContainer');
const optionButtons = document.querySelectorAll('.option-button');

// Start camera by default
window.addEventListener('load', () => {
    startCamera();
});

function updateOptionButtons() {
    optionButtons.forEach(button => {
        button.classList.remove('active');
        if ((button.textContent === 'Take Photo' && isCamera) ||
            (button.textContent === 'Upload Photo' && !isCamera)) {
            button.classList.add('active');
        }
    });
}

async function startCamera() {
    isCamera = true;
    updateOptionButtons();
    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        videoElement.srcObject = stream;
        cameraContainer.style.display = 'block';
    } catch (err) {
        showDialog('error', 'Camera Error', 'Unable to access camera. Please make sure you have granted camera permissions.');
    }
}

function closeCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
    cameraContainer.style.display = 'none';
}

function showUploadSection() {
    isCamera = false;
    updateOptionButtons();
    closeCamera();
}

async function capturePhoto() {
    const canvas = document.createElement('canvas');
    canvas.width = videoElement.videoWidth;
    canvas.height = videoElement.videoHeight;
    canvas.getContext('2d').drawImage(videoElement, 0, 0);
    
    canvas.toBlob(async (blob) => {
        const file = new File([blob], "camera-photo.jpg", { type: "image/jpeg" });
        await handleFile(file);
    }, 'image/jpeg');
}
