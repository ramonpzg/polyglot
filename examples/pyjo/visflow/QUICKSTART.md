# 🚀 VisFlow Quick Start Guide

## Installation & Setup

### 1. Navigate to VisFlow Directory
```bash
cd /home/rpg/d2/projects/polyglot/examples/pyjo/visflow
```

### 2. Install Dependencies
```bash
# Install all dependencies (this is done already!)
uv sync
```

### 3. Launch VisFlow
```bash
# Method 1: Using the entry point command
uv run visflow

# Method 2: Using Python module
uv run python -m visflow

# Method 3: Development mode (auto-reload on code changes)
uv run visflow --dev
```

## 🎯 Quick Demo (30 seconds)

1. **Start VisFlow**:
   ```bash
   uv run visflow
   ```
   - Opens automatically at http://localhost:8000
   - Auto-detects free port if 8000 is busy

2. **Try Sample Data**:
   - Click "🔥 Bushfire Example" button
   - Watch 1000+ data points render in 3D
   - Use mouse to rotate, zoom, pan

3. **Live Coding**:
   - Press `Ctrl+R` to execute the Python code
   - Modify the code and run again
   - See changes instantly in 3D

## 🎮 Controls

- **Mouse Wheel**: Zoom in/out
- **Left Drag**: Rotate 3D view
- **Right Drag**: Pan camera
- **Ctrl+R**: Execute Python code
- **Esc**: Close modals

## 📁 Upload Your Data

1. Click "📁 Upload" button
2. Select a CSV file with columns like:
   - `latitude`, `longitude` (coordinates)
   - `temperature`, `value`, `intensity` (data)
   - `time`, `timestamp` (optional, for animation)

## 🔧 Command Line Options

```bash
# Custom port
uv run visflow --port 8080

# Allow external connections
uv run visflow --host 0.0.0.0

# Don't auto-open browser
uv run visflow --no-browser

# Development mode (auto-reload)
uv run visflow --dev

# Show help
uv run visflow --help
```

## 🚨 Troubleshooting

### Port Already in Use
```bash
uv run visflow --port 8001
```

### Python Dependencies Missing
```bash
uv sync  # Reinstall dependencies
```

### Browser Won't Open Automatically
- Manually navigate to http://localhost:8000
- Or use `uv run visflow --no-browser`

### Performance Issues
- Close other browser tabs
- Reduce dataset size (<50K points)
- Disable anti-aliasing in settings

## 📊 Sample Python Code

Try this in the code editor:

```python
import pandas as pd
import numpy as np

# Create spiral data
n = 5000
t = np.linspace(0, 4*np.pi, n)
r = np.linspace(0, 20, n)

# 3D spiral positions
positions = np.column_stack([
    r * np.cos(t),
    r * np.sin(t),
    t * 2
])

# Color gradient
colors = np.zeros((n, 3))
colors[:, 0] = t / (4*np.pi)  # Red increases
colors[:, 2] = 1 - t / (4*np.pi)  # Blue decreases

# Create visualization
viz_data = create_particle_system(
    positions=positions,
    colors=colors,
    sizes=np.ones(n) * 2
)

print(f"Created spiral with {n} particles")
```

## ✅ Ready to Go!

VisFlow is now fully functional. Check out:
- **README.md** - Comprehensive documentation
- **TUTORIAL.md** - JavaScript tutorial for Python developers
- **examples/** - Sample visualization scripts

**Happy visualizing! 📊✨**