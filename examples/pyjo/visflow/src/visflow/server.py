"""
VisFlow FastAPI Server

Main server handling data processing, file uploads, and real-time WebSocket communication
between Python data processing and Three.js visualization.
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .data_processor import DataProcessor


class CodeExecutionRequest(BaseModel):
    code: str
    data_context: Optional[Dict[str, Any]] = None


class VisualizationData(BaseModel):
    type: str
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


class ConnectionManager:
    """Manage WebSocket connections for real-time data streaming."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception:
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)


app = FastAPI(
    title="VisFlow",
    description="3D Interactive Data Visualization Studio",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
manager = ConnectionManager()
processor = DataProcessor()

# Get the directory where this file is located
current_dir = Path(__file__).parent
static_dir = current_dir / "static"

# Mount static files
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main application HTML."""
    index_path = static_dir / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Frontend not found")
    
    return HTMLResponse(content=index_path.read_text(), status_code=200)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "VisFlow server is running"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process a data file (CSV, JSON, etc.)."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    try:
        # Read file content
        content = await file.read()
        
        # Process based on file type
        if file.filename.endswith('.csv'):
            df = pd.read_csv(pd.io.common.BytesIO(content))
        elif file.filename.endswith('.json'):
            df = pd.read_json(pd.io.common.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Store in processor
        dataset_id = processor.store_dataset(df, file.filename)
        
        # Get basic info about the dataset
        info = processor.get_dataset_info(dataset_id)
        
        # Broadcast to connected clients
        await manager.broadcast(json.dumps({
            "type": "dataset_uploaded",
            "data": {
                "dataset_id": dataset_id,
                "filename": file.filename,
                "info": info
            }
        }))
        
        return {
            "dataset_id": dataset_id,
            "filename": file.filename,
            "info": info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.post("/execute")
async def execute_code(request: CodeExecutionRequest):
    """Execute Python code for data processing and visualization."""
    try:
        # Execute code with processor
        result = await processor.execute_code(
            request.code,
            request.data_context or {}
        )
        
        # Broadcast result to connected clients
        await manager.broadcast(json.dumps({
            "type": "code_execution_result",
            "data": result
        }))
        
        return result
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "output": None,
            "visualization_data": None
        }
        
        # Broadcast error to connected clients
        await manager.broadcast(json.dumps({
            "type": "code_execution_error",
            "data": error_result
        }))
        
        return error_result


@app.get("/datasets")
async def list_datasets():
    """List all available datasets."""
    return processor.list_datasets()


@app.get("/datasets/{dataset_id}")
async def get_dataset(dataset_id: str, limit: int = 1000):
    """Get dataset by ID with optional row limit."""
    try:
        data = processor.get_dataset(dataset_id, limit)
        return data
    except KeyError:
        raise HTTPException(status_code=404, detail="Dataset not found")


@app.delete("/datasets/{dataset_id}")
async def delete_dataset(dataset_id: str):
    """Delete a dataset."""
    try:
        processor.delete_dataset(dataset_id)
        
        # Broadcast deletion to connected clients
        await manager.broadcast(json.dumps({
            "type": "dataset_deleted",
            "data": {"dataset_id": dataset_id}
        }))
        
        return {"message": "Dataset deleted successfully"}
    except KeyError:
        raise HTTPException(status_code=404, detail="Dataset not found")


@app.get("/examples")
async def list_examples():
    """List available example datasets."""
    examples_dir = static_dir / "sample_data"
    examples = []
    
    if examples_dir.exists():
        for file in examples_dir.glob("*.csv"):
            examples.append({
                "name": file.stem,
                "filename": file.name,
                "path": f"/static/sample_data/{file.name}"
            })
    
    return examples


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication."""
    await manager.connect(websocket)
    
    try:
        while True:
            # Listen for messages from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message["type"] == "ping":
                await manager.send_personal_message(
                    json.dumps({"type": "pong"}),
                    websocket
                )
            elif message["type"] == "execute_code":
                # Execute code and stream results
                try:
                    result = await processor.execute_code(
                        message["data"]["code"],
                        message["data"].get("context", {})
                    )
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "code_execution_result",
                            "data": result
                        }),
                        websocket
                    )
                except Exception as e:
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "code_execution_error",
                            "data": {"error": str(e)}
                        }),
                        websocket
                    )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "visflow.server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )