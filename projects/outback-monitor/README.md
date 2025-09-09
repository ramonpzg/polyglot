# Outback Monitor

Real-time agricultural monitoring dashboard for Australian conditions.

## Installation

```bash
pip install outback-monitor
```

## Usage

Start the monitoring dashboard:

```bash
outback-monitor
```

Or specify a region directly:

```bash
outback-monitor --region queensland
```

## Features

- Real-time simulation of Australian agricultural conditions
- WebSocket-based live data streaming
- Minimalist dashboard with Chart.js visualizations
- CLI interface with region selection
- FastAPI backend with Python data simulation
- Vanilla JavaScript frontend

## Architecture

This is a polyglot application demonstrating Python + JavaScript integration:

- **Python**: FastAPI server, data simulation with NumPy, CLI interface
- **JavaScript**: Real-time dashboard, Chart.js visualizations, WebSocket client

Perfect example of using Python for backend logic and JavaScript for interactive UIs.
