class CanvasHandler {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.canvas = document.createElement('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.container.appendChild(this.canvas);

        this.originalImage = new Image();
        this.masks = []; // List of {x, y, w, h}
        this.scale = 1.0;
        this.isDrawing = false;
        this.startX = 0;
        this.startY = 0;

        this.initEvents();
    }

    setImages(src, callback) {
        this.originalImage.onload = () => {
            this.resizeCanvas();
            this.render();
            if (callback) callback();
        };
        this.originalImage.src = src;
    }

    resizeCanvas() {
        const maxWidth = 1000;
        const width = this.originalImage.width;
        const height = this.originalImage.height;

        if (width > maxWidth) {
            this.scale = maxWidth / width;
        } else {
            this.scale = 1.0;
        }

        this.canvas.width = width * this.scale;
        this.canvas.height = height * this.scale;
    }

    initEvents() {
        this.canvas.addEventListener('mousedown', (e) => this.startDrawing(e));
        this.canvas.addEventListener('mousemove', (e) => this.draw(e));
        this.canvas.addEventListener('mouseup', (e) => this.stopDrawing(e));
        this.canvas.addEventListener('mouseleave', (e) => {
            if (this.isDrawing) this.stopDrawing(e);
        });
    }

    getMousePos(e) {
        const rect = this.canvas.getBoundingClientRect();
        return {
            x: (e.clientX - rect.left) / this.scale,
            y: (e.clientY - rect.top) / this.scale
        };
    }

    startDrawing(e) {
        this.isDrawing = true;
        const pos = this.getMousePos(e);
        this.startX = pos.x;
        this.startY = pos.y;
    }

    draw(e) {
        if (!this.isDrawing) return;
        const pos = this.getMousePos(e);
        const w = pos.x - this.startX;
        const h = pos.y - this.startY;

        this.render();
        // Feedback box
        this.ctx.strokeStyle = '#ff4d4d';
        this.ctx.lineWidth = 2;
        this.ctx.strokeRect(this.startX * this.scale, this.startY * this.scale, w * this.scale, h * this.scale);
        this.ctx.fillStyle = 'rgba(255, 77, 77, 0.3)';
        this.ctx.fillRect(this.startX * this.scale, this.startY * this.scale, w * this.scale, h * this.scale);
    }

    stopDrawing(e) {
        if (!this.isDrawing) return;
        this.isDrawing = false;

        const pos = this.getMousePos(e);
        const w = Math.abs(pos.x - this.startX);
        const h = Math.abs(pos.y - this.startY);
        const x = Math.min(this.startX, pos.x);
        const y = Math.min(this.startY, pos.y);

        // threshold for drag (mask) vs click (toggle)
        if (w > 5 || h > 5) {
            this.masks.push({ x, y, w, h });
            console.log("Mask added:", { x, y, w, h });
        } else {
            this.toggleMaskAt(pos.x, pos.y);
        }
        this.render();
    }

    toggleMaskAt(x, y) {
        // Find if we clicked on an existing mask
        const index = this.masks.findIndex(m =>
            x >= m.x && x <= m.x + m.w &&
            y >= m.y && y <= m.y + m.h
        );

        if (index !== -1) {
            this.masks.splice(index, 1);
        }
    }

    maskAll(detections) {
        if (!detections) return;
        const newMasks = [];
        detections.forEach(d => {
            // Avoid duplicate masks for the same area
            const exists = this.masks.some(m => Math.abs(m.x - d.bbox.x) < 5 && Math.abs(m.y - d.bbox.y) < 5);
            if (!exists) {
                newMasks.push(d.bbox);
            }
        });
        this.masks = [...this.masks, ...newMasks];
        this.render();
    }

    unmaskAll() {
        this.clear();
    }

    undo() {
        this.masks.pop();
        this.render();
    }

    clear() {
        this.masks = [];
        this.render();
    }

    render() {
        if (!this.originalImage.complete) return;
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx.drawImage(this.originalImage, 0, 0, this.canvas.width, this.canvas.height);

        // Draw all masks with nice rounded corners or solid black
        this.ctx.fillStyle = 'black';
        this.ctx.shadowBlur = 0;
        this.masks.forEach(m => {
            this.ctx.fillRect(m.x * this.scale, m.y * this.scale, m.w * this.scale, m.h * this.scale);
        });
    }

    getMasks() {
        return this.masks.map(m => ({
            x: Math.round(m.x),
            y: Math.round(m.y),
            w: Math.round(m.w),
            h: Math.round(m.h)
        }));
    }
}
