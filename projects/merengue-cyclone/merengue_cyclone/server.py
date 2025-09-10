"""
FastAPI server for Merengue Cyclone hurricane tracking.
"""

import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .hurricane import (
    HurricaneTracker,
    HurricanePoint,
    calculate_distance,
    estimate_surge,
)

# Initialize FastAPI app
app = FastAPI(
    title="Merengue Cyclone API",
    description="High-performance hurricane tracking and analysis API",
    version="0.1.0",
)

# Add CORS middleware for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global tracker instance
tracker = HurricaneTracker()

# Active WebSocket connections
active_connections: List[WebSocket] = []


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main dashboard."""
    html_path = Path(__file__).parent / "static" / "index.html"
    if html_path.exists():
        return html_path.read_text()
    else:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Merengue Cyclone</title>
            <style>
                body {
                    font-family: system-ui;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 2rem;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }
                h1 { text-align: center; }
                .status {
                    background: rgba(255,255,255,0.1);
                    padding: 1rem;
                    border-radius: 8px;
                    margin: 1rem 0;
                }
            </style>
        </head>
        <body>
            <h1>🌀 Merengue Cyclone</h1>
            <div class="status">
                <h2>Hurricane Tracking Server Active</h2>
                <p>API: <a href="/docs" style="color: cyan">Interactive Docs</a></p>
                <p>WebSocket: ws://localhost:8000/ws</p>
            </div>
        </body>
        </html>
        """


@app.get("/api/status")
async def get_status():
    """Get server status and active tracks."""
    return {
        "status": "active",
        "active_tracks": list(tracker.tracks.keys()),
        "connections": len(active_connections),
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/api/track/{name}/observation")
async def add_observation(
    name: str,
    lat: float,
    lon: float,
    pressure: float,
    wind_speed: float,
):
    """Add a new observation to a hurricane track."""
    point = HurricanePoint(
        lat=lat,
        lon=lon,
        pressure=pressure,
        wind_speed=wind_speed,
        timestamp=datetime.now(),
    )

    tracker.add_observation(name, point)

    # Notify WebSocket clients
    await broadcast_update({
        "type": "observation",
        "track": name,
        "point": {
            "lat": lat,
            "lon": lon,
            "pressure": pressure,
            "wind_speed": wind_speed,
            "category": point.category,
        }
    })

    return {"success": True, "category": point.category}


@app.get("/api/track/{name}/analysis")
async def analyze_track(name: str):
    """Get analysis for a hurricane track."""
    if name not in tracker.tracks:
        raise HTTPException(status_code=404, detail=f"Track '{name}' not found")

    analysis = tracker.analyze_track(name)

    return {
        "total_distance_km": analysis.total_distance,
        "average_speed_kmh": analysis.average_speed,
        "ace": analysis.ace,
        "max_intensity": {
            "wind_speed_kmh": analysis.max_intensity.wind_speed,
            "category": analysis.max_intensity.category,
            "lat": analysis.max_intensity.lat,
            "lon": analysis.max_intensity.lon,
        },
        "point_count": len(analysis.points),
    }


@app.get("/api/track/{name}/predict")
async def predict_track(name: str, hours: int = 24):
    """Predict future track positions."""
    if name not in tracker.tracks:
        raise HTTPException(status_code=404, detail=f"Track '{name}' not found")

    predictions = tracker.predict_next_position(name, hours)

    return {
        "track": name,
        "predictions": [
            {
                "lat": p.lat,
                "lon": p.lon,
                "wind_speed": p.wind_speed,
                "pressure": p.pressure,
                "timestamp": p.timestamp.isoformat(),
                "hours_ahead": i * 6,
            }
            for i, p in enumerate(predictions[::6], 1)
        ]
    }


@app.get("/api/track/{name}/impact/dr")
async def get_dr_impact(name: str):
    """Get Dominican Republic impact assessment."""
    if name not in tracker.tracks:
        raise HTTPException(status_code=404, detail=f"Track '{name}' not found")

    return tracker.estimate_dominican_impact(name)


@app.post("/api/simulate/{scenario}")
async def simulate_hurricane(scenario: str):
    """Simulate a historical hurricane scenario."""
    scenarios = {
        "maria": [
            {"lat": 15.0, "lon": -59.0, "pressure": 958, "wind_speed": 241},
            {"lat": 15.3, "lon": -60.1, "pressure": 950, "wind_speed": 257},
            {"lat": 15.7, "lon": -61.2, "pressure": 930, "wind_speed": 280},
            {"lat": 16.2, "lon": -62.4, "pressure": 925, "wind_speed": 295},
            {"lat": 16.8, "lon": -63.7, "pressure": 920, "wind_speed": 280},
            {"lat": 17.5, "lon": -65.0, "pressure": 925, "wind_speed": 270},
            {"lat": 18.0, "lon": -66.5, "pressure": 935, "wind_speed": 250},
        ],
        "georges": [
            {"lat": 16.0, "lon": -64.0, "pressure": 970, "wind_speed": 185},
            {"lat": 16.5, "lon": -65.5, "pressure": 965, "wind_speed": 195},
            {"lat": 17.2, "lon": -67.0, "pressure": 960, "wind_speed": 205},
            {"lat": 17.9, "lon": -68.5, "pressure": 955, "wind_speed": 215},
            {"lat": 18.5, "lon": -70.0, "pressure": 960, "wind_speed": 195},
        ],
        "david": [
            {"lat": 14.0, "lon": -56.0, "pressure": 950, "wind_speed": 240},
            {"lat": 14.8, "lon": -58.0, "pressure": 940, "wind_speed": 260},
            {"lat": 15.6, "lon": -60.0, "pressure": 930, "wind_speed": 280},
            {"lat": 16.5, "lon": -62.0, "pressure": 925, "wind_speed": 290},
            {"lat": 17.4, "lon": -64.0, "pressure": 930, "wind_speed": 280},
            {"lat": 18.3, "lon": -66.0, "pressure": 940, "wind_speed": 260},
        ],
    }

    if scenario not in scenarios:
        raise HTTPException(status_code=400, detail=f"Unknown scenario: {scenario}")

    # Clear existing track
    if scenario in tracker.tracks:
        tracker.tracks[scenario] = []

    # Add points with timestamps
    base_time = datetime.now()
    for i, point_data in enumerate(scenarios[scenario]):
        point = HurricanePoint(
            lat=point_data["lat"],
            lon=point_data["lon"],
            pressure=point_data["pressure"],
            wind_speed=point_data["wind_speed"],
            timestamp=base_time + timedelta(hours=i * 6),
        )
        tracker.add_observation(scenario, point)

        # Broadcast each point
        await broadcast_update({
            "type": "simulation",
            "scenario": scenario,
            "point": {
                "lat": point.lat,
                "lon": point.lon,
                "pressure": point.pressure,
                "wind_speed": point.wind_speed,
                "category": point.category,
                "timestamp": point.timestamp.isoformat(),
            },
            "progress": (i + 1) / len(scenarios[scenario]),
        })

        # Small delay for visual effect
        await asyncio.sleep(0.2)

    # Return analysis
    analysis = tracker.analyze_track(scenario)
    impact = tracker.estimate_dominican_impact(scenario)

    return {
        "scenario": scenario,
        "points": len(scenarios[scenario]),
        "analysis": {
            "total_distance_km": analysis.total_distance,
            "average_speed_kmh": analysis.average_speed,
            "ace": analysis.ace,
            "max_wind_speed": analysis.max_intensity.wind_speed,
            "max_category": analysis.max_intensity.category,
        },
        "dr_impact": impact,
    }


@app.get("/api/surge/calculate")
async def calculate_surge(
    wind_speed: float,
    pressure: float,
    depth: float = 20,
    angle: float = 45,
):
    """Calculate storm surge estimate."""
    surge_height = estimate_surge(wind_speed, pressure, depth, angle)

    # Risk assessment
    if surge_height < 1.0:
        risk = "low"
    elif surge_height < 2.0:
        risk = "moderate"
    elif surge_height < 3.0:
        risk = "high"
    else:
        risk = "extreme"

    return {
        "surge_meters": surge_height,
        "risk_level": risk,
        "parameters": {
            "wind_speed_kmh": wind_speed,
            "pressure_mb": pressure,
            "water_depth_m": depth,
            "approach_angle_deg": angle,
        }
    }


@app.get("/api/benchmark")
async def run_benchmark():
    """Run performance benchmark."""
    results = tracker.benchmark_performance(10000)

    return {
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "platform": "Zig-accelerated" if "zig_ms" in results else "Pure Python",
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await websocket.accept()
    active_connections.append(websocket)

    try:
        # Send initial status
        await websocket.send_json({
            "type": "connected",
            "tracks": list(tracker.tracks.keys()),
            "timestamp": datetime.now().isoformat(),
        })

        # Keep connection alive
        while True:
            # Receive and echo messages
            data = await websocket.receive_text()

            # Handle ping/pong
            if data == "ping":
                await websocket.send_text("pong")
            else:
                # Echo back any other message
                await websocket.send_text(f"Echo: {data}")

    except Exception:
        pass
    finally:
        active_connections.remove(websocket)


async def broadcast_update(data: Dict[str, Any]):
    """Broadcast update to all connected WebSocket clients."""
    disconnected = []

    for connection in active_connections:
        try:
            await connection.send_json(data)
        except:
            disconnected.append(connection)

    # Clean up disconnected clients
    for conn in disconnected:
        if conn in active_connections:
            active_connections.remove(conn)


def start_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """Start the FastAPI server."""
    uvicorn.run(
        "merengue_cyclone.server:app",
        host=host,
        port=port,
        reload=reload,
    )


if __name__ == "__main__":
    start_server()
