let stream = null;
let isCamera = true; // Track current mode
const videoElement = document.getElementById('videoElement');
const cameraContainer = document.getElementById('cameraContainer');
const dialogOverlay = document.getElementById('dialogOverlay');
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const optionButtons = document.querySelectorAll('.option-button');
let selectedFile = null;

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
    dropZone.style.display = 'none';
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
    dropZone.style.display = 'block';
    resetUpload();
}

function resetUpload() {
    selectedFile = null;
    const previewImage = document.getElementById('previewImage');
    const uploadButtons = document.getElementById('uploadButtons');
    previewImage.style.display = 'none';
    uploadButtons.style.display = 'none';
    dropZone.classList.remove('dragover');
    fileInput.value = '';
}

function submitPhoto() {
    if (selectedFile) {
        handleFile(selectedFile);
    }
}

function previewFile(file) {
    selectedFile = file;
    const reader = new FileReader();
    const previewImage = document.getElementById('previewImage');
    const uploadButtons = document.getElementById('uploadButtons');
    
    reader.onload = function(e) {
        previewImage.src = e.target.result;
        previewImage.style.display = 'block';
        uploadButtons.style.display = 'flex';
    }
    
    reader.readAsDataURL(file);
}

// Upload handlers
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        previewFile(files[0]);
    }
});

dropZone.addEventListener('click', (e) => {
    if (e.target === dropZone || e.target.tagName === 'P') {
        fileInput.click();
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        previewFile(e.target.files[0]);
    }
});

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
