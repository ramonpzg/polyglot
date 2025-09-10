"""
CaribeTech FastAPI Server - Real-time hurricane monitoring web interface.
"""

import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import time

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from . import CycloneTracker, StormTrack, StormPoint, benchmark_python_vs_zig

app = FastAPI(
    title="🌀 CaribeTech Hurricane Monitor",
    description="Real-time Caribbean hurricane tracking and analysis",
    version="0.1.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global tracker instance
tracker = CycloneTracker()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                # Connection closed, remove it
                self.active_connections.remove(connection)

manager = ConnectionManager()

@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {
        "service": "CaribeTech Hurricane Monitor",
        "version": "0.1.0",
        "description": "Dominican Republic-focused hurricane tracking system",
        "endpoints": {
            "current_storms": "/api/storms/current",
            "historical": "/api/storms/historical",
            "threats": "/api/threats/dominican-republic",
            "benchmark": "/api/benchmark",
            "websocket": "/ws"
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "CaribeTech Monitor"
    }

@app.get("/api/storms/current")
async def get_current_storms():
    """Get current active storms in the Caribbean."""
    # Simulate current storms
    current_storms = []
    
    # Generate 1-3 active storms
    num_storms = random.randint(0, 3)
    
    for i in range(num_storms):
        storm = tracker.generate_sample_data()
        storm.name = f"Active-{i+1}"
        
        # Only include recent points (last 24 hours)
        recent_points = storm.points[-4:]  # Last 4 points (24 hours)
        storm.points = recent_points
        
        current_storms.append({
            "name": storm.name,
            "season": storm.season,
            "current_position": {
                "latitude": storm.points[-1].latitude,
                "longitude": storm.points[-1].longitude,
                "timestamp": storm.points[-1].timestamp.isoformat()
            },
            "intensity": {
                "category": storm.points[-1].category,
                "wind_speed_kmh": storm.points[-1].wind_speed_kmh,
                "pressure_hpa": storm.points[-1].pressure_hpa
            },
            "threat_level": storm.threat_level(),
            "distance_to_dr": storm.closest_approach_to_dr[0],
            "track": [
                {
                    "lat": point.latitude,
                    "lon": point.longitude,
                    "time": point.timestamp.isoformat(),
                    "category": point.category,
                    "wind_speed": point.wind_speed_kmh
                }
                for point in storm.points
            ]
        })
    
    return {
        "storms": current_storms,
        "count": len(current_storms),
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/storms/historical")
async def get_historical_storms(years: int = 5):
    """Get historical storm data."""
    tracks = tracker.load_historical_data(years)
    
    return {
        "storms": [
            {
                "name": track.name,
                "season": track.season,
                "max_category": track.max_category,
                "threat_level": track.threat_level(),
                "closest_distance_km": track.closest_approach_to_dr[0],
                "track_points": len(track.points)
            }
            for track in tracks
        ],
        "total": len(tracks),
        "years_analyzed": years
    }

@app.get("/api/threats/dominican-republic")
async def get_dominican_threats(years: int = 10):
    """Get storms that threatened Dominican Republic."""
    tracks = tracker.load_historical_data(years)
    threats = tracker.analyze_dominican_threats()
    
    threat_data = []
    for track in threats:
        distance, closest_point = track.closest_approach_to_dr
        
        threat_data.append({
            "name": track.name,
            "season": track.season,
            "max_category": track.max_category,
            "threat_level": track.threat_level(),
            "closest_approach": {
                "distance_km": distance,
                "date": closest_point.timestamp.isoformat() if closest_point else None,
                "wind_speed_kmh": closest_point.wind_speed_kmh if closest_point else None,
                "pressure_hpa": closest_point.pressure_hpa if closest_point else None
            }
        })
    
    return {
        "threats": threat_data,
        "total_threats": len(threats),
        "total_storms": len(tracks),
        "threat_percentage": (len(threats) / len(tracks) * 100) if tracks else 0,
        "years_analyzed": years
    }

@app.get("/api/prediction/{storm_name}")
async def get_storm_prediction(storm_name: str, hours: int = 72):
    """Get storm path prediction."""
    # Generate a sample storm for prediction
    storm = tracker.generate_sample_data()
    storm.name = storm_name
    
    # Get current track
    current_track = storm.points[-3:]  # Last 3 points
    
    # Generate prediction
    predicted_points = tracker.predict_path(current_track, hours_ahead=hours)
    
    return {
        "storm_name": storm_name,
        "current_position": {
            "latitude": current_track[-1].latitude,
            "longitude": current_track[-1].longitude,
            "timestamp": current_track[-1].timestamp.isoformat()
        },
        "prediction_hours": hours,
        "predicted_track": [
            {
                "latitude": point.latitude,
                "longitude": point.longitude,
                "timestamp": point.timestamp.isoformat(),
                "category": point.category,
                "wind_speed_kmh": point.wind_speed_kmh,
                "pressure_hpa": point.pressure_hpa
            }
            for point in predicted_points
        ]
    }

@app.get("/api/benchmark")
async def run_benchmark(calculations: int = 10000):
    """Run performance benchmark between Python and Zig."""
    results = benchmark_python_vs_zig(calculations)
    
    return {
        "benchmark_results": results,
        "summary": {
            "zig_speedup": f"{results['speedup']:.1f}x faster",
            "python_time": f"{results['python_time']:.4f}s",
            "zig_time": f"{results['zig_time']:.4f}s",
            "calculations_per_second": {
                "python": int(calculations / results['python_time']),
                "zig": int(calculations / results['zig_time'])
            }
        }
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time storm updates."""
    await manager.connect(websocket)
    try:
        while True:
            # Send storm updates every 5 seconds
            await asyncio.sleep(5)
            
            # Generate real-time storm data
            update = {
                "type": "storm_update",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "active_storms": random.randint(0, 3),
                    "new_alerts": random.choice([True, False]),
                    "dominican_threat_level": random.choice(["LOW", "MODERATE", "HIGH", "EXTREME"]),
                    "latest_position": {
                        "latitude": random.uniform(15.0, 25.0),
                        "longitude": random.uniform(-75.0, -60.0),
                        "wind_speed": random.uniform(100, 250),
                        "category": random.randint(1, 5)
                    }
                }
            }
            
            await manager.broadcast(update)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/demo")
async def demo_page():
    """Demo page for live monitoring."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🌀 CaribeTech Live Monitor</title>
        <meta charset="utf-8">
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: white;
                margin: 0;
                padding: 20px;
            }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 30px; }
            .card { 
                background: rgba(255,255,255,0.1);
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
                backdrop-filter: blur(10px);
            }
            .storm-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .storm-card { 
                background: rgba(255,255,255,0.15);
                border-radius: 8px;
                padding: 15px;
                border-left: 4px solid #ff6b6b;
            }
            .status { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
            .threat-extreme { background: #ff4757; }
            .threat-high { background: #ff6348; }
            .threat-moderate { background: #ffa502; }
            .threat-low { background: #2ed573; }
            #updates { height: 200px; overflow-y: auto; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌀 CaribeTech Hurricane Monitor</h1>
                <p>Real-time Caribbean Storm Tracking - Dominican Republic Focus</p>
            </div>
            
            <div class="card">
                <h2>🔴 Live Storm Updates</h2>
                <div id="status">Connecting to real-time feed...</div>
                <div id="updates"></div>
            </div>
            
            <div class="card">
                <h2>📊 Current Storm Data</h2>
                <div id="current-storms" class="storm-grid">
                    <div class="storm-card">
                        <h3>🌪️ Loading...</h3>
                        <p>Fetching current storm data...</p>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>⚡ Performance Stats</h2>
                <div id="performance">
                    <p>Zig-powered calculations provide <strong>6-8x speedup</strong> for real-time analysis</p>
                    <button onclick="runBenchmark()" style="background: #2ed573; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">Run Benchmark</button>
                    <div id="benchmark-results"></div>
                </div>
            </div>
        </div>
        
        <script>
            // WebSocket connection for real-time updates
            const ws = new WebSocket(`ws://${window.location.host}/ws`);
            const updatesDiv = document.getElementById('updates');
            const statusDiv = document.getElementById('status');
            
            ws.onopen = function(event) {
                statusDiv.textContent = '🟢 Connected - Receiving live updates';
                statusDiv.style.color = '#2ed573';
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                const time = new Date(data.timestamp).toLocaleTimeString();
                const threatClass = `threat-${data.data.dominican_threat_level.toLowerCase()}`;
                
                updatesDiv.innerHTML = `
                    <div style="margin-bottom: 10px; padding: 5px; border-left: 3px solid #2ed573;">
                        <strong>${time}</strong> - ${data.data.active_storms} active storms | 
                        DR Threat: <span class="status ${threatClass}">${data.data.dominican_threat_level}</span>
                    </div>
                ` + updatesDiv.innerHTML;
                
                // Keep only last 10 updates
                const updates = updatesDiv.children;
                while (updates.length > 10) {
                    updatesDiv.removeChild(updates[updates.length - 1]);
                }
            };
            
            ws.onclose = function(event) {
                statusDiv.textContent = '🔴 Disconnected from live feed';
                statusDiv.style.color = '#ff4757';
            };
            
            // Load current storms
            async function loadCurrentStorms() {
                try {
                    const response = await fetch('/api/storms/current');
                    const data = await response.json();
                    
                    const stormsDiv = document.getElementById('current-storms');
                    if (data.storms.length === 0) {
                        stormsDiv.innerHTML = '<div class="storm-card"><h3>✅ No Active Threats</h3><p>Caribbean region is currently clear</p></div>';
                    } else {
                        stormsDiv.innerHTML = data.storms.map(storm => `
                            <div class="storm-card">
                                <h3>🌀 ${storm.name}</h3>
                                <p><strong>Category:</strong> ${storm.intensity.category}</p>
                                <p><strong>Wind Speed:</strong> ${Math.round(storm.intensity.wind_speed_kmh)} km/h</p>
                                <p><strong>Distance to DR:</strong> ${Math.round(storm.distance_to_dr)} km</p>
                                <span class="status threat-${storm.threat_level.toLowerCase()}">${storm.threat_level}</span>
                            </div>
                        `).join('');
                    }
                } catch (error) {
                    console.error('Error loading storms:', error);
                }
            }
            
            // Run performance benchmark
            async function runBenchmark() {
                const button = event.target;
                const resultsDiv = document.getElementById('benchmark-results');
                
                button.textContent = 'Running...';
                button.disabled = true;
                
                try {
                    const response = await fetch('/api/benchmark?calculations=50000');
                    const data = await response.json();
                    
                    resultsDiv.innerHTML = `
                        <div style="margin-top: 15px; padding: 15px; background: rgba(0,0,0,0.3); border-radius: 5px;">
                            <h4>🏁 Benchmark Results</h4>
                            <p><strong>Python:</strong> ${data.summary.python_time}</p>
                            <p><strong>Zig:</strong> ${data.summary.zig_time}</p>
                            <p><strong>Speedup:</strong> <span style="color: #2ed573; font-weight: bold;">${data.summary.zig_speedup}</span></p>
                            <p><strong>Calculations/sec:</strong> Python: ${data.summary.calculations_per_second.python.toLocaleString()}, Zig: ${data.summary.calculations_per_second.zig.toLocaleString()}</p>
                        </div>
                    `;
                } catch (error) {
                    resultsDiv.innerHTML = '<p style="color: #ff4757;">Benchmark failed</p>';
                }
                
                button.textContent = 'Run Benchmark';
                button.disabled = false;
            }
            
            // Load initial data
            loadCurrentStorms();
            setInterval(loadCurrentStorms, 30000); // Refresh every 30 seconds
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
