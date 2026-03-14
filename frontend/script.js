document.addEventListener('DOMContentLoaded', () => {
    
    // File State Management
    let inspectionFile = null;
    let thermalFile = null;

    // UI Elements
    const dropZoneInspection = document.getElementById('drop-zone-inspection');
    const fileInputInspection = document.getElementById('file-input-inspection');
    const statusInspection = document.getElementById('status-inspection');
    
    const dropZoneThermal = document.getElementById('drop-zone-thermal');
    const fileInputThermal = document.getElementById('file-input-thermal');
    const statusThermal = document.getElementById('status-thermal');
    
    const analyzeBtn = document.getElementById('analyze-btn');
    const loadingState = document.getElementById('loading-state');
    const resultsSection = document.getElementById('results-section');
    const markdownOutput = document.getElementById('markdown-output');
    
    const loadingText = document.getElementById('loading-text');
    const step1 = document.getElementById('step-1');
    const step2 = document.getElementById('step-2');
    const step3 = document.getElementById('step-3');

    // Make target specific helper to reduce duplication
    function setupDropZone(dropZoneElem, inputElem, type) {
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZoneElem.addEventListener(eventName, preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZoneElem.addEventListener(eventName, () => dropZoneElem.classList.add('dragover'), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZoneElem.addEventListener(eventName, () => dropZoneElem.classList.remove('dragover'), false);
        });

        dropZoneElem.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            handleFileSelect(files[0], type);
        }, false);

        // Click on dropzone delegates to hidden input
        dropZoneElem.addEventListener('click', () => {
            inputElem.click();
        });

        inputElem.addEventListener('change', function() {
            if(this.files && this.files.length > 0) {
                handleFileSelect(this.files[0], type);
            }
        });
    }

    setupDropZone(dropZoneInspection, fileInputInspection, 'inspection');
    setupDropZone(dropZoneThermal, fileInputThermal, 'thermal');

    // Global prevent default
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults (e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function handleFileSelect(file, type) {
        if (!file) return;

        const isPdf = file.type === "application/pdf" || file.name.toLowerCase().endsWith('.pdf');
        const isDocx = file.type === "application/vnd.openxmlformats-officedocument.wordprocessingml.document" || file.name.toLowerCase().endsWith('.docx');
        
        if (!isPdf && !isDocx) {
            alert("Please upload a valid document (.pdf or .docx).");
            return;
        }

        // Update state and UI
        if (type === 'inspection') {
            inspectionFile = file;
            updateFileStatus(dropZoneInspection, statusInspection, file);
        } else if (type === 'thermal') {
            thermalFile = file;
            updateFileStatus(dropZoneThermal, statusThermal, file);
        }

        checkEnableButton();
    }

    function updateFileStatus(dropZoneElem, statusElem, file) {
        // Hide dropzone, show status
        dropZoneElem.classList.add('hidden');
        statusElem.classList.remove('hidden');
        
        // Populate file details
        statusElem.querySelector('.file-name').textContent = file.name;
        statusElem.querySelector('.file-size').textContent = formatBytes(file.size);
    }

    function checkEnableButton() {
        // We require BOTH an inspection and thermal report now
        if (inspectionFile && thermalFile) {
            analyzeBtn.disabled = false;
        }
    }

    function formatBytes(bytes, decimals = 2) {
        if (!+bytes) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
    }

    // Handle form submission
    analyzeBtn.addEventListener('click', async () => {
        if (!inspectionFile || !thermalFile) {
            alert("Please upload both the Inspection and Thermal reports.");
            return;
        }

        // Setup loading UI
        analyzeBtn.disabled = true;
        // Hide upload section to make space if on mobile, or just show loading state
        loadingState.classList.remove('hidden');
        resultsSection.classList.add('hidden');
        
        // Scroll to loading state
        loadingState.scrollIntoView({ behavior: 'smooth' });

        const formData = new FormData();
        formData.append("inspection_file", inspectionFile);
        formData.append("thermal_file", thermalFile);

        // Simulate step updates since backend stream might be tricky without websockets
        const stepInterval = simulateProgressSteps();

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Upload failed");
            }

            const data = await response.json();
            
            clearInterval(stepInterval);
            finishProgressSteps();
            
            // Render the markdown result
            loadingState.classList.add('hidden');
            resultsSection.classList.remove('hidden');
            
            // Use marked.js configured gracefully
            if (typeof marked !== 'undefined') {
                markdownOutput.innerHTML = marked.parse(data.report);
            } else {
                // Fallback text rendering
                markdownOutput.innerHTML = `<pre style="white-space: pre-wrap; font-family: inherit;">${data.report}</pre>`;
            }

            // Scroll to results
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

        } catch (error) {
            clearInterval(stepInterval);
            loadingState.classList.add('hidden');
            console.error("Error analyzing documents:", error);
            alert("An error occurred during analysis: " + error.message);
        } finally {
            analyzeBtn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Re-run Analysis';
            analyzeBtn.disabled = false;
        }
    });

    function simulateProgressSteps() {
        step1.classList.add('active');
        step2.classList.remove('active');
        step3.classList.remove('active');
        loadingText.textContent = "Extracting text and imaging data...";

        let tick = 0;
        return setInterval(() => {
            tick++;
            // Approximate backend timing based on main.py wait states
            if (tick === 5) {
                step1.classList.remove('active');
                step2.classList.add('active');
                loadingText.textContent = "Synthesizing and running reasoning models...";
            } else if (tick === 15) {
                step2.classList.remove('active');
                step3.classList.add('active');
                loadingText.textContent = "Generating final diagnostic report...";
            }
        }, 1500); // 1.5 seconds per tick
    }
    
    function finishProgressSteps() {
        step1.classList.remove('active');
        step2.classList.remove('active');
        step3.classList.add('active');
        loadingText.textContent = "Complete!";
    }
});
