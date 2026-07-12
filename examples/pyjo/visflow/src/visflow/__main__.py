#!/usr/bin/env python3
"""
VisFlow Main Entry Point

Launch the VisFlow 3D Interactive Data Visualization Studio.

Usage:
    python -m visflow [options]
    visflow [options]
"""

import argparse
import asyncio
import sys
import threading
import time
import webbrowser
from pathlib import Path

import uvicorn


def check_dependencies():
    """Check if all required dependencies are installed."""
    missing_deps = []
    
    try:
        import fastapi
    except ImportError:
        missing_deps.append("fastapi")
    
    try:
        import uvicorn
    except ImportError:
        missing_deps.append("uvicorn")
    
    try:
        import pandas
    except ImportError:
        missing_deps.append("pandas")
    
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
    
    if missing_deps:
        print(f"❌ Missing required dependencies: {', '.join(missing_deps)}")
        print("Please install them with:")
        print(f"  pip install {' '.join(missing_deps)}")
        sys.exit(1)
    
    return True


def find_free_port(start_port=8000, max_attempts=50):
    """Find a free port starting from start_port."""
    import socket
    
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    
    raise RuntimeError(f"Could not find a free port in range {start_port}-{start_port + max_attempts}")


def open_browser(url, delay=2.0):
    """Open browser after a delay to ensure server is running."""
    def delayed_open():
        time.sleep(delay)
        try:
            print(f"🌐 Opening VisFlow in your default browser...")
            webbrowser.open(url)
        except Exception as e:
            print(f"⚠️  Could not open browser automatically: {e}")
            print(f"   Please open {url} manually")
    
    thread = threading.Thread(target=delayed_open, daemon=True)
    thread.start()


def print_banner():
    """Print the VisFlow startup banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║    📊 VisFlow - 3D Interactive Data Visualization Studio    ║
    ║                                                              ║
    ║    Transform your data into stunning 3D visualizations      ║
    ║    with Python + Three.js in real-time                      ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_startup_info(host, port, dev_mode=False):
    """Print startup information and instructions."""
    url = f"http://{host}:{port}"
    
    print(f"✅ VisFlow server starting...")
    print(f"   🔗 URL: {url}")
    print(f"   🖥️  Host: {host}")
    print(f"   🔌 Port: {port}")
    print(f"   🛠️  Mode: {'Development' if dev_mode else 'Production'}")
    print()
    print("📖 Quick Start:")
    print("   1. Upload a CSV file or try the sample datasets")
    print("   2. Write Python code to process your data")
    print("   3. Use visualization functions to create 3D scenes")
    print("   4. Press Ctrl+R to execute code and update visualization")
    print()
    print("🔧 Controls:")
    print("   • Ctrl+C: Stop the server")
    print("   • Mouse: Rotate, zoom, pan the 3D scene")
    print("   • Ctrl+R: Execute Python code")
    print()


def main():
    """Main entry point for VisFlow."""
    parser = argparse.ArgumentParser(
        description="VisFlow - 3D Interactive Data Visualization Studio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  visflow                    # Start with default settings
  visflow --port 8080        # Start on port 8080
  visflow --host 0.0.0.0     # Allow external connections
  visflow --dev              # Enable development mode
  visflow --no-browser       # Don't open browser automatically
        """
    )
    
    parser.add_argument(
        "--host", 
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--port", 
        type=int, 
        default=0,
        help="Port to bind to (default: auto-detect starting from 8000)"
    )
    
    parser.add_argument(
        "--dev", 
        action="store_true",
        help="Enable development mode (auto-reload)"
    )
    
    parser.add_argument(
        "--no-browser", 
        action="store_true",
        help="Don't open browser automatically"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["critical", "error", "warning", "info", "debug"],
        default="info",
        help="Set the logging level (default: info)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"VisFlow {get_version()}"
    )
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    check_dependencies()
    print("✅ All dependencies found")
    print()
    
    # Determine port
    if args.port == 0:
        try:
            port = find_free_port()
        except RuntimeError as e:
            print(f"❌ {e}")
            sys.exit(1)
    else:
        port = args.port
    
    # Print startup info
    print_startup_info(args.host, port, args.dev)
    
    # Open browser unless disabled
    url = f"http://{args.host}:{port}"
    if not args.no_browser and args.host in ("127.0.0.1", "localhost"):
        open_browser(url)
    
    # Configure uvicorn
    config = uvicorn.Config(
        "visflow.server:app",
        host=args.host,
        port=port,
        reload=args.dev,
        log_level=args.log_level,
        access_log=args.dev,  # Only show access logs in dev mode
    )
    
    # Start server
    try:
        server = uvicorn.Server(config)
        server.run()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down VisFlow...")
        print("👋 Thanks for using VisFlow!")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)


def get_version():
    """Get VisFlow version."""
    try:
        from . import __version__
        return __version__
    except ImportError:
        return "0.1.0"


if __name__ == "__main__":
    main()