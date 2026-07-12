# VisFlow - 3D Interactive Data Visualization Studio

VisFlow is a local-first, interactive environment where Python scripts generate data that's immediately visualized in stunning 3D scenes. Think of it as "Jupyter for 3D data" - upload CSV datasets and watch them transform into interactive 3D visualizations.

## Features

- Real-time 3D climate data explorer
- Upload CSV datasets (weather, sensor data, geographic info)
- Python data processing with pandas/numpy
- Three.js 3D visualization
- WebSocket real-time communication
- Installable via pip/uv like Jupyter or Marimo

## Installation

```bash
# Using uv (recommended)
uv pip install visflow
visflow

# Using pip
pip install visflow
visflow
```

## Quick Start

1. Launch VisFlow: `visflow` or `python -m visflow`
2. Browser opens to `http://localhost:8000`
3. Drag CSV file or select example dataset
4. Modify Python code to transform data
5. Watch 3D scene update in real-time

## Examples

Try the built-in examples:
- Australian Bushfire Data Explorer
- Ocean Current Visualization
- Weather Pattern Explorer
- Sensor Network Monitor

## Tutorial

If you're a Python developer new to JavaScript and 3D graphics, check out our [JavaScript for Python Developers Tutorial](TUTORIAL.md) which explains how to build interactive visualizations like those in VisFlow.

## Use Cases

- Climate modeling and visualization
- Scientific data analysis
- IoT sensor data monitoring
- Geographic information visualization
- Real-time data exploration