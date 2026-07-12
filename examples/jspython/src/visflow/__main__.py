"""Main entry point for VisFlow."""

import uvicorn
import argparse
from .server import app

def main():
    parser = argparse.ArgumentParser(description="VisFlow - 3D Interactive Data Visualization Studio")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8070, help="Port to bind to")
    args = parser.parse_args()

    print(f"VisFlow starting on http://{args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")

if __name__ == "__main__":
    main()
