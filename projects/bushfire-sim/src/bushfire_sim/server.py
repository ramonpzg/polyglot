"""FastAPI server for real-time bushfire visualization."""

import asyncio
import json
import logging
from typing import Dict, List
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path
import uvicorn
from . import BushfireModel

# Set up logging
logger = logging.getLogger(__name__)

app = FastAPI(title="Bushfire Simulation")

# Mount static files
static_path = Path(__file__).parent / "static"
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Global simulation state
active_simulations: Dict[str, BushfireModel] = {}
active_connections: List[WebSocket] = []

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the main dashboard."""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bushfire Simulation</title>
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
        }
        button:hover { border-color: #666; cursor: pointer; }
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
        .simulation-area {
            flex: 1;
            border: 1px solid #333;
            padding: 15px;
            min-height: 500px;
            position: relative;
        }
        .stats-panel {
            width: 250px;
            border: 1px solid #333;
            padding: 15px;
        }
        .stat {
            margin-bottom: 15px;
        }
        .stat-label {
            font-size: 10px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .stat-value {
            font-size: 16px;
            margin-top: 3px;
        }
        #canvas {
            width: 100%;
            height: 400px;
            border: 1px solid #333;
            background: #111;
        }
        .legend {
            margin-top: 10px;
            display: flex;
            gap: 15px;
            font-size: 10px;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .legend-color {
            width: 12px;
            height: 12px;
            border: 1px solid #333;
        }
        .hidden { display: none; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔥 BUSHFIRE SIMULATION</h1>
    </div>
    
    <div class="controls">
        <select id="dangerSelect">
            <option value="moderate">Moderate</option>
            <option value="high">High</option>
            <option value="very_high">Very High</option>
            <option value="severe">Severe</option>
            <option value="extreme">Extreme</option>
            <option value="catastrophic">Catastrophic</option>
        </select>
        <button id="startBtn">START SIMULATION</button>
        <button id="stopBtn" class="hidden">STOP</button>
        <button id="resetBtn">RESET</button>
    </div>
    
    <div class="status" id="status">Select danger level and start simulation</div>
    
    <div class="main-content">
        <div class="simulation-area">
            <canvas id="canvas" width="400" height="400"></canvas>
            <div class="legend">
                <div class="legend-item">
                    <div class="legend-color" style="background: white;"></div>
                    <span>Empty</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: green;"></div>
                    <span>Vegetation</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: red;"></div>
                    <span>Burning</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #333;"></div>
                    <span>Burnt</span>
                </div>
            </div>
        </div>
        
        <div class="stats-panel">
            <div class="stat">
                <div class="stat-label">Step</div>
                <div class="stat-value" id="step">0</div>
            </div>
            <div class="stat">
                <div class="stat-label">Fire Spread</div>
                <div class="stat-value" id="fireSpread">0.0%</div>
            </div>
            <div class="stat">
                <div class="stat-label">Active Fires</div>
                <div class="stat-value" id="activeFires">0.0%</div>
            </div>
            <div class="stat">
                <div class="stat-label">Burnt Cells</div>
                <div class="stat-value" id="burntCells">0</div>
            </div>
            <div class="stat">
                <div class="stat-label">Burning Cells</div>
                <div class="stat-value" id="burningCells">0</div>
            </div>
        </div>
    </div>
    
    <script>
        class BushfireViz {
            constructor() {
                this.ws = null;
                this.canvas = document.getElementById('canvas');
                this.ctx = this.canvas.getContext('2d');
                this.size = 80;
                this.cellSize = this.canvas.width / this.size;
                
                this.colors = ['white', 'green', 'red', '#333'];
                
                this.bindEvents();
            }
            
            bindEvents() {
                document.getElementById('startBtn').addEventListener('click', () => this.start());
                document.getElementById('stopBtn').addEventListener('click', () => this.stop());
                document.getElementById('resetBtn').addEventListener('click', () => this.reset());
            }
            
            start() {
                const danger = document.getElementById('dangerSelect').value;
                this.setStatus('Connecting...');
                
                const wsUrl = `ws://localhost:8001/ws/${danger}`;
                this.ws = new WebSocket(wsUrl);
                
                this.ws.onopen = () => {
                    this.setStatus(`Simulating ${danger.toUpperCase()} conditions - LIVE`);
                    document.getElementById('startBtn').classList.add('hidden');
                    document.getElementById('stopBtn').classList.remove('hidden');
                };
                
                this.ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    this.updateVisualization(data);
                };
                
                this.ws.onerror = () => {
                    this.setStatus('Connection error');
                };
                
                this.ws.onclose = () => {
                    this.setStatus('Simulation stopped');
                };
            }
            
            stop() {
                if (this.ws) {
                    this.ws.close();
                }
                document.getElementById('startBtn').classList.remove('hidden');
                document.getElementById('stopBtn').classList.add('hidden');
            }
            
            reset() {
                this.stop();
                this.ctx.fillStyle = 'black';
                this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
                this.setStatus('Reset complete');
                
                // Reset stats
                document.getElementById('step').textContent = '0';
                document.getElementById('fireSpread').textContent = '0.0%';
                document.getElementById('activeFires').textContent = '0.0%';
                document.getElementById('burntCells').textContent = '0';
                document.getElementById('burningCells').textContent = '0';
            }
            
            setStatus(message) {
                document.getElementById('status').textContent = message;
            }
            
            updateVisualization(data) {
                // Update stats
                document.getElementById('step').textContent = data.stats.step;
                document.getElementById('fireSpread').textContent = data.stats.fire_spread_pct.toFixed(1) + '%';
                document.getElementById('activeFires').textContent = data.stats.active_fire_pct.toFixed(1) + '%';
                document.getElementById('burntCells').textContent = data.stats.burnt.toLocaleString();
                document.getElementById('burningCells').textContent = data.stats.burning.toLocaleString();
                
                // Draw grid
                const state = data.state;
                for (let y = 0; y < this.size; y++) {
                    for (let x = 0; x < this.size; x++) {
                        const cellValue = state[y * this.size + x];
                        this.ctx.fillStyle = this.colors[cellValue];
                        this.ctx.fillRect(
                            x * this.cellSize, 
                            y * this.cellSize, 
                            this.cellSize, 
                            this.cellSize
                        );
                    }
                }
            }
        }
        
        new BushfireViz();
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

@app.websocket("/ws/{danger_level}")
async def websocket_endpoint(websocket: WebSocket, danger_level: str):
    logger.info(f"New WebSocket connection for danger level: {danger_level}")
    await websocket.accept()
    
    # Create simulation
    model = BushfireModel(80, 80)
    try:
        conditions = model.set_conditions(danger_level)
        logger.info(f"Simulation conditions: {conditions}")
    except ValueError as e:
        logger.error(f"Invalid danger level: {e}")
        await websocket.send_text(json.dumps({"error": f"Invalid danger level: {danger_level}"}))
        return
    
    # Start fire at center
    model.ignite([(40, 40)])
    logger.info("Fire ignited at center (40, 40)")
    
    active_simulations[websocket] = model
    active_connections.append(websocket)
    
    step_count = 0
    try:
        while True:
            # Run one simulation step
            model.simulate_steps(1, save_history=False)
            step_count += 1
            
            # Get current state
            state = model.get_state()
            stats = model.get_stats()
            
            if step_count % 5 == 0:  # Log every 5 steps for better debugging
                logger.debug(f"Step {step_count}: {stats['burning']} burning, {stats['burnt']} burnt, {stats['fire_spread_pct']:.1f}% spread")
            
            # Send to client
            data = {
                "state": state.flatten().tolist(),
                "stats": stats
            }
            
            await websocket.send_text(json.dumps(data))
            await asyncio.sleep(0.2)  # 5 FPS
            
            # Stop if fire is out
            if stats['burning'] == 0:
                logger.info(f"Simulation complete after {step_count} steps")
                await asyncio.sleep(2)
                break
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if websocket in active_simulations:
            del active_simulations[websocket]
        if websocket in active_connections:
            active_connections.remove(websocket)
        logger.info("WebSocket connection closed")

@app.get("/api/danger-levels")
async def get_danger_levels():
    """Get available danger levels and their conditions."""
    from . import BushfireModel
    return {"danger_levels": BushfireModel.DANGER_LEVELS}

def run_server(host: str = "127.0.0.1", port: int = 8001, debug: bool = False, headless: bool = False):
    """Run the FastAPI server."""
    log_level = "debug" if debug else "error"
    
    if debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger.setLevel(logging.DEBUG)
    
    if headless:
        # Remove the dashboard route in headless mode
        from fastapi.routing import APIRoute
        app.routes = [route for route in app.routes if not (
            isinstance(route, APIRoute) and route.path == "/"
        )]
        logger.info("Running in headless mode (API-only)")
    
    uvicorn.run(app, host=host, port=port, log_level=log_level)

if __name__ == "__main__":
    run_server()
