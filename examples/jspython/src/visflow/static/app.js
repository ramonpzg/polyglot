/* VisFlow JavaScript Application */

class VisFlowEngine {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.websocket = null;
        this.particles = null;
        
        this.init();
        this.setupWebSocket();
        this.setupEventListeners();
    }
    
    init() {
        // Create scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x111111);
        
        // Create camera
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.camera.position.z = 50;
        
        // Create renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(window.innerWidth * 0.7, window.innerHeight * 0.6);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        document.getElementById('visualization-container').appendChild(this.renderer.domElement);
        
        // Add lighting
        const ambientLight = new THREE.AmbientLight(0x404040);
        this.scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight.position.set(1, 1, 1);
        this.scene.add(directionalLight);
        
        // Add axes helper
        const axesHelper = new THREE.AxesHelper(5);
        this.scene.add(axesHelper);
        
        // Start animation loop
        this.animate();
        
        // Handle window resize
        window.addEventListener('resize', () => this.onWindowResize(), false);
    }
    
    setupWebSocket() {
        // In a real implementation, we would connect to the WebSocket
        // For now, we'll just simulate data updates
        console.log("WebSocket connection would be established here");
    }
    
    setupEventListeners() {
        // Run button
        document.getElementById('run-btn').addEventListener('click', () => {
            this.executeCode();
        });
        
        // Upload button
        document.getElementById('upload-btn').addEventListener('click', () => {
            document.getElementById('file-input').click();
        });
        
        // File input
        document.getElementById('file-input').addEventListener('change', (event) => {
            this.uploadFile(event.target.files[0]);
        });
        
        // Example button
        document.getElementById('example-btn').addEventListener('click', () => {
            this.loadExampleData();
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (event) => {
            if ((event.ctrlKey || event.metaKey) && event.key === 'r') {
                event.preventDefault();
                this.executeCode();
            }
        });
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        // Rotate particles for demo
        if (this.particles) {
            this.particles.rotation.x += 0.001;
            this.particles.rotation.y += 0.002;
        }
        
        this.renderer.render(this.scene, this.camera);
    }
    
    onWindowResize() {
        this.camera.aspect = (window.innerWidth * 0.7) / (window.innerHeight * 0.6);
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth * 0.7, window.innerHeight * 0.6);
    }
    
    async executeCode() {
        const code = document.getElementById('code-editor').value;
        const logsElement = document.getElementById('logs');
        
        logsElement.innerHTML = 'Executing code...';
        
        try {
            const response = await fetch('/execute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ code: code })
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                logsElement.innerHTML = 'Code executed successfully';
                if (result.data) {
                    this.updateVisualization(result.data);
                    this.updateDataPreview(result.data);
                }
            } else {
                logsElement.innerHTML = `Error: ${result.message}`;
                console.error(result.traceback);
            }
        } catch (error) {
            logsElement.innerHTML = `Network error: ${error.message}`;
            console.error(error);
        }
    }
    
    async uploadFile(file) {
        const logsElement = document.getElementById('logs');
        
        if (!file) return;
        
        const formData = new FormData();
        formData.append('file', file);
        
        logsElement.innerHTML = 'Uploading file...';
        
        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                logsElement.innerHTML = `File uploaded: ${result.rows} rows, ${result.columns.length} columns`;
                // Load the data for visualization
                this.loadCurrentData();
            } else {
                logsElement.innerHTML = `Upload error: ${result.message}`;
            }
        } catch (error) {
            logsElement.innerHTML = `Network error: ${error.message}`;
            console.error(error);
        }
    }
    
    async loadCurrentData() {
        try {
            const response = await fetch('/data');
            const result = await response.json();
            
            if (result.data) {
                this.updateVisualization(result.data);
                this.updateDataPreview(result.data);
            }
        } catch (error) {
            console.error('Error loading data:', error);
        }
    }
    
    loadExampleData() {
        // Create sample data for demonstration
        const sampleData = [];
        for (let i = 0; i < 1000; i++) {
            sampleData.push({
                latitude: (Math.random() - 0.5) * 180,
                longitude: (Math.random() - 0.5) * 360,
                temperature: Math.random() * 40,
                humidity: Math.random() * 100,
                wind_speed: Math.random() * 30,
                fire_risk: Math.random()
            });
        }
        
        this.updateVisualization(sampleData);
        this.updateDataPreview(sampleData);
        document.getElementById('logs').innerHTML = 'Example data loaded';
    }
    
    updateVisualization(data) {
        // Clear previous visualization
        if (this.particles) {
            this.scene.remove(this.particles);
        }
        
        // Create particle system for data points
        const particleCount = Math.min(data.length, 10000); // Limit for performance
        const positions = new Float32Array(particleCount * 3);
        const colors = new Float32Array(particleCount * 3);
        const sizes = new Float32Array(particleCount);
        
        // Find min/max for normalization
        let minRisk = Infinity, maxRisk = -Infinity;
        let minTemp = Infinity, maxTemp = -Infinity;
        
        for (let i = 0; i < particleCount; i++) {
            const point = data[i];
            if (point.fire_risk < minRisk) minRisk = point.fire_risk;
            if (point.fire_risk > maxRisk) maxRisk = point.fire_risk;
            if (point.temperature < minTemp) minTemp = point.temperature;
            if (point.temperature > maxTemp) maxTemp = point.temperature;
        }
        
        // Create particles
        for (let i = 0; i < particleCount; i++) {
            const point = data[i];
            
            // Convert lat/lon to 3D coordinates (simplified for demo)
            const lat = point.latitude || 0;
            const lon = point.longitude || 0;
            
            // Simple projection for demo purposes
            const x = (lon / 180) * 20;
            const y = (lat / 90) * 10;
            const z = (point.fire_risk - minRisk) / (maxRisk - minRisk) * 20;
            
            positions[i * 3] = x;
            positions[i * 3 + 1] = y;
            positions[i * 3 + 2] = z;
            
            // Color based on fire risk (red for high risk)
            const normalizedRisk = (point.fire_risk - minRisk) / (maxRisk - minRisk);
            colors[i * 3] = normalizedRisk; // R
            colors[i * 3 + 1] = 0.5 * (1 - normalizedRisk); // G
            colors[i * 3 + 2] = 0.2; // B
            
            // Size based on temperature
            const normalizedTemp = (point.temperature - minTemp) / (maxTemp - minTemp);
            sizes[i] = 2 + normalizedTemp * 8;
        }
        
        // Create geometry and material
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
        
        const material = new THREE.PointsMaterial({
            size: 1,
            vertexColors: true,
            transparent: true,
            opacity: 0.8,
            sizeAttenuation: true
        });
        
        // Create particle system
        this.particles = new THREE.Points(geometry, material);
        this.scene.add(this.particles);
    }
    
    updateDataPreview(data) {
        const previewElement = document.getElementById('data-preview');
        
        if (!data || data.length === 0) {
            previewElement.innerHTML = 'No data available';
            return;
        }
        
        // Create a simple table preview
        let html = '<table><thead><tr>';
        
        // Get column names from first row
        const columns = Object.keys(data[0]);
        columns.forEach(col => {
            html += `<th>${col}</th>`;
        });
        
        html += '</tr></thead><tbody>';
        
        // Show first 10 rows
        const rowsToShow = Math.min(data.length, 10);
        for (let i = 0; i < rowsToShow; i++) {
            html += '<tr>';
            columns.forEach(col => {
                html += `<td>${data[i][col].toFixed ? data[i][col].toFixed(2) : data[i][col]}</td>`;
            });
            html += '</tr>';
        }
        
        html += '</tbody></table>';
        
        if (data.length > 10) {
            html += `<p>Showing 10 of ${data.length} rows</p>`;
        }
        
        previewElement.innerHTML = html;
    }
}

// Initialize the application when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.visflow = new VisFlowEngine();
});