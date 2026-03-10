document.addEventListener('DOMContentLoaded', () => {
    let currentSession = null;
    let images = [];
    let currentPageIndex = 0;
    let pageMasks = []; // Store masks per page [[page0_masks], [page1_masks]...]

    const canvasHandler = new CanvasHandler('editor-container');

    // UI Elements
    const fileUpload = document.getElementById('file-upload');
    const uploadSection = document.getElementById('upload-section');
    const editorSection = document.getElementById('editor-section');
    const fileInfo = document.getElementById('file-info');
    const filenameDisplay = document.getElementById('filename-display');
    const detectBtn = document.getElementById('detect-btn');
    const resetBtn = document.getElementById('reset-btn');

    const pageControls = document.getElementById('page-controls');
    const pageIndicator = document.getElementById('page-indicator');
    const prevPage = document.getElementById('prev-page');
    const nextPage = document.getElementById('next-page');

    const undoBtn = document.getElementById('undo-btn');
    const maskAllBtn = document.getElementById('mask-all-btn');
    const unmaskAllBtn = document.getElementById('unmask-all-btn');
    const clearBtn = document.getElementById('clear-btn');
    const downloadBtn = document.getElementById('download-btn');
    const compareBtn = document.getElementById('compare-btn');

    const suggestionsDiv = document.getElementById('detection-suggestions');
    const suggestionsList = document.getElementById('suggestions-list');

    let lastDetections = [];

    // Upload Handling
    fileUpload.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        try {
            const data = await API.upload(file);
            if (data.error) throw new Error(data.error);

            currentSession = data.session_id;
            images = data.images;
            currentPageIndex = 0;
            pageMasks = images.map(() => []);

            filenameDisplay.textContent = file.name;
            fileInfo.classList.remove('hidden');
            uploadSection.classList.add('hidden');
            editorSection.classList.remove('hidden');

            loadPage(0);
        } catch (err) {
            alert("Upload failed: " + err.message);
        }
    });

    const loadPage = (index) => {
        currentPageIndex = index;

        const imageUrl = `/api/images/${images[index]}`;
        canvasHandler.setImages(imageUrl, () => {
            canvasHandler.masks = pageMasks[index] || [];
            canvasHandler.render();
        });

        if (images.length > 1) {
            pageControls.classList.remove('hidden');
            pageIndicator.textContent = `Page ${index + 1} of ${images.length}`;
            prevPage.disabled = index === 0;
            nextPage.disabled = index === images.length - 1;
        } else {
            pageControls.classList.add('hidden');
        }

        suggestionsDiv.classList.add('hidden');
        suggestionsList.innerHTML = '';
        lastDetections = [];
    };

    // Pagination
    prevPage.onclick = () => {
        pageMasks[currentPageIndex] = canvasHandler.masks; // Final sync
        if (currentPageIndex > 0) loadPage(currentPageIndex - 1);
    };
    nextPage.onclick = () => {
        pageMasks[currentPageIndex] = canvasHandler.masks; // Final sync
        if (currentPageIndex < images.length - 1) loadPage(currentPageIndex + 1);
    };

    // Detection
    detectBtn.onclick = async () => {
        pageMasks[currentPageIndex] = canvasHandler.masks;
        const originalText = detectBtn.innerHTML;
        detectBtn.disabled = true;
        detectBtn.innerHTML = "⌛ Detecting...";

        try {
            const data = await API.detect(currentSession, currentPageIndex);
            lastDetections = data.detections || [];

            if (lastDetections.length > 0) {
                suggestionsDiv.classList.remove('hidden');
                suggestionsList.innerHTML = '';
                lastDetections.forEach(det => {
                    const item = document.createElement('div');
                    item.className = 'suggestion-item';
                    item.innerHTML = `
                        <span><strong>${det.type}</strong>: ${det.text}</span>
                        <button class="apply-suggestion">Mask</button>
                    `;
                    item.querySelector('.apply-suggestion').onclick = () => {
                        canvasHandler.masks.push(det.bbox);
                        pageMasks[currentPageIndex] = canvasHandler.masks; // Sync to pageMasks
                        canvasHandler.render();
                        item.remove();
                        if (suggestionsList.children.length === 0) suggestionsDiv.classList.add('hidden');
                    };
                    suggestionsList.appendChild(item);
                });
                suggestionsDiv.scrollIntoView({ behavior: 'smooth' });
            } else {
                alert("No sensitive information detected on this page.");
            }
        } catch (err) {
            alert("Detection error: Make sure Tesseract is installed properly.");
        } finally {
            detectBtn.disabled = false;
            detectBtn.innerHTML = originalText;
        }
    };

    // Actions
    undoBtn.onclick = () => {
        canvasHandler.undo();
        pageMasks[currentPageIndex] = canvasHandler.masks;
    };
    maskAllBtn.onclick = () => {
        if (lastDetections.length === 0) {
            alert("Please run 'Auto-detect' first!");
            return;
        }
        canvasHandler.maskAll(lastDetections);
        pageMasks[currentPageIndex] = canvasHandler.masks; // Sync to pageMasks
        suggestionsList.innerHTML = '';
        suggestionsDiv.classList.add('hidden');
    };
    unmaskAllBtn.onclick = () => {
        canvasHandler.unmaskAll();
        pageMasks[currentPageIndex] = canvasHandler.masks;
    };
    clearBtn.onclick = () => {
        canvasHandler.clear();
        pageMasks[currentPageIndex] = canvasHandler.masks;
    };
    resetBtn.onclick = () => window.location.reload();

    downloadBtn.onclick = async () => {
        // Final save for current page
        pageMasks[currentPageIndex] = canvasHandler.masks;

        try {
            const data = await API.redact(currentSession, pageMasks);
            if (data.download_url) {
                window.location.href = data.download_url;
            }
        } catch (err) {
            alert("Redaction failed: " + err.message);
        }
    };

    // Comparison View
    const modal = document.getElementById('compare-modal');
    compareBtn.onclick = () => {
        pageMasks[currentPageIndex] = canvasHandler.masks;
        const origPreview = document.getElementById('orig-preview');
        const maskedPreview = document.getElementById('masked-preview');

        const imgUrl = `/api/images/${images[currentPageIndex]}`;
        origPreview.innerHTML = `<img src="${imgUrl}">`;

        // Show masked version
        const maskedCanvas = document.createElement('canvas');
        const mCtx = maskedCanvas.getContext('2d');
        const img = new Image();
        img.onload = () => {
            maskedCanvas.width = img.width;
            maskedCanvas.height = img.height;
            mCtx.drawImage(img, 0, 0);
            mCtx.fillStyle = 'black';
            canvasHandler.getMasks().forEach(m => {
                mCtx.fillRect(m.x, m.y, m.w, m.h);
            });
            maskedPreview.innerHTML = '';
            maskedPreview.appendChild(maskedCanvas);
        };
        img.src = imgUrl;

        modal.classList.remove('hidden');
    };

    document.querySelector('.close-modal').onclick = () => modal.classList.add('hidden');
    window.onclick = (e) => { if (e.target == modal) modal.classList.add('hidden'); };
});
