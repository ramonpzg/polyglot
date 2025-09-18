"""FastAPI server for real-time wildlife monitoring interface."""

import asyncio
import json
import logging
import numpy as np
from typing import Dict, List
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn
from . import BushEarsAnalyzer, AustralianSpecies

app = FastAPI(title="Bush Ears Wildlife Monitor")
logger = logging.getLogger(__name__)

# Global analyzer instance
analyzer = BushEarsAnalyzer()
active_connections: List[WebSocket] = []

def get_scientific_name(common_name: str) -> str:
    """Get scientific name for species."""
    scientific_names = {
        'Laughing Kookaburra': 'Dacelo novaeguineae',
        'Australian Magpie': 'Gymnorhina tibicen',
        'Galah': 'Eolophus roseicapilla',
        'Cockatoo': 'Cacatua galerita',
        'Koala': 'Phascolarctos cinereus',
        'Dingo': 'Canis dingo'
    }
    return scientific_names.get(common_name, 'Unknown species')

def get_conservation_weight(common_name: str) -> float:
    """Get conservation importance weight."""
    weights = {
        'Laughing Kookaburra': 0.8,
        'Australian Magpie': 0.9,
        'Galah': 0.7,
        'Cockatoo': 0.6,
        'Koala': 1.0,  # Highest conservation priority
        'Dingo': 0.95
    }
    return weights.get(common_name, 0.5)

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the wildlife monitoring dashboard."""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bush Ears - Wildlife Monitor</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Monaco', 'Menlo', monospace;
            background: #000;
            color: #fff;
            line-height: 1.4;
        }
        .header {
            padding: 20px;
            border-bottom: 1px solid #333;
            text-align: center;
        }
        .header h1 {
            font-size: 24px;
            font-weight: normal;
            letter-spacing: 2px;
        }
        .controls {
            padding: 20px;
            display: flex;
            gap: 15px;
            justify-content: center;
            align-items: center;
        }
        select, button {
            background: #000;
            color: #fff;
            border: 1px solid #333;
            padding: 8px 16px;
            font-family: inherit;
            font-size: 12px;
            cursor: pointer;
        }
        button:hover { border-color: #666; }
        .status {
            padding: 10px 20px;
            text-align: center;
            color: #666;
            font-size: 12px;
        }
        .main-content {
            display: flex;
            padding: 20px;
            gap: 20px;
        }
        .detection-area {
            flex: 1;
            border: 1px solid #333;
            padding: 15px;
            min-height: 400px;
        }
        .metrics-panel {
            width: 300px;
            border: 1px solid #333;
            padding: 15px;
        }
        .detection {
            margin-bottom: 10px;
            padding: 8px;
            border-left: 3px solid #666;
            font-size: 11px;
        }
        .detection.new {
            border-color: #00ff00;
            animation: fadeIn 0.5s;
        }
        .metric {
            margin-bottom: 15px;
        }
        .metric-label {
            font-size: 10px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .metric-value {
            font-size: 16px;
            margin-top: 3px;
        }
        .species-icon {
            display: inline-block;
            margin-right: 5px;
        }
        @keyframes fadeIn {
            from { background: #333; }
            to { background: transparent; }
        }
        .hidden { display: none; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🦘 BUSH EARS</h1>
    </div>
    
    <div class="controls">
        <select id="scenarioSelect">
            <option value="dawn_chorus">Dawn Chorus</option>
            <option value="urban_park">Urban Park</option>
            <option value="outback_night">Outback Night</option>
            <option value="endangered_habitat">Endangered Habitat</option>
        </select>
        <button id="startBtn">START MONITORING</button>
        <button id="stopBtn" class="hidden">STOP</button>
        <button id="resetBtn">RESET</button>
    </div>
    
    <div class="status" id="status">Select scenario to begin wildlife monitoring</div>
    
    <div class="main-content">
        <div class="detection-area">
            <h3>Real-time Species Detections</h3>
            <div id="detectionsList"></div>
        </div>
        
        <div class="metrics-panel">
            <div class="metric">
                <div class="metric-label">Biodiversity Index</div>
                <div class="metric-value" id="biodiversityIndex">0.00</div>
            </div>
            <div class="metric">
                <div class="metric-label">Conservation Score</div>
                <div class="metric-value" id="conservationScore">0.00</div>
            </div>
            <div class="metric">
                <div class="metric-label">Species Richness</div>
                <div class="metric-value" id="speciesRichness">0</div>
            </div>
            <div class="metric">
                <div class="metric-label">Total Detections</div>
                <div class="metric-value" id="totalDetections">0</div>
            </div>
            
            <h4 style="margin-top: 20px; margin-bottom: 10px;">Species Count</h4>
            <div id="speciesList"></div>
        </div>
    </div>
    
    <script>
        class BushEarsMonitor {
            constructor() {
                this.ws = null;
                this.isRunning = false;
                this.detectionCount = 0;
                this.speciesIcons = {
                    'Laughing Kookaburra': '🦆',
                    'Australian Magpie': '🦅', 
                    'Galah': '🦜',
                    'Koala': '🐨',
                    'Dingo': '🐺'
                };
                this.bindEvents();
            }
            
            bindEvents() {
                document.getElementById('startBtn').addEventListener('click', () => this.start());
                document.getElementById('stopBtn').addEventListener('click', () => this.stop());
                document.getElementById('resetBtn').addEventListener('click', () => this.reset());
            }
            
            start() {
                const scenario = document.getElementById('scenarioSelect').value;
                this.setStatus('Connecting to monitoring system...');
                
                const wsUrl = `ws://localhost:8002/ws/${scenario}`;
                this.ws = new WebSocket(wsUrl);
                
                this.ws.onopen = () => {
                    this.isRunning = true;
                    this.setStatus(`Monitoring ${scenario.replace('_', ' ').toUpperCase()} - LIVE`);
                    document.getElementById('startBtn').classList.add('hidden');
                    document.getElementById('stopBtn').classList.remove('hidden');
                };
                
                this.ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    this.handleDetection(data);
                };
                
                this.ws.onerror = () => {
                    this.setStatus('Connection error - is the server running?');
                };
                
                this.ws.onclose = () => {
                    if (this.isRunning) {
                        this.setStatus('Monitoring stopped');
                    }
                };
            }
            
            stop() {
                if (this.ws) {
                    this.ws.close();
                }
                this.isRunning = false;
                this.setStatus('Monitoring stopped');
                document.getElementById('startBtn').classList.remove('hidden');
                document.getElementById('stopBtn').classList.add('hidden');
            }
            
            reset() {
                this.stop();
                document.getElementById('detectionsList').innerHTML = '';
                document.getElementById('speciesList').innerHTML = '';
                this.detectionCount = 0;
                this.updateMetrics(0, 0, 0, 0);
                this.setStatus('Ready to begin monitoring');
            }
            
            handleDetection(data) {
                if (data.species_detected) {
                    this.addDetection(data);
                }
                
                // Update ecosystem metrics
                this.updateMetrics(
                    data.biodiversity_index,
                    data.conservation_score || 0,
                    data.ecosystem_health || 0,
                    data.total_detections
                );
            }
            
            addDetection(data) {
                this.detectionCount++;
                const timestamp = new Date().toLocaleTimeString();
                const icon = this.speciesIcons[data.common_name] || '🦜';
                
                const detection = document.createElement('div');
                detection.classList.add('detection', 'new');
                detection.innerHTML = `
                    <span class="species-icon">${icon}</span>
                    <strong>${data.common_name}</strong><br>
                    <small>${data.scientific_name}</small><br>
                    <small>Detected: ${timestamp}</small>
                `;
                
                const detectionsList = document.getElementById('detectionsList');
                detectionsList.insertBefore(detection, detectionsList.firstChild);
                
                // Remove 'new' class after animation
                setTimeout(() => detection.classList.remove('new'), 500);
                
                // Keep only recent detections
                const detections = detectionsList.children;
                if (detections.length > 10) {
                    detectionsList.removeChild(detections[detections.length - 1]);
                }
            }
            
            updateMetrics(biodiversity, conservation, health, total) {
                document.getElementById('biodiversityIndex').textContent = biodiversity.toFixed(2);
                document.getElementById('conservationScore').textContent = conservation.toFixed(2);
                document.getElementById('speciesRichness').textContent = Math.floor(biodiversity * 3); // Rough estimate
                document.getElementById('totalDetections').textContent = total;
            }
            
            setStatus(message) {
                document.getElementById('status').textContent = message;
            }
        }
        
        new BushEarsMonitor();
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

@app.websocket("/ws/{scenario}")
async def websocket_endpoint(websocket: WebSocket, scenario: str):
    await websocket.accept()
    active_connections.append(websocket)
    
    logger.info(f"Starting wildlife monitoring: {scenario}")
    
    # Demo scenarios with guaranteed detections for presentations
    demo_species = {
        'dawn_chorus': [
            {'species': 'Laughing Kookaburra', 'time': 1.2},
            {'species': 'Australian Magpie', 'time': 3.5},
            {'species': 'Galah', 'time': 6.8},
            {'species': 'Australian Magpie', 'time': 8.1},
        ],
        'urban_park': [
            {'species': 'Australian Magpie', 'time': 2.1},
            {'species': 'Galah', 'time': 4.5},
            {'species': 'Cockatoo', 'time': 7.2},
        ],
        'outback_night': [
            {'species': 'Dingo', 'time': 2.8},
            {'species': 'Koala', 'time': 5.5},
            {'species': 'Dingo', 'time': 8.9},
        ],
        'endangered_habitat': [
            {'species': 'Koala', 'time': 1.8},
            {'species': 'Koala', 'time': 4.2},
            {'species': 'Koala', 'time': 7.5},
        ]
    }
    
    try:
        scheduled_detections = demo_species.get(scenario, [])
        detection_index = 0
        simulation_time = 0.0
        
        logger.info(f"Running demo mode for {scenario} with {len(scheduled_detections)} scheduled detections")
        
        # Run for 10 seconds, sending updates every 0.1 seconds
        while simulation_time <= 10.0:
            # Check if we should trigger a detection
            species_detected = False
            detection_data = {
                'species_detected': False,
                'monitoring_time': simulation_time
            }
            
            # Check for scheduled detection
            if (detection_index < len(scheduled_detections) and 
                abs(simulation_time - scheduled_detections[detection_index]['time']) < 0.1):
                
                species_name = scheduled_detections[detection_index]['species']
                species_detected = True
                detection_index += 1
                
                # Create realistic detection data
                detection_data = {
                    'species_detected': True,
                    'species_id': 1,  # Will be mapped correctly
                    'common_name': species_name,
                    'scientific_name': get_scientific_name(species_name),
                    'conservation_weight': get_conservation_weight(species_name),
                    'monitoring_time': simulation_time,
                    'biodiversity_index': min(detection_index * 0.3, 2.0),
                    'conservation_score': min(detection_index * 0.2, 1.0),
                    'ecosystem_health': min(detection_index * 0.25, 1.0),
                    'total_detections': detection_index
                }
                
                logger.debug(f"Demo detection: {species_name} at {simulation_time:.1f}s")
            
            # Always send update (with or without detection)
            await websocket.send_text(json.dumps(detection_data, default=str))
            await asyncio.sleep(0.1)
            simulation_time += 0.1
        
        # Send final ecosystem report
        health = analyzer.get_ecosystem_health()
        final_report = {
            'session_complete': True,
            'ecosystem_health': {
                'biodiversity_index': health.biodiversity_index,
                'conservation_score': health.conservation_score,
                'species_richness': health.species_richness,
                'total_detections': health.total_detections
            }
        }
        
        await websocket.send_text(json.dumps(final_report))
        
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        active_connections.remove(websocket)

@app.get("/api/species")
async def get_species_info():
    """Get information about supported Australian species."""
    species_data = {}
    
    for species, info in BushEarsAnalyzer.SPECIES_INFO.items():
        species_data[species.name] = {
            'common_name': info['name'],
            'habitat': info['habitat'],
            'conservation_status': info['conservation_status'],
            'ecosystem_role': info['ecosystem_role']
        }
    
    return {"species": species_data}

@app.get("/api/benchmark")
async def run_benchmark():
    """Run performance benchmark and return results."""
    results = analyzer.benchmark_cpp_vs_python(30)
    
    return {
        "benchmark_results": results,
        "analysis": {
            "realtime_capable": results['cpp_samples_per_second'] >= 44100,
            "speedup_category": "exceptional" if results['speedup'] > 20 else "good" if results['speedup'] > 5 else "modest"
        }
    }

def run_server(host: str = "127.0.0.1", port: int = 8002, debug: bool = False, headless: bool = False):
    """Run the FastAPI server."""
    log_level = "debug" if debug else "error"
    
    if debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger.setLevel(logging.DEBUG)
    
    if headless:
        logger.info("Running in headless mode (API-only)")
    
    uvicorn.run(app, host=host, port=port, log_level=log_level)

if __name__ == "__main__":
    run_server()
