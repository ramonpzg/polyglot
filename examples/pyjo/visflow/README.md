# 📊 VisFlow - 3D Interactive Data Visualization Studio

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Three.js](https://img.shields.io/badge/Three.js-0.158+-red.svg)](https://threejs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Transform your data into stunning 3D visualizations with the power of Python + Three.js**

VisFlow is a desktop-style web application that combines Python's data processing capabilities with Three.js 3D visualization, creating an interactive environment perfect for exploring spatial-temporal datasets. Think "Jupyter for 3D data" - a local-first tool that lets you upload CSV datasets and immediately see them come alive in beautiful 3D scenes.

![VisFlow Screenshot](docs/images/visflow-demo.png)

## 🌟 Key Features

- **🐍 Python + 🌐 Three.js Integration**: Best of both worlds - powerful data processing with stunning 3D visuals
- **📁 Local-First**: Runs entirely on your machine, no cloud dependencies
- **⚡ Real-Time Updates**: Live code execution with instant 3D feedback
- **🔥 Fire & Climate Focus**: Perfect for bushfire data, weather patterns, and environmental analysis
- **💻 VS Code-Like Experience**: Monaco editor with syntax highlighting and shortcuts
- **🎮 Interactive 3D**: Mouse controls, camera manipulation, and smooth 60fps rendering
- **📊 Multiple Data Formats**: CSV, JSON support with automatic type detection
- **🚀 Easy Installation**: One command to get started

## 🚀 Quick Start (2 Minutes!)

### Installation

```bash
# Using pip
pip install visflow

# Using uv (recommended)
uv pip install visflow
```

### Launch & First Visualization

```bash
# Start VisFlow
visflow

# Opens automatically at http://localhost:8000
```

**That's it!** VisFlow will:
1. Auto-detect a free port
2. Open your browser automatically  
3. Show you the welcome screen with sample datasets

### Your First 3D Scene

1. **Load Sample Data**: Click "🔥 Bushfire Example" 
2. **See the Magic**: Watch as 1000+ data points become a 3D fire risk visualization
3. **Interact**: 
   - Mouse wheel = zoom
   - Left drag = rotate
   - Right drag = pan
4. **Experiment**: Modify the code and press `Ctrl+R` to see changes instantly

## 📖 Detailed Usage Guide

### Data Upload Options

#### Option 1: Drag & Drop CSV Files
- Simply drag any CSV file into the browser window
- Automatic column detection and type inference
- Immediate data preview in the bottom panel

#### Option 2: Use Sample Datasets
- **Bushfire Data**: Australian fire risk with weather conditions
- **Ocean Currents**: 3D oceanographic flow patterns  
- **Wind Patterns**: Atmospheric data with multiple altitudes

#### Option 3: Connect Your Own Data
```python
# Your data should have coordinate columns
data = pd.read_csv('your_data.csv')
# Columns like: latitude, longitude, value, time, etc.
```

### Creating Visualizations

#### Basic Particle System
```python
import pandas as pd
import numpy as np

# Load your data (or use uploaded dataset)
data = your_uploaded_dataset

# Create 3D positions
positions = np.column_stack([
    data['x'],          # X coordinates
    data['y'],          # Y coordinates  
    data['z']           # Z coordinates (or elevation)
])

# Create colors (optional)
colors = create_heatmap_colors(data['temperature'], 'fire')

# Generate visualization
viz_data = create_particle_system(
    positions=positions,
    colors=colors,
    sizes=data['intensity'] / 10,
    point_size=3
)

print(f"Created {len(positions)} particles")
```

#### Advanced Fire Risk Visualization
```python
# Calculate enhanced fire risk
def calculate_risk(temp, humidity, wind, elevation):
    base_risk = (temp * wind) / (humidity + 10)
    elevation_factor = 1 + (elevation / 1000)
    return base_risk * elevation_factor

data['risk'] = calculate_risk(
    data['temperature'], 
    data['humidity'],
    data['wind_speed'], 
    data['elevation']
)

# Create time-animated visualization
for time_step in data['time'].unique():
    time_data = data[data['time'] == time_step]
    
    positions = generate_particle_positions(time_data[['lat', 'lon']], 'elevation')
    colors = create_heatmap_colors(time_data['risk'], 'fire')
    
    viz_data = create_particle_system(
        positions=positions,
        colors=colors,
        sizes=time_data['risk'] / 5
    )
    
    time.sleep(0.5)  # Animation delay
```

#### Mesh Terrain Visualization
```python
# Create 3D terrain mesh from elevation data
vertices, faces = create_terrain_mesh(
    data['latitude'], 
    data['longitude'], 
    data['elevation']
)

terrain_viz = create_mesh_visualization(
    vertices=vertices,
    faces=faces,
    color=0x8B4513,  # Brown terrain
    wireframe=False
)
```

### Available Visualization Functions

| Function | Purpose | Example |
|----------|---------|---------|
| `create_particle_system()` | Scatter plots, point clouds | Fire locations, sensor networks |
| `create_mesh_visualization()` | 3D surfaces, terrain | Elevation maps, temperature surfaces |
| `create_line_visualization()` | Paths, connections | Flight routes, river networks |
| `create_heatmap_colors()` | Color mapping | Temperature, risk levels |
| `generate_particle_positions()` | Coordinate conversion | Lat/lon to 3D space |
| `calculate_fire_risk()` | Fire risk scoring | Weather-based risk calculation |

## 🔥 Real-World Use Cases

### 1. Australian Bushfire Analysis
```python
# Load bushfire weather data
data = pd.read_csv('bushfire_stations.csv')

# Calculate McArthur Fire Danger Index
data['fire_risk'] = calculate_fire_risk(
    data['temp'], data['humidity'], data['wind_speed']
)

# 3D visualization with terrain
positions = bushfire_coordinates(data['lat'], data['lon'], data['elevation'])
colors = fire_risk_colors(data['fire_risk'])

viz_data = create_particle_system(positions, colors, data['fire_risk']/10)
```

### 2. Ocean Current Flow
```python
# Oceanographic data visualization
ocean_data = pd.read_csv('ocean_currents.csv')

# Create flow vectors
vectors = create_flow_vectors(
    ocean_data[['u_velocity', 'v_velocity', 'w_velocity']]
)

# Color by temperature
colors = create_heatmap_colors(ocean_data['temperature'], 'ocean')

viz_data = create_line_visualization(vectors, colors)
```

### 3. Sensor Network Monitoring
```python
# IoT sensor network
sensors = pd.read_csv('sensor_network.csv')

# Real-time positions
positions = sensor_positions(sensors['lat'], sensors['lon'], sensors['elevation'])

# Status colors (green=active, red=fault)
colors = status_colors(sensors['status'])

# Size by battery level
sizes = sensors['battery_level'] / 20

viz_data = create_particle_system(positions, colors, sizes)
```

## ⚙️ Configuration & Settings

### Command Line Options
```bash
# Basic usage
visflow

# Custom port
visflow --port 8080

# Development mode (auto-reload)
visflow --dev

# Allow external connections
visflow --host 0.0.0.0

# Don't open browser automatically
visflow --no-browser

# Set logging level
visflow --log-level debug
```

### Environment Variables
```bash
# Set default port
export VISFLOW_PORT=8080

# Set default host
export VISFLOW_HOST=0.0.0.0

# Enable debug mode
export VISFLOW_DEBUG=true
```

### Settings Panel
Access via the ⚙️ button in the top navigation:

- **Editor Theme**: Dark/Light mode
- **Auto-run Code**: Execute on changes
- **3D Rendering**: Anti-aliasing, shadows
- **Performance**: Max particles limit

## 🎮 Keyboard Shortcuts & Controls

### Code Editor
- `Ctrl+R` / `Cmd+R`: Execute Python code
- `Ctrl+S` / `Cmd+S`: Auto-save (local storage)
- `Ctrl+Z` / `Cmd+Z`: Undo
- `Ctrl+/` / `Cmd+/`: Toggle comment
- `F11`: Fullscreen editor

### 3D Visualization
- **Mouse Wheel**: Zoom in/out
- **Left Click + Drag**: Rotate camera
- **Right Click + Drag**: Pan view
- **Middle Click + Drag**: Pan view (alternative)
- **Double Click**: Reset camera to center
- **Spacebar**: Play/pause animations (when available)

### Interface
- `Tab`: Switch between panels
- `F12`: Open browser dev tools
- `Esc`: Close modals/panels

## 📊 Sample Datasets Included

### 1. Bushfire Data (`bushfire_data.csv`)
- **Size**: 1,000+ data points
- **Columns**: latitude, longitude, temperature, humidity, wind_speed, fire_intensity, elevation, time_hours
- **Use Case**: Fire risk modeling, spread prediction
- **Visualization**: 3D particle system with terrain

### 2. Ocean Currents (`ocean_currents.csv`)
- **Size**: 500+ measurements at multiple depths
- **Columns**: latitude, longitude, depth, u_velocity, v_velocity, w_velocity, temperature, salinity, pressure  
- **Use Case**: Oceanographic flow analysis
- **Visualization**: Flow vectors, particle tracking

### 3. Wind Patterns (`wind_patterns.csv`)
- **Size**: 800+ atmospheric measurements
- **Columns**: latitude, longitude, altitude, wind_u, wind_v, wind_w, wind_speed, wind_direction, temperature, pressure, humidity
- **Use Case**: Weather modeling, atmospheric studies
- **Visualization**: 3D wind field, streamlines

## 🛠️ Advanced Features

### Custom Data Processing Functions
```python
# Create your own utility functions
def custom_risk_calculation(data):
    """Custom risk model for your domain."""
    risk = (data['factor1'] * data['factor2']) / (data['factor3'] + 1)
    return risk

# Use in visualizations
data['custom_risk'] = custom_risk_calculation(data)
colors = create_heatmap_colors(data['custom_risk'], 'custom')
```

### Animation & Time Series
```python
# Animate data over time
time_steps = sorted(data['timestamp'].unique())

for i, timestamp in enumerate(time_steps):
    frame_data = data[data['timestamp'] == timestamp]
    
    # Create visualization for this time step
    viz_data = create_particle_system(
        positions=frame_data[['x', 'y', 'z']].values,
        colors=time_colors(i, len(time_steps)),
        sizes=frame_data['intensity'].values
    )
    
    # Small delay for smooth animation
    time.sleep(0.1)
```

### Export & Sharing
```python
# Export visualization data
viz_export = {
    'metadata': {
        'created': datetime.now().isoformat(),
        'dataset': 'bushfire_analysis',
        'points': len(viz_data['positions'])
    },
    'visualization': viz_data
}

# Save to JSON for later use
with open('visualization_export.json', 'w') as f:
    json.dump(viz_export, f, indent=2)
```

## 🔧 Development & Customization

### Project Structure
```
visflow/
├── src/visflow/
│   ├── __init__.py          # Package entry point
│   ├── __main__.py          # CLI entry point  
│   ├── server.py            # FastAPI backend
│   ├── data_processor.py    # Python data processing
│   └── static/              # Frontend assets
│       ├── index.html       # Main application
│       ├── app.js           # Three.js engine
│       ├── style.css        # UI styling
│       └── sample_data/     # Example datasets
├── examples/                # Example scripts
├── tests/                   # Test suite
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=visflow

# Run specific test file
pytest tests/test_data_processing.py -v
```

### Development Mode
```bash
# Start with auto-reload
visflow --dev

# Or manually
uvicorn visflow.server:app --reload --host 127.0.0.1 --port 8000
```

### Adding New Visualization Types
```python
# In data_processor.py, add new utility function
def create_custom_visualization(data, **kwargs):
    """Create your custom visualization type."""
    return {
        'type': 'custom_type',
        'data': process_custom_data(data),
        'options': kwargs
    }

# In app.js, handle new type
createVisualizationObject(data) {
    switch (data.type) {
        case 'custom_type':
            this.createCustomVisualization(data);
            break;
        // ... existing cases
    }
}
```

## 🚨 Troubleshooting

### Common Issues

#### "Port already in use"
```bash
# VisFlow auto-detects free ports, but if needed:
visflow --port 8001

# Or kill the process using the port
lsof -ti:8000 | xargs kill -9
```

#### "Module not found" errors
```bash
# Ensure all dependencies are installed
pip install --upgrade visflow

# Or reinstall
pip uninstall visflow
pip install visflow
```

#### Slow 3D performance
- Reduce particle count in visualizations
- Disable anti-aliasing in settings
- Close other browser tabs
- Update graphics drivers

#### WebSocket connection failed
- Check firewall settings
- Try different port: `visflow --port 8080`
- Disable VPN/proxy temporarily

### Debug Mode
```bash
# Enable verbose logging
visflow --log-level debug

# Check browser console (F12) for client-side errors
# Check terminal for server-side errors
```

### Performance Optimization

#### For Large Datasets (>100K points)
```python
# Sample large datasets
if len(data) > 50000:
    data = data.sample(50000)

# Use lower precision for positions
positions = positions.astype(np.float32)

# Simplify colors
colors = simple_color_map(data['value'])
```

#### Memory Management
```python
# Clear old visualizations
viz_data = None  # Clear previous viz_data

# Process data in chunks
chunk_size = 10000
for chunk in pd.read_csv('large_file.csv', chunksize=chunk_size):
    process_chunk(chunk)
```

## 📚 API Reference

### Data Processing Functions

#### `create_particle_system(positions, colors=None, sizes=None, **kwargs)`
Create a particle system visualization.

**Parameters:**
- `positions` (array-like): 3D positions as [[x,y,z], ...]
- `colors` (array-like, optional): RGB colors as [[r,g,b], ...]  
- `sizes` (array-like, optional): Point sizes as [size1, size2, ...]
- `**kwargs`: Additional options (point_size, opacity, material)

**Returns:**
- `dict`: Visualization data for Three.js

#### `create_heatmap_colors(values, colormap='viridis')`
Generate colors for heatmap visualization.

**Parameters:**
- `values` (pd.Series): Numeric values to map
- `colormap` (str): Color scheme ('viridis', 'fire', 'ocean')

**Returns:**
- `np.ndarray`: RGB color array

#### `calculate_fire_risk(temperature, humidity, wind_speed)`
Calculate fire risk based on weather conditions.

**Parameters:**
- `temperature` (pd.Series): Temperature in Celsius
- `humidity` (pd.Series): Relative humidity (%)
- `wind_speed` (pd.Series): Wind speed (km/h)

**Returns:**
- `pd.Series`: Fire risk scores

### Server Endpoints

#### `POST /upload`
Upload and process data files.

#### `POST /execute`  
Execute Python code in safe environment.

#### `GET /datasets`
List all stored datasets.

#### `GET /datasets/{id}`
Retrieve specific dataset.

#### `WebSocket /ws`
Real-time communication channel.

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup
```bash
# Clone the repository
git clone https://github.com/visflow-team/visflow.git
cd visflow

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Start development server
visflow --dev
```

### Contribution Guidelines
1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature-name`
3. **Write** tests for new functionality
4. **Ensure** all tests pass: `pytest`
5. **Submit** a pull request

### Areas for Contribution
- 🎨 New visualization types
- 📊 Additional sample datasets
- 🌍 Geospatial projections
- ⚡ Performance optimizations
- 📱 Mobile responsiveness
- 🌐 Internationalization

## 📄 License

VisFlow is open source software licensed under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **Three.js** - Amazing 3D graphics library
- **FastAPI** - Modern Python web framework  
- **Monaco Editor** - VS Code editor for the web
- **pandas** - Powerful data analysis library
- **uvicorn** - Lightning-fast ASGI server

## 📞 Support & Community

- **🐛 Bug Reports**: [GitHub Issues](https://github.com/visflow-team/visflow/issues)
- **💡 Feature Requests**: [GitHub Discussions](https://github.com/visflow-team/visflow/discussions)
- **📖 Documentation**: [visflow.readthedocs.io](https://visflow.readthedocs.io/)
- **💬 Community**: [Discord Server](https://discord.gg/visflow)

## 🚀 What's Next?

Check out our [roadmap](ROADMAP.md) for upcoming features:

- 🎮 VR/AR support
- 🤖 AI-powered visualization suggestions
- ☁️ Cloud deployment options
- 📱 Mobile app
- 🎬 Animation timeline editor
- 🌐 Real-time collaboration

---

**Ready to transform your data into stunning 3D visualizations?**

```bash
pip install visflow && visflow
```

**Happy visualizing! 📊✨**