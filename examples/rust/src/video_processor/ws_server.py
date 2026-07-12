from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import time
from processor import VideoProcessor

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTML page for testing
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>ASCII Video Demo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #1a1a1a;
            color: white;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .controls {
            margin-bottom: 20px;
        }
        button {
            padding: 10px 20px;
            margin: 5px;
            font-size: 16px;
            cursor: pointer;
        }
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .metric-card {
            background: #2a2a2a;
            padding: 15px;
            border-radius: 8px;
        }
        .ascii-display {
            font-family: 'Courier New', monospace;
            font-size: 8px;
            line-height: 8px;
            white-space: pre;
            background: black;
            padding: 10px;
            border-radius: 4px;
            overflow: auto;
            max-height: 600px;
        }
        .status {
            padding: 10px;
            background: #2a2a2a;
            border-radius: 4px;
            margin-bottom: 10px;
        }
        .fps-python { color: #3498db; }
        .fps-rust { color: #e74c3c; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎬 ASCII Video Processor</h1>

        <div class="status" id="status">
            Status: Disconnected
        </div>

        <div class="controls">
            <button onclick="connect()">Connect</button>
            <button onclick="switchMethod()">Switch Method</button>
            <button onclick="runBenchmark()">Run Benchmark</button>
        </div>

        <div class="metrics" id="metrics">
            <div class="metric-card">
                <h3>Python Performance</h3>
                <div class="fps-python" id="python-fps">-- FPS</div>
                <div id="python-time">-- ms</div>
            </div>
            <div class="metric-card">
                <h3>Rust Performance</h3>
                <div class="fps-rust" id="rust-fps">-- FPS</div>
                <div id="rust-time">-- ms</div>
            </div>
        </div>

        <div class="ascii-display" id="ascii">
            Waiting for connection...
        </div>
    </div>

    <script>
        let ws = null;
        let currentMethod = 'python';

        function connect() {
            if (ws) ws.close();

            ws = new WebSocket('ws://localhost:8000/ws');

            ws.onopen = () => {
                document.getElementById('status').textContent = 'Status: Connected ✅';
                console.log('Connected to WebSocket');
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);

                if (data.type === 'frame') {
                    document.getElementById('ascii').textContent = data.ascii;

                    if (data.method === 'python') {
                        document.getElementById('python-fps').textContent = data.fps.toFixed(1) + ' FPS';
                        document.getElementById('python-time').textContent = data.time.toFixed(1) + ' ms';
                    } else {
                        document.getElementById('rust-fps').textContent = data.fps.toFixed(1) + ' FPS';
                        document.getElementById('rust-time').textContent = data.time.toFixed(1) + ' ms';
                    }
                }

                if (data.type === 'benchmark') {
                    alert(`Benchmark Complete!
Python: ${data.python_fps.toFixed(1)} FPS
Rust: ${data.rust_fps.toFixed(1)} FPS
Speedup: ${data.speedup.toFixed(1)}x`);
                }
            };

            ws.onerror = (error) => {
                document.getElementById('status').textContent = 'Status: Error ❌';
                console.error('WebSocket error:', error);
            };

            ws.onclose = () => {
                document.getElementById('status').textContent = 'Status: Disconnected';
            };
        }

        function switchMethod() {
            if (ws && ws.readyState === WebSocket.OPEN) {
                currentMethod = currentMethod === 'python' ? 'rust' : 'python';
                ws.send(JSON.stringify({ command: 'switch', method: currentMethod }));
            }
        }

        function runBenchmark() {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ command: 'benchmark' }));
            }
        }

        // Auto-connect on load
        window.onload = () => connect();
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(HTML_PAGE)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    processor = VideoProcessor(scale=10)
    use_rust = False
    frame_num = 0

    try:
        while True:
            # Handle incoming messages
            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=0.01)
                if data.get('command') == 'switch':
                    use_rust = data.get('method') == 'rust'
                elif data.get('command') == 'benchmark':
                    # Run quick benchmark
                    await run_benchmark(websocket, processor)
            except asyncio.TimeoutError:
                pass

            # Get frame
            if processor.use_test_pattern:
                frame = processor.generate_test_frame(frame_num)
                frame_num += 1
            else:
                ret, frame = processor.cap.read()
                if not ret:
                    frame = processor.generate_test_frame(frame_num)
                    frame_num += 1

            # Process frame
            start = time.perf_counter()

            if use_rust and RUST_AVAILABLE:
                ascii_art = processor.process_frame_rust(frame)
                method = 'rust'
            else:
                ascii_art = processor.process_frame_python(frame)
                method = 'python'

            elapsed = (time.perf_counter() - start) * 1000
            fps = 1000 / elapsed if elapsed > 0 else 0

            # Send frame data
            await websocket.send_json({
                'type': 'frame',
                'ascii': ascii_art,
                'method': method,
                'time': elapsed,
                'fps': fps
            })

            # Control frame rate
            await asyncio.sleep(0.033)  # ~30 FPS

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")

async def run_benchmark(websocket: WebSocket, processor: VideoProcessor):
    """Run a quick benchmark"""
    import numpy as np

    # Generate test frame
    frame = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)

    # Test Python
    python_times = []
    for _ in range(10):
        start = time.perf_counter()
        _ = processor.process_frame_python(frame)
        python_times.append((time.perf_counter() - start) * 1000)

    python_avg = np.mean(python_times)

    # Test Rust
    rust_avg = python_avg  # Default if not available
    if RUST_AVAILABLE:
        rust_times = []
        for _ in range(10):
            start = time.perf_counter()
            _ = processor.process_frame_rust(frame)
            rust_times.append((time.perf_counter() - start) * 1000)
        rust_avg = np.mean(rust_times)

    await websocket.send_json({
        'type': 'benchmark',
        'python_fps': 1000 / python_avg,
        'rust_fps': 1000 / rust_avg,
        'speedup': python_avg / rust_avg
    })

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting web demo at http://localhost:8000")
    print("📺 Open browser to see ASCII video")
    uvicorn.run(app, host="0.0.0.0", port=8000)
