// Air Drums Web Application - Main JavaScript (Original working version + color selection)

class AirDrums {
    constructor() {
        this.video = document.getElementById('videoInput');
        this.canvas = document.getElementById('videoCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.startBtn = document.getElementById('startBtn');
        this.statusEl = document.getElementById('status');
        this.zonesOverlay = document.getElementById('zonesOverlay');
        
        this.stream = null;
        this.isRunning = false;
        this.animationId = null;
        
        // Drum zones (2x3 grid)
        this.zones = [
            { name: 'kick', x1: 0, y1: 0, x2: 0.333, y2: 0.5, color: '#00ff00' },
            { name: 'snare', x1: 0.333, y1: 0, x2: 0.666, y2: 0.5, color: '#ff0000' },
            { name: 'tom', x1: 0.666, y1: 0, x2: 1.0, y2: 0.5, color: '#0000ff' },
            { name: 'floor', x1: 0, y1: 0.5, x2: 0.333, y2: 1.0, color: '#ffff00' },
            { name: 'hat', x1: 0.333, y1: 0.5, x2: 0.666, y2: 1.0, color: '#ff00ff' },
            { name: 'ride', x1: 0.666, y1: 0.5, x2: 1.0, y2: 1.0, color: '#00ffff' }
        ];
        
        // Stick tracking
        this.sticks = {
            left: { points: [], min: 500, isGoingDown: false },
            right: { points: [], min: 500, isGoingDown: false }
        };
        
        // Audio context and buffers
        this.audioContext = null;
        this.audioBuffers = {};
        
        // Color detection thresholds (HSV format - original green defaults)
        this.colorThresholds = {
            minH: 30, minS: 86, minV: 14,
            maxH: 97, maxS: 244, maxV: 255
        };
        this.currentColorName = 'Green';
        
        // Initialize
        this.init();
    }
    
    async init() {
        this.startBtn.addEventListener('click', () => this.start());
        this.setupColorPickers();
        
        // Initialize audio context
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            await this.loadAudioFiles();
            this.statusEl.textContent = 'Ready! Click "Start Camera" to begin.';
        } catch (e) {
            console.error('Audio initialization error:', e);
            this.statusEl.textContent = 'Audio initialization failed. Please check browser permissions.';
        }
    }
    
    setupColorPickers() {
        // Preset color buttons
        const presetButtons = document.querySelectorAll('.color-preset');
        presetButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                presetButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                const color = btn.dataset.color;
                this.selectPresetColor(color);
            });
        });
        
        // Custom color picker
        const customColorPicker = document.getElementById('customColorPicker');
        const useCustomBtn = document.getElementById('useCustomColor');
        
        if (useCustomBtn) {
            useCustomBtn.addEventListener('click', () => {
                const hex = customColorPicker.value;
                this.selectCustomColor(hex);
                presetButtons.forEach(b => b.classList.remove('active'));
            });
        }
        
        // Set green as default active
        const greenBtn = document.querySelector('[data-color="green"]');
        if (greenBtn) {
            greenBtn.classList.add('active');
        }
    }
    
    selectPresetColor(colorName) {
        // HSV color ranges for different colors (Hue, Saturation, Value)
        const colorRanges = {
            green: { minH: 30, minS: 86, minV: 14, maxH: 97, maxS: 244, maxV: 255, name: 'Green' },
            blue: { minH: 100, minS: 100, minV: 50, maxH: 130, maxS: 255, maxV: 255, name: 'Blue' },
            red: { minH: 0, minS: 100, minV: 50, maxH: 10, maxS: 255, maxV: 255, name: 'Red' },
            yellow: { minH: 20, minS: 100, minV: 50, maxH: 30, maxS: 255, maxV: 255, name: 'Yellow' },
            purple: { minH: 130, minS: 100, minV: 50, maxH: 160, maxS: 255, maxV: 255, name: 'Purple' },
            orange: { minH: 10, minS: 100, minV: 50, maxH: 20, maxS: 255, maxV: 255, name: 'Orange' }
        };
        
        const color = colorRanges[colorName];
        if (color) {
            this.colorThresholds = {
                minH: color.minH, minS: color.minS, minV: color.minV,
                maxH: color.maxH, maxS: color.maxS, maxV: color.maxV
            };
            this.currentColorName = color.name;
            this.updateColorDisplay(colorName);
            this.updateStatusMessage();
        }
    }
    
    selectCustomColor(hex) {
        // Convert hex to RGB then to HSV
        const r = parseInt(hex.slice(1, 3), 16) / 255;
        const g = parseInt(hex.slice(3, 5), 16) / 255;
        const b = parseInt(hex.slice(5, 7), 16) / 255;
        
        const hsv = this.rgbToHsv(r, g, b);
        
        // Create range around the selected color
        this.colorThresholds = {
            minH: Math.max(0, hsv.h - 15),
            minS: Math.max(50, hsv.s * 255 - 50),
            minV: Math.max(50, hsv.v * 255 - 50),
            maxH: Math.min(179, hsv.h + 15),
            maxS: Math.min(255, hsv.s * 255 + 50),
            maxV: Math.min(255, hsv.v * 255 + 50)
        };
        
        this.currentColorName = 'Custom';
        this.updateColorDisplay(null, hex);
        this.updateStatusMessage();
    }
    
    rgbToHsv(r, g, b) {
        const max = Math.max(r, g, b);
        const min = Math.min(r, g, b);
        const delta = max - min;
        
        let h = 0;
        if (delta !== 0) {
            if (max === r) {
                h = ((g - b) / delta) % 6;
            } else if (max === g) {
                h = (b - r) / delta + 2;
            } else {
                h = (r - g) / delta + 4;
            }
        }
        h = Math.round(h * 60);
        if (h < 0) h += 360;
        h = h / 2; // Convert to OpenCV HSV range (0-179)
        
        const s = max === 0 ? 0 : delta / max;
        const v = max;
        
        return { h, s, v };
    }
    
    updateColorDisplay(colorName, hexColor = null) {
        const colorDisplay = document.getElementById('currentColorDisplay');
        const colorNameEl = document.getElementById('currentColorName');
        
        if (colorDisplay) {
            if (hexColor) {
                colorDisplay.style.background = hexColor;
            } else if (colorName) {
                const colors = {
                    green: '#00ff00',
                    blue: '#0000ff',
                    red: '#ff0000',
                    yellow: '#ffff00',
                    purple: '#8000ff',
                    orange: '#ff8800'
                };
                colorDisplay.style.background = colors[colorName] || '#00ff00';
            }
        }
        if (colorNameEl) {
            colorNameEl.textContent = this.currentColorName;
        }
    }
    
    updateStatusMessage() {
        if (this.isRunning) {
            this.statusEl.textContent = `Camera active. Move your ${this.currentColorName.toLowerCase()} object!`;
        }
    }
    
    async loadAudioFiles() {
        try {
            const response = await fetch('/api/audio-list');
            const audioList = await response.json();
            
            for (const [drumType, files] of Object.entries(audioList)) {
                if (files.length === 0) continue;
                
                this.audioBuffers[drumType] = [];
                for (const filePath of files.slice(0, 5)) {
                    try {
                        const audioResponse = await fetch(filePath);
                        const arrayBuffer = await audioResponse.arrayBuffer();
                        const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
                        this.audioBuffers[drumType].push(audioBuffer);
                    } catch (e) {
                        console.error(`Failed to load ${filePath}:`, e);
                    }
                }
            }
            
            console.log('Audio files loaded:', Object.keys(this.audioBuffers));
        } catch (e) {
            console.error('Failed to load audio list:', e);
        }
    }
    
    playSound(drumType, volumeIndex = 2) {
        if (!this.audioBuffers[drumType] || this.audioBuffers[drumType].length === 0) {
            return;
        }
        
        const buffers = this.audioBuffers[drumType];
        const index = Math.max(0, Math.min(buffers.length - 1, volumeIndex));
        const buffer = buffers[index];
        
        if (!buffer) return;
        
        try {
            const source = this.audioContext.createBufferSource();
            const gainNode = this.audioContext.createGain();
            
            source.buffer = buffer;
            gainNode.gain.value = 0.7;
            
            source.connect(gainNode);
            gainNode.connect(this.audioContext.destination);
            source.start(0);
        } catch (e) {
            console.error('Error playing sound:', e);
        }
    }
    
    async start() {
        if (this.isRunning) {
            this.stop();
            return;
        }
        
        try {
            this.statusEl.textContent = 'Requesting camera access...';
            
            if (this.audioContext.state === 'suspended') {
                await this.audioContext.resume();
            }
            
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 800 },
                    height: { ideal: 600 },
                    facingMode: 'user'
                }
            });
            
            this.video.srcObject = this.stream;
            
            this.video.addEventListener('loadedmetadata', () => {
                this.canvas.width = this.video.videoWidth;
                this.canvas.height = this.video.videoHeight;
                this.updateZonesOverlay();
                this.processVideo();
            }, { once: true });
            
            this.video.play();
            
            this.isRunning = true;
            this.startBtn.textContent = 'Stop Camera';
            this.updateStatusMessage();
            
        } catch (error) {
            console.error('Camera access error:', error);
            this.statusEl.textContent = 'Failed to access camera. Please allow camera access and refresh the page.';
        }
    }
    
    stop() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
        
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        
        this.isRunning = false;
        this.startBtn.textContent = 'Start Camera';
        this.statusEl.textContent = 'Camera stopped.';
        
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }
    
    updateZonesOverlay() {
        if (!this.zonesOverlay) return;
        
        const rect = this.canvas.getBoundingClientRect();
        this.zonesOverlay.innerHTML = '';
        this.zonesOverlay.style.width = rect.width + 'px';
        this.zonesOverlay.style.height = rect.height + 'px';
        
        this.zones.forEach(zone => {
            const div = document.createElement('div');
            div.className = `zone ${zone.name}`;
            div.style.left = (zone.x1 * 100) + '%';
            div.style.top = (zone.y1 * 100) + '%';
            div.style.width = ((zone.x2 - zone.x1) * 100) + '%';
            div.style.height = ((zone.y2 - zone.y1) * 100) + '%';
            this.zonesOverlay.appendChild(div);
        });
    }
    
    getZoneAtPosition(x, y) {
        const normalizedX = x / this.canvas.width;
        const normalizedY = y / this.canvas.height;
        
        for (const zone of this.zones) {
            if (normalizedX >= zone.x1 && normalizedX < zone.x2 &&
                normalizedY >= zone.y1 && normalizedY < zone.y2) {
                return zone;
            }
        }
        return null;
    }
    
    trackStick(stick, x, y) {
        const now = Date.now();
        stick.points.push({ x, y, time: now });
        
        while (stick.points.length > 4) {
            stick.points.shift();
        }
        
        stick.points = stick.points.filter(p => now - p.time < 200);
        stick.min = Math.min(stick.min, y);
        
        if (stick.points.length >= 2) {
            const oldest = stick.points[0];
            const newest = stick.points[stick.points.length - 1];
            const yDirection = oldest.y - newest.y;
            
            if (stick.isGoingDown && yDirection < -20) {
                const zone = this.getZoneAtPosition(x, y);
                if (zone) {
                    const depth = this.canvas.height - stick.min;
                    const volume = Math.floor(depth / 100);
                    const volumeIndex = Math.max(0, Math.min(4, volume));
                    
                    this.playSound(zone.name, volumeIndex);
                    this.highlightZone(zone.name);
                }
                
                stick.min = this.canvas.height;
                stick.isGoingDown = false;
            }
            
            if (Math.abs(yDirection) > 15 && yDirection >= 0) {
                stick.isGoingDown = true;
            }
        }
    }
    
    highlightZone(zoneName) {
        const zoneEl = this.zonesOverlay.querySelector(`.zone.${zoneName}`);
        if (zoneEl) {
            zoneEl.classList.add('active');
            setTimeout(() => {
                zoneEl.classList.remove('active');
            }, 150);
        }
    }
    
    // Original working green color detection - now works with any HSV range
    isTargetColor(r, g, b) {
        // Convert RGB to HSV
        const rNorm = r / 255;
        const gNorm = g / 255;
        const bNorm = b / 255;
        
        const max = Math.max(rNorm, gNorm, bNorm);
        const min = Math.min(rNorm, gNorm, bNorm);
        const delta = max - min;
        
        let h = 0;
        if (delta !== 0) {
            if (max === rNorm) {
                h = ((gNorm - bNorm) / delta) % 6;
            } else if (max === gNorm) {
                h = (bNorm - rNorm) / delta + 2;
            } else {
                h = (rNorm - gNorm) / delta + 4;
            }
        }
        h = Math.round(h * 60);
        if (h < 0) h += 360;
        h = h / 2; // Convert to OpenCV HSV range (0-179)
        
        const s = max === 0 ? 0 : (delta / max) * 255;
        const v = max * 255;
        
        // Check if within HSV range
        return h >= this.colorThresholds.minH && h <= this.colorThresholds.maxH &&
               s >= this.colorThresholds.minS && s <= this.colorThresholds.maxS &&
               v >= this.colorThresholds.minV && v <= this.colorThresholds.maxV;
    }
    
    findColoredObjects(imageData) {
        const centers = [];
        const width = imageData.width;
        const height = imageData.height;
        const data = imageData.data;
        
        const sampleRate = 4;
        const coloredPixels = [];
        
        for (let y = 0; y < height; y += sampleRate) {
            for (let x = 0; x < width; x += sampleRate) {
                const idx = (y * width + x) * 4;
                const r = data[idx];
                const g = data[idx + 1];
                const b = data[idx + 2];
                
                if (this.isTargetColor(r, g, b)) {
                    coloredPixels.push({ x, y });
                }
            }
        }
        
        if (coloredPixels.length < 50) return centers;
        
        const clusters = this.clusterPixels(coloredPixels);
        
        for (const cluster of clusters) {
            if (cluster.length > 100) {
                let sumX = 0, sumY = 0;
                for (const pixel of cluster) {
                    sumX += pixel.x;
                    sumY += pixel.y;
                }
                centers.push({
                    x: sumX / cluster.length,
                    y: sumY / cluster.length,
                    size: cluster.length
                });
            }
        }
        
        return centers;
    }
    
    clusterPixels(pixels, threshold = 50) {
        const clusters = [];
        const visited = new Set();
        
        for (let i = 0; i < pixels.length; i++) {
            if (visited.has(i)) continue;
            
            const cluster = [pixels[i]];
            visited.add(i);
            
            for (let j = i + 1; j < pixels.length; j++) {
                if (visited.has(j)) continue;
                
                const dx = pixels[i].x - pixels[j].x;
                const dy = pixels[i].y - pixels[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < threshold) {
                    cluster.push(pixels[j]);
                    visited.add(j);
                }
            }
            
            clusters.push(cluster);
        }
        
        return clusters;
    }
    
    processVideo() {
        if (!this.isRunning) return;
        
        if (this.video.readyState === this.video.HAVE_ENOUGH_DATA) {
            // Draw video frame (mirrored)
            this.ctx.save();
            this.ctx.translate(this.canvas.width, 0);
            this.ctx.scale(-1, 1);
            this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
            this.ctx.restore();
            
            // Draw drum zones
            this.drawZones();
            
            // Get image data for color detection
            const imageData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
            
            // Find colored objects
            const centers = this.findColoredObjects(imageData);
            
            // Sort by size and take top 2
            centers.sort((a, b) => b.size - a.size);
            const topCenters = centers.slice(0, 2);
            
            // Track sticks
            if (topCenters.length === 2) {
                topCenters.sort((a, b) => a.x - b.x);
                this.trackStick(this.sticks.left, topCenters[0].x, topCenters[0].y);
                this.trackStick(this.sticks.right, topCenters[1].x, topCenters[1].y);
                
                // Draw stick positions
                this.ctx.fillStyle = 'rgba(156, 76, 76, 0.8)';
                this.ctx.beginPath();
                this.ctx.arc(topCenters[0].x, topCenters[0].y, 10, 0, Math.PI * 2);
                this.ctx.fill();
                
                this.ctx.fillStyle = 'rgba(76, 76, 156, 0.8)';
                this.ctx.beginPath();
                this.ctx.arc(topCenters[1].x, topCenters[1].y, 10, 0, Math.PI * 2);
                this.ctx.fill();
            } else if (topCenters.length === 1) {
                const center = topCenters[0];
                if (center.x < this.canvas.width / 2) {
                    this.trackStick(this.sticks.left, center.x, center.y);
                } else {
                    this.trackStick(this.sticks.right, center.x, center.y);
                }
                
                this.ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
                this.ctx.beginPath();
                this.ctx.arc(center.x, center.y, 10, 0, Math.PI * 2);
                this.ctx.fill();
            }
        }
        
        this.animationId = requestAnimationFrame(() => this.processVideo());
    }
    
    drawZones() {
        const width = this.canvas.width;
        const height = this.canvas.height;
        
        this.zones.forEach(zone => {
            const x1 = zone.x1 * width;
            const y1 = zone.y1 * height;
            const x2 = zone.x2 * width;
            const y2 = zone.y2 * height;
            
            const color = zone.color;
            this.ctx.strokeStyle = color;
            this.ctx.lineWidth = 3;
            this.ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
            
            this.ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
            this.ctx.fillRect(x1 + 5, y1 + 5, 80, 25);
            
            this.ctx.fillStyle = color;
            this.ctx.font = 'bold 16px Arial';
            this.ctx.fillText(zone.name.toUpperCase(), x1 + 10, y1 + 23);
        });
    }
}

// Initialize when page loads
let airDrums;
document.addEventListener('DOMContentLoaded', () => {
    airDrums = new AirDrums();
});
