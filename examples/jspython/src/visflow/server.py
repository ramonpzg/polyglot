"""FastAPI backend for VisFlow."""

import json
import pandas as pd
import numpy as np
from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import asyncio
import traceback
import os

app = FastAPI(title="VisFlow", description="3D Interactive Data Visualization Studio")

# In-memory storage for data
current_data = None

# Serve static files
# Get the directory where this file is located
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")

# Check if static directory exists
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    # Get the directory where this file is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(current_dir, "static", "index.html")
    
    if os.path.exists(index_path):
        with open(index_path) as f:
            return HTMLResponse(content=f.read(), status_code=200)
    else:
        return HTMLResponse(content="<h1>VisFlow</h1><p>Static files not found. Please check your installation.</p>", status_code=200)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Keep the connection alive
            await asyncio.sleep(1)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

@app.post("/upload")
async def upload_data(file: UploadFile = File(...)):
    global current_data
    try:
        # Read the CSV file
        content = await file.read()
        # Convert bytes to string and then to DataFrame
        from io import StringIO
        string_content = StringIO(content.decode())
        df = pd.read_csv(string_content)
        current_data = df.to_dict(orient='records')
        return {"status": "success", "rows": len(df), "columns": list(df.columns)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/execute")
async def execute_python_code(code: str):
    global current_data
    try:
        # Create a safe execution environment
        local_env = {
            'pd': pd,
            'np': np,
            'data': pd.DataFrame(current_data) if current_data else None
        }
        
        # Execute the code
        exec(code, {"__builtins__": {}}, local_env)
        
        # Extract results
        result = local_env.get('result', None)
        if result is not None:
            if isinstance(result, pd.DataFrame):
                return {"status": "success", "data": result.to_dict(orient='records')}
            else:
                return {"status": "success", "data": str(result)}
        else:
            return {"status": "success", "message": "Code executed successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}

@app.get("/data")
async def get_current_data():
    return {"data": current_data}