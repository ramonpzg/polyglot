import asyncio
import base64
import io
import os
import json
from typing import Optional

import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from PIL import Image

from ._hillshade import hillshade, HillshadeSession
from .utils import synthetic_uluru, normalize_cellsize

def create_app(dem_path: Optional[str] = None) -> FastAPI:
    app = FastAPI(title="coolproject")

    # Load DEM (float32 HxW). Fallback to synthetic if not provided or fails.
    if dem_path:
        try:
            dem = np.load(dem_path).astype(np.float32)
        except Exception as e:
            print(f"Failed to load DEM at {dem_path}: {e}. Falling back to synthetic.")
            dem = synthetic_uluru()
    else:
        dem = synthetic_uluru()

    cellsize = normalize_cellsize(*dem.shape)
    session = HillshadeSession()

    app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

    @app.get("/")
    async def index():
        with open(os.path.join(os.path.dirname(__file__), "static", "index.html"), "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())

    @app.get("/api/hillshade")
    async def api_hillshade(azimuth: float = 315.0, altitude: float = 35.0):
        img = session.render(dem, cellsize, float(azimuth), float(altitude))
        pil = Image.fromarray(img, mode="RGBA")
        buf = io.BytesIO()
        pil.save(buf, format="PNG")
        return Response(content=buf.getvalue(), media_type="image/png")

    @app.websocket("/ws")
    async def ws(ws: WebSocket):
        await ws.accept()
        try:
            # Initial frame
            await send_frame(ws, session, dem, cellsize, 315.0, 35.0)
            async for msg in ws.iter_text():
                try:
                    data = json.loads(msg)
                    az = float(data.get("azimuth", 315.0))
                    alt = float(data.get("altitude", 35.0))
                    await send_frame(ws, session, dem, cellsize, az, alt)
                except Exception as e:
                    await ws.send_text(json.dumps({"error": str(e)}))
        except WebSocketDisconnect:
            pass

    return app

async def send_frame(ws: WebSocket, session: HillshadeSession, dem: np.ndarray, cell: float, az: float, alt: float):
    # Offload to thread to avoid blocking event loop (GPU call runs w/o GIL but we encode PNG)
    loop = asyncio.get_running_loop()
    img = await loop.run_in_executor(None, lambda: session.render(dem, cell, az, alt))
    pil = Image.fromarray(img, mode="RGBA")
    buf = io.BytesIO()
    pil.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    await ws.send_text(json.dumps({"png": b64, "azimuth": az, "altitude": alt}))
