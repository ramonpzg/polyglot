"""FastAPI server for outback monitoring dashboard."""

import asyncio
import json
import numpy as np
from datetime import datetime
from typing import Dict, List
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(title="Outback Monitor")

# Mount static files
from pathlib import Path
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Australian regions for simulation
REGIONS = {
    "queensland": {"temp_base": 28, "humidity_base": 70, "rainfall_base": 5},
    "nsw": {"temp_base": 24, "humidity_base": 60, "rainfall_base": 3},
    "victoria": {"temp_base": 20, "humidity_base": 65, "rainfall_base": 4},
    "sa": {"temp_base": 26, "humidity_base": 55, "rainfall_base": 2},
    "wa": {"temp_base": 30, "humidity_base": 45, "rainfall_base": 1},
}

class DataSimulator:
    def __init__(self, region: str):
        self.region = region
        self.config = REGIONS[region]
        self.time_step = 0
    
    def generate_data(self) -> Dict:
        """Generate realistic agricultural data with some randomness."""
        self.time_step += 1
        
        # Add daily cycles and noise
        temp_cycle = 5 * np.sin(self.time_step * 0.1) + np.random.normal(0, 2)
        humidity_noise = np.random.normal(0, 8)
        rainfall_burst = max(0, np.random.normal(0, 3))
        
        temp = max(0, self.config["temp_base"] + temp_cycle)
        humidity = np.clip(self.config["humidity_base"] + humidity_noise, 20, 100)
        rainfall = max(0, self.config["rainfall_base"] + rainfall_burst)
        
        # Derived metrics
        soil_moisture = min(100, max(10, 80 - (temp - 20) + rainfall * 5 + np.random.normal(0, 5)))
        evaporation = max(0, (temp - 15) * 0.3 + np.random.normal(0, 1))
        
        return {
            "timestamp": datetime.now().isoformat(),
            "region": self.region.title(),
            "temperature": round(temp, 1),
            "humidity": round(humidity, 1),
            "rainfall": round(rainfall, 1),
            "soil_moisture": round(soil_moisture, 1),
            "evaporation": round(evaporation, 1),
        }

# Global simulators
simulators: Dict[str, DataSimulator] = {}
active_connections: List[WebSocket] = []

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the main dashboard."""
    html_content = (Path(__file__).parent / "static" / "index.html").read_text()
    return HTMLResponse(content=html_content)

@app.websocket("/ws/{region}")
async def websocket_endpoint(websocket: WebSocket, region: str):
    await websocket.accept()
    active_connections.append(websocket)
    
    if region not in simulators:
        simulators[region] = DataSimulator(region)
    
    try:
        while True:
            data = simulators[region].generate_data()
            await websocket.send_text(json.dumps(data))
            await asyncio.sleep(1)  # Send data every second
    except Exception:
        active_connections.remove(websocket)

@app.get("/api/regions")
async def get_regions():
    """Get available regions."""
    return {"regions": list(REGIONS.keys())}

def run_server(host: str = "127.0.0.1", port: int = 8000):
    """Run the FastAPI server."""
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    run_server()
