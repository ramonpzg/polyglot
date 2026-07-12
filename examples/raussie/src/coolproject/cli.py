import argparse
import webbrowser
import uvicorn

from .server import create_app

def main():
    parser = argparse.ArgumentParser(description="Rust+Python GPU hillshade demo")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--dem", type=str, default=None, help="Path to .npy float32 DEM (HxW)")
    args = parser.parse_args()

    app = create_app(dem_path=args.dem)
    url = f"http://{args.host}:{args.port}/"
    print(f"Starting server at {url}")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")
