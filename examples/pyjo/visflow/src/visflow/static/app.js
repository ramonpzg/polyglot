/**
 * VisFlow - 3D Interactive Data Visualization Engine
 * 
 * Main application combining Monaco Editor, Three.js visualization,
 * and WebSocket communication with Python backend.
 */

class VisflowEngine {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.websocket = null;
        this.editor = null;
        
        // Application state
        this.datasets = new Map();
        this.currentVisualization = null;
        this.isConnected = false;
        
        // Performance tracking
        this.frameCount = 0;
        this.lastTime = performance.now();
        
        // Settings
        this.settings = {
            autoRun: false,
            theme: 'vs-dark',
            antiAliasing: true,
            shadows: true,
            maxParticles: 100000
        };
        
        this.initializeApplication();
    }
    
    async initializeApplication() {
        console.log('🚀 Initializing VisFlow...');
        
        // Wait for Monaco to be ready
        await this.waitForMonaco();
        
        // Initialize components
        this.initializeThreeJS();
        this.initializeMonacoEditor();
        this.initializeWebSocket();
        this.initializeEventListeners();
        this.initializeUI();
        
        console.log('✅ VisFlow initialized successfully!');
        this.logToConsole('VisFlow initialized successfully!', 'info');
    }
    
    waitForMonaco() {
        return new Promise((resolve) => {
            if (window.monaco) {
                resolve();
            } else {
                window.addEventListener('monaco-ready', resolve);
            }
        });
    }
    
    // Three.js Initialization
    initializeThreeJS() {
        const canvas = document.getElementById('three-canvas');
        const container = canvas.parentElement;
        
        // Scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x1a1a1a);
        
        // Camera
        this.camera = new THREE.PerspectiveCamera(
            75, 
            container.clientWidth / container.clientHeight, 
            0.1, 
            10000
        );
        this.camera.position.set(50, 50, 50);
        
        // Renderer
        this.renderer = new THREE.WebGLRenderer({
            canvas: canvas,
            antialias: this.settings.antiAliasing,
            alpha: true
        });
        this.renderer.setSize(container.clientWidth, container.clientHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.shadowMap.enabled = this.settings.shadows;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        
        // Controls
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.maxDistance = 1000;
        
        // Lighting
        this.addLighting();
        
        // Grid and axes helpers
        this.addHelpers();
        
        // Start render loop
        this.animate();
        
        // Handle window resize
        window.addEventListener('resize', () => this.onWindowResize());
        
        console.log('🎨 Three.js initialized');
    }
    
    addLighting() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
        this.scene.add(ambientLight);
        
        // Directional light
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(100, 100, 50);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        this.scene.add(directionalLight);
        
        // Point lights for better illumination
        const pointLight1 = new THREE.PointLight(0x4080ff, 0.3, 1000);
        pointLight1.position.set(-50, 50, 50);
        this.scene.add(pointLight1);
        
        const pointLight2 = new THREE.PointLight(0xff4080, 0.3, 1000);
        pointLight2.position.set(50, -50, 50);
        this.scene.add(pointLight2);
    }
    
    addHelpers() {
        // Grid
        const gridHelper = new THREE.GridHelper(200, 20, 0x444444, 0x222222);
        gridHelper.name = 'gridHelper';
        this.scene.add(gridHelper);
        
        // Axes helper
        const axesHelper = new THREE.AxesHelper(50);
        axesHelper.name = 'axesHelper';
        this.scene.add(axesHelper);
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        this.controls.update();
        this.renderer.render(this.scene, this.camera);
        
        // Update FPS counter
        this.frameCount++;
        const currentTime = performance.now();
        if (currentTime - this.lastTime >= 1000) {
            const fps = Math.round((this.frameCount * 1000) / (currentTime - this.lastTime));
            document.getElementById('fps-counter').textContent = fps;
            this.frameCount = 0;
            this.lastTime = currentTime;
        }
        
        // Update stats
        this.updateVisualizationStats();
    }
    
    onWindowResize() {
        const container = this.renderer.domElement.parentElement;
        this.camera.aspect = container.clientWidth / container.clientHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(container.clientWidth, container.clientHeight);
    }
    
    // Monaco Editor Initialization
    initializeMonacoEditor() {
        const editorContainer = document.getElementById('code-editor');
        
        this.editor = monaco.editor.create(editorContainer, {
            value: this.getDefaultCode(),
            language: 'python',
            theme: this.settings.theme,
            automaticLayout: true,
            fontSize: 14,
            minimap: { enabled: true },
            scrollBeyondLastLine: false,
            wordWrap: 'on'
        });
        
        // Add keyboard shortcuts
        this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyR, () => {
            this.executeCode();
        });
        
        // Auto-run on changes (if enabled)
        this.editor.onDidChangeModelContent(() => {
            if (this.settings.autoRun) {
                clearTimeout(this.autoRunTimeout);
                this.autoRunTimeout = setTimeout(() => this.executeCode(), 1000);
            }
        });
        
        console.log('⌨️ Monaco Editor initialized');
    }
    
    getDefaultCode() {
        return `# Welcome to VisFlow!
# 3D Interactive Data Visualization Studio

# Example: Create a simple particle system
import pandas as pd
import numpy as np

# Sample data - replace with your uploaded dataset
data = pd.DataFrame({
    'x': np.random.normal(0, 10, 1000),
    'y': np.random.normal(0, 10, 1000),
    'z': np.random.normal(0, 10, 1000),
    'value': np.random.uniform(0, 100, 1000)
})

# Create 3D positions
positions = data[['x', 'y', 'z']].values

# Create colors based on values
colors = create_heatmap_colors(data['value'], 'viridis')

# Create particle system for Three.js
viz_data = create_particle_system(
    positions=positions,
    colors=colors,
    sizes=data['value'] / 20,  # Size based on value
    material='points'
)

print(f"Created particle system with {len(positions)} points")
print(f"Value range: {data['value'].min():.2f} - {data['value'].max():.2f}")`;
    }
    
    // WebSocket Communication
    initializeWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        this.connectWebSocket(wsUrl);
    }
    
    connectWebSocket(url) {
        this.websocket = new WebSocket(url);
        
        this.websocket.onopen = () => {
            console.log('🔌 WebSocket connected');
            this.isConnected = true;
            this.updateConnectionStatus(true);
            this.logToConsole('Connected to VisFlow server', 'success');
        };
        
        this.websocket.onmessage = (event) => {
            this.handleWebSocketMessage(JSON.parse(event.data));
        };
        
        this.websocket.onclose = () => {
            console.log('🔌 WebSocket disconnected');
            this.isConnected = false;
            this.updateConnectionStatus(false);
            this.logToConsole('Disconnected from server', 'warning');
            
            // Attempt to reconnect after 3 seconds
            setTimeout(() => this.connectWebSocket(url), 3000);
        };
        
        this.websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.logToConsole('WebSocket connection error', 'error');
        };
    }
    
    handleWebSocketMessage(message) {
        switch (message.type) {
            case 'code_execution_result':
                this.handleCodeExecutionResult(message.data);
                break;
            case 'code_execution_error':
                this.handleCodeExecutionError(message.data);
                break;
            case 'dataset_uploaded':
                this.handleDatasetUploaded(message.data);
                break;
            case 'dataset_deleted':
                this.handleDatasetDeleted(message.data);
                break;
            default:
                console.log('Unknown message type:', message.type);
        }
    }
    
    // Event Listeners
    initializeEventListeners() {
        // File upload
        document.getElementById('file-input').addEventListener('change', (e) => {
            this.handleFileUpload(e);
        });
        
        // Navigation buttons
        document.getElementById('file-upload-btn').addEventListener('click', () => {
            document.getElementById('file-input').click();
        });
        
        document.getElementById('examples-btn').addEventListener('click', () => {
            this.showExamplesModal();
        });
        
        document.getElementById('settings-btn').addEventListener('click', () => {
            this.showSettingsModal();
        });
        
        // Code execution
        document.getElementById('run-code-btn').addEventListener('click', () => {
            this.executeCode();
        });
        
        document.getElementById('clear-editor-btn').addEventListener('click', () => {
            this.editor.setValue('');
        });
        
        // Visualization controls
        document.getElementById('reset-camera-btn').addEventListener('click', () => {
            this.resetCamera();
        });
        
        document.getElementById('screenshot-btn').addEventListener('click', () => {
            this.takeScreenshot();
        });
        
        // Example buttons
        document.querySelectorAll('.example-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.loadExample(e.target.dataset.example);
            });
        });
        
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });
        
        // Bottom panel toggle
        document.getElementById('bottom-panel-toggle').addEventListener('click', () => {
            this.toggleBottomPanel();
        });
        
        // Modal close buttons
        document.querySelectorAll('.close-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.closeModal(e.target.dataset.modal);
            });
        });
        
        // Welcome screen
        document.getElementById('load-bushfire-example').addEventListener('click', () => {
            this.loadBushfireExample();
        });
        
        console.log('🎯 Event listeners initialized');
    }
    
    // UI Management
    initializeUI() {
        this.initializeResizer();
        this.loadSettings();
        this.hideWelcomeScreen();
        
        // Show welcome screen initially if no datasets
        if (this.datasets.size === 0) {
            this.showWelcomeScreen();
        }
    }
    
    initializeResizer() {
        const resizer = document.getElementById('horizontal-resizer');
        const leftPanel = document.getElementById('left-panel');
        let isResizing = false;
        
        resizer.addEventListener('mousedown', (e) => {
            isResizing = true;
            document.addEventListener('mousemove', handleMouseMove);
            document.addEventListener('mouseup', handleMouseUp);
        });
        
        const handleMouseMove = (e) => {
            if (!isResizing) return;
            
            const containerWidth = document.querySelector('.main-container').offsetWidth;
            const newWidth = (e.clientX / containerWidth) * 100;
            
            if (newWidth > 20 && newWidth < 80) {
                leftPanel.style.width = newWidth + '%';
                document.querySelector('.right-panel').style.width = (100 - newWidth) + '%';
            }
        };
        
        const handleMouseUp = () => {
            isResizing = false;
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
        };
    }
    
    // File Operations
    async handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        this.showLoading();
        this.logToConsole(`Uploading file: ${file.name}`, 'info');
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`Upload failed: ${response.statusText}`);
            }
            
            const result = await response.json();
            this.logToConsole(`File uploaded successfully: ${result.filename}`, 'success');
            
        } catch (error) {
            this.logToConsole(`Upload error: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    handleDatasetUploaded(data) {
        this.datasets.set(data.dataset_id, data);
        this.updateDatasetSelector();
        this.hideWelcomeScreen();
        this.logToConsole(`Dataset loaded: ${data.filename} (${data.info.shape[0]} rows, ${data.info.shape[1]} columns)`, 'success');
    }
    
    // Code Execution
    async executeCode() {
        if (!this.isConnected) {
            this.logToConsole('Not connected to server', 'error');
            return;
        }
        
        const code = this.editor.getValue();
        if (!code.trim()) {
            this.logToConsole('No code to execute', 'warning');
            return;
        }
        
        this.showLoading();
        this.logToConsole('Executing Python code...', 'info');
        
        try {
            const response = await fetch('/execute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    code: code,
                    data_context: {}
                })
            });
            
            const result = await response.json();
            this.handleCodeExecutionResult(result);
            
        } catch (error) {
            this.handleCodeExecutionError({ error: error.message });
        } finally {
            this.hideLoading();
        }
    }
    
    handleCodeExecutionResult(result) {
        if (result.success) {
            this.logToConsole('Code executed successfully', 'success');
            
            // Display Python output
            if (result.output) {
                document.getElementById('python-output-content').textContent = result.output;
                this.switchTab('output');
            }
            
            // Handle visualization data
            if (result.visualization_data) {
                this.updateVisualization(result.visualization_data);
            }
            
        } else {
            this.handleCodeExecutionError(result);
        }
    }
    
    handleCodeExecutionError(error) {
        this.logToConsole(`Execution error: ${error.error}`, 'error');
        
        // Show error in output tab
        let errorText = `Error: ${error.error}\n`;
        if (error.traceback) {
            errorText += `\nTraceback:\n${error.traceback}`;
        }
        if (error.output) {
            errorText += `\nOutput:\n${error.output}`;
        }
        
        document.getElementById('python-output-content').textContent = errorText;
        this.switchTab('output');
    }
    
    // Visualization Updates
    updateVisualization(vizData) {
        // Clear previous visualization
        this.clearVisualization();
        
        if (Array.isArray(vizData)) {
            vizData.forEach(data => this.createVisualizationObject(data));
        } else {
            this.createVisualizationObject(vizData);
        }
        
        this.hideWelcomeScreen();
        this.logToConsole('Visualization updated', 'success');
    }
    
    createVisualizationObject(data) {
        switch (data.type) {
            case 'particles':
            case 'particle_system':
                this.createParticleSystem(data);
                break;
            case 'mesh':
                this.createMeshVisualization(data);
                break;
            case 'lines':
                this.createLineVisualization(data);
                break;
            default:
                console.warn('Unknown visualization type:', data.type);
        }
    }
    
    createParticleSystem(data) {
        const positions = new Float32Array(data.positions.flat());
        const colors = data.colors ? new Float32Array(data.colors.flat()) : null;
        const sizes = data.sizes ? new Float32Array(data.sizes) : null;
        
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        
        if (colors) {
            geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        }
        
        if (sizes) {
            geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
        }
        
        const material = new THREE.PointsMaterial({
            size: data.point_size || 2,
            vertexColors: colors ? true : false,
            color: colors ? 0xffffff : (data.color || 0x4080ff),
            transparent: true,
            opacity: data.opacity || 0.8,
            sizeAttenuation: true
        });
        
        const points = new THREE.Points(geometry, material);
        points.name = 'visualization';
        this.scene.add(points);
        
        this.currentVisualization = points;
    }
    
    createMeshVisualization(data) {
        const vertices = new Float32Array(data.vertices.flat());
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
        
        if (data.faces) {
            const indices = new Uint32Array(data.faces.flat());
            geometry.setIndex(new THREE.BufferAttribute(indices, 1));
        }
        
        if (data.colors) {
            const colors = new Float32Array(data.colors.flat());
            geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        }
        
        geometry.computeVertexNormals();
        
        const material = new THREE.MeshPhongMaterial({
            color: data.color || 0x4080ff,
            vertexColors: data.colors ? true : false,
            transparent: true,
            opacity: data.opacity || 0.8,
            wireframe: data.wireframe || false
        });
        
        const mesh = new THREE.Mesh(geometry, material);
        mesh.name = 'visualization';
        this.scene.add(mesh);
        
        this.currentVisualization = mesh;
    }
    
    createLineVisualization(data) {
        const points = data.points.map(p => new THREE.Vector3(p[0], p[1], p[2]));
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        
        if (data.colors) {
            const colors = new Float32Array(data.colors.flat());
            geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        }
        
        const material = new THREE.LineBasicMaterial({
            color: data.color || 0x4080ff,
            vertexColors: data.colors ? true : false,
            linewidth: data.linewidth || 1
        });
        
        const lines = new THREE.Line(geometry, material);
        lines.name = 'visualization';
        this.scene.add(lines);
        
        this.currentVisualization = lines;
    }
    
    clearVisualization() {
        const vizObjects = this.scene.children.filter(child => child.name === 'visualization');
        vizObjects.forEach(obj => {
            this.scene.remove(obj);
            if (obj.geometry) obj.geometry.dispose();
            if (obj.material) obj.material.dispose();
        });
        this.currentVisualization = null;
    }
    
    // Utility Functions
    updateConnectionStatus(connected) {
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('status-text');
        
        if (connected) {
            statusDot.className = 'status-dot online';
            statusText.textContent = 'Connected';
        } else {
            statusDot.className = 'status-dot offline';
            statusText.textContent = 'Disconnected';
        }
    }
    
    showLoading() {
        document.getElementById('loading-overlay').classList.add('active');
    }
    
    hideLoading() {
        document.getElementById('loading-overlay').classList.remove('active');
    }
    
    showWelcomeScreen() {
        document.getElementById('welcome-screen').classList.add('active');
    }
    
    hideWelcomeScreen() {
        document.getElementById('welcome-screen').classList.remove('active');
    }
    
    logToConsole(message, type = 'info') {
        const logsContent = document.getElementById('logs-content');
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = `[${timestamp}] ${type.toUpperCase()}: ${message}\n`;
        
        logsContent.textContent += logEntry;
        logsContent.scrollTop = logsContent.scrollHeight;
        
        console.log(`[VisFlow] ${message}`);
    }
    
    switchTab(tabName) {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });
        
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.toggle('active', content.id === `${tabName}-tab`);
        });
    }
    
    updateVisualizationStats() {
        const objects = this.scene.children.filter(child => child.name === 'visualization').length;
        const triangles = this.currentVisualization && this.currentVisualization.geometry 
            ? (this.currentVisualization.geometry.index ? this.currentVisualization.geometry.index.count / 3 : 0)
            : 0;
        
        document.getElementById('object-count').textContent = objects;
        document.getElementById('triangle-count').textContent = Math.floor(triangles);
    }
    
    resetCamera() {
        this.camera.position.set(50, 50, 50);
        this.camera.lookAt(0, 0, 0);
        this.controls.target.set(0, 0, 0);
        this.controls.update();
    }
    
    takeScreenshot() {
        this.renderer.render(this.scene, this.camera);
        const canvas = this.renderer.domElement;
        
        canvas.toBlob((blob) => {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `visflow-screenshot-${Date.now()}.png`;
            a.click();
            URL.revokeObjectURL(url);
        });
        
        this.logToConsole('Screenshot saved', 'success');
    }
    
    // Example Loading
    loadExample(exampleType) {
        const examples = {
            'fire-risk': `# Fire Risk Calculation Example
import pandas as pd
import numpy as np

# Simulate bushfire weather data
n_points = 5000
data = pd.DataFrame({
    'lat': np.random.uniform(-37.5, -36.5, n_points),  # Melbourne region
    'lon': np.random.uniform(144.5, 145.5, n_points),
    'temperature': np.random.normal(35, 8, n_points),  # Hot day
    'humidity': np.random.normal(30, 15, n_points),    # Low humidity
    'wind_speed': np.random.exponential(15, n_points)  # Variable wind
})

# Calculate fire risk score
data['fire_risk'] = calculate_fire_risk(data['temperature'], data['humidity'], data['wind_speed'])

# Create 3D positions (scale lat/lon for visualization)
positions = np.column_stack([
    (data['lon'] - data['lon'].mean()) * 100,
    (data['lat'] - data['lat'].mean()) * 100,
    data['fire_risk'] / 2  # Height based on risk
])

# Color by fire risk
colors = create_heatmap_colors(data['fire_risk'], 'fire')

# Create visualization
viz_data = create_particle_system(
    positions=positions,
    colors=colors,
    sizes=data['fire_risk'] / 10,
    point_size=3
)

print(f"Fire risk visualization with {len(data)} points")
print(f"Risk range: {data['fire_risk'].min():.1f} - {data['fire_risk'].max():.1f}")`,

            'particle-system': `# Particle System Example
import pandas as pd
import numpy as np

# Create a spiral particle system
n = 10000
t = np.linspace(0, 4*np.pi, n)
r = np.linspace(0, 50, n)

positions = np.column_stack([
    r * np.cos(t),
    r * np.sin(t),
    t * 5
])

# Colors transition from blue to red
colors = np.zeros((n, 3))
colors[:, 0] = t / (4*np.pi)  # Red increases
colors[:, 2] = 1 - t / (4*np.pi)  # Blue decreases

# Sizes vary with distance
sizes = np.ones(n) * 2

viz_data = create_particle_system(
    positions=positions,
    colors=colors,
    sizes=sizes
)

print(f"Created spiral with {n} particles")`,

            'heatmap': `# 3D Heatmap Example
import pandas as pd
import numpy as np

# Create a grid of temperature data
x = np.linspace(-25, 25, 50)
y = np.linspace(-25, 25, 50)
X, Y = np.meshgrid(x, y)

# Temperature function (peaks and valleys)
Z = 20 * np.exp(-(X**2 + Y**2)/200) + 10 * np.exp(-((X-10)**2 + (Y-10)**2)/100)

# Flatten for particle system
positions = np.column_stack([X.flatten(), Y.flatten(), Z.flatten()])

# Create temperature-based colors
temp_colors = create_heatmap_colors(pd.Series(Z.flatten()), 'fire')

viz_data = create_particle_system(
    positions=positions,
    colors=temp_colors,
    sizes=Z.flatten() / 5
)

print(f"Temperature heatmap: {len(positions)} points")
print(f"Temperature range: {Z.min():.1f}°C - {Z.max():.1f}°C")`
        };
        
        if (examples[exampleType]) {
            this.editor.setValue(examples[exampleType]);
            this.logToConsole(`Loaded ${exampleType} example`, 'info');
        }
    }
    
    loadBushfireExample() {
        this.loadExample('fire-risk');
        setTimeout(() => this.executeCode(), 500);
    }
    
    // Modal Management
    showExamplesModal() {
        document.getElementById('examples-modal').classList.add('active');
    }
    
    showSettingsModal() {
        document.getElementById('settings-modal').classList.add('active');
    }
    
    closeModal(modalId) {
        document.getElementById(modalId).classList.remove('active');
    }
    
    // Settings Management
    loadSettings() {
        const savedSettings = localStorage.getItem('visflow-settings');
        if (savedSettings) {
            this.settings = { ...this.settings, ...JSON.parse(savedSettings) };
        }
        
        // Apply settings to UI
        document.getElementById('auto-run-checkbox').checked = this.settings.autoRun;
        document.getElementById('theme-select').value = this.settings.theme;
        document.getElementById('anti-aliasing-checkbox').checked = this.settings.antiAliasing;
        document.getElementById('shadows-checkbox').checked = this.settings.shadows;
        document.getElementById('max-particles-input').value = this.settings.maxParticles;
    }
    
    saveSettings() {
        localStorage.setItem('visflow-settings', JSON.stringify(this.settings));
    }
    
    // UI Helpers
    toggleBottomPanel() {
        const panel = document.getElementById('bottom-panel');
        const content = document.getElementById('bottom-content');
        const isCollapsed = panel.classList.contains('collapsed');
        
        if (isCollapsed) {
            panel.classList.remove('collapsed');
            content.style.display = 'block';
        } else {
            panel.classList.add('collapsed');
            content.style.display = 'none';
        }
    }
    
    updateDatasetSelector() {
        const select = document.getElementById('dataset-select');
        select.innerHTML = '<option value="">Select dataset...</option>';
        
        for (const [id, dataset] of this.datasets) {
            const option = document.createElement('option');
            option.value = id;
            option.textContent = `${dataset.filename} (${dataset.info.shape[0]} rows)`;
            select.appendChild(option);
        }
    }
}

// Initialize VisFlow when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.visflow = new VisflowEngine();
});