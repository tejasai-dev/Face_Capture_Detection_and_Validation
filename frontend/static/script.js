let isCamera = true; // Track current mode
const optionButtons = document.querySelectorAll('.option-button');

function updateOptionButtons() {
    optionButtons.forEach(button => {
        button.classList.remove('active');
        if ((button.textContent === 'Take Photo' && isCamera) ||
            (button.textContent === 'Upload Photo' && !isCamera)) {
            button.classList.add('active');
        }
    });
}

function startCamera() {
    isCamera = true;
    updateOptionButtons();
    // Camera functionality will be added in the next phase
}

function showUploadSection() {
    isCamera = false;
    updateOptionButtons();
    // Upload section functionality will be added in the next phase
}
