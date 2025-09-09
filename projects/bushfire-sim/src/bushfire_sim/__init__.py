"""Bushfire Simulation - Real-time fire spread modeling with Rust acceleration."""

from ._core import FireSimulation, run_batch_simulation
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional
import time

class BushfireModel:
    """High-level Python interface for bushfire simulation."""
    
    # Australian fire danger ratings (adjusted for better visual demonstrations)
    DANGER_LEVELS = {
        'low': {'wind': 15, 'humidity': 65, 'temp': 25},
        'moderate': {'wind': 20, 'humidity': 50, 'temp': 30},
        'high': {'wind': 30, 'humidity': 35, 'temp': 35},
        'very_high': {'wind': 40, 'humidity': 25, 'temp': 40},
        'severe': {'wind': 50, 'humidity': 15, 'temp': 45},
        'extreme': {'wind': 65, 'humidity': 8, 'temp': 48},
        'catastrophic': {'wind': 80, 'humidity': 5, 'temp': 50},
    }
    
    def __init__(self, width: int = 100, height: int = 100):
        self.width = width
        self.height = height
        self.sim = None
        self.history = []
        
    def set_conditions(self, danger_level: str = 'moderate', **overrides):
        """Set weather conditions based on Australian fire danger ratings."""
        if danger_level not in self.DANGER_LEVELS:
            raise ValueError(f"Unknown danger level: {danger_level}")
            
        conditions = self.DANGER_LEVELS[danger_level].copy()
        conditions.update(overrides)
        
        self.sim = FireSimulation(
            self.width, 
            self.height,
            conditions['wind'],
            0.0,  # wind direction (radians)
            conditions['humidity'],
            conditions['temp']
        )
        
        return conditions
    
    def ignite(self, locations: List[Tuple[int, int]]):
        """Start fires at specified locations."""
        if not self.sim:
            raise RuntimeError("Must set conditions first")
            
        for x, y in locations:
            self.sim.ignite(x, y)
    
    def simulate_steps(self, steps: int, save_history: bool = True):
        """Run simulation for specified steps."""
        if not self.sim:
            raise RuntimeError("Must set conditions first")
            
        results = []
        for i in range(steps):
            state = self.get_state()
            if save_history:
                self.history.append(state)
            results.append(state)
            
            self.sim.step()
            
        return results
    
    def get_state(self) -> np.ndarray:
        """Get current simulation state as 2D numpy array."""
        if not self.sim:
            return np.zeros((self.height, self.width))
            
        flat_state = self.sim.get_state()
        return np.array(flat_state).reshape(self.height, self.width)
    
    def get_stats(self):
        """Get simulation statistics."""
        if not self.sim:
            return None
            
        step, empty, vegetation, burning, burnt = self.sim.get_stats()
        total = empty + vegetation + burning + burnt
        
        return {
            'step': step,
            'empty': empty,
            'vegetation': vegetation, 
            'burning': burning,
            'burnt': burnt,
            'fire_spread_pct': (burnt / total * 100) if total > 0 else 0,
            'active_fire_pct': (burning / total * 100) if total > 0 else 0,
        }
    
    def benchmark_rust_vs_python(self, steps: int = 50) -> dict:
        """Benchmark Rust vs Python implementation for performance comparison."""
        
        # Rust implementation
        start_time = time.time()
        rust_results = run_batch_simulation(
            self.width, self.height, steps, 
            [(self.width//2, self.height//2)],  # Center ignition
            25.0, 40.0, 35.0  # Moderate-high conditions
        )
        rust_time = time.time() - start_time
        
        # Pure Python simulation (simplified for comparison)
        start_time = time.time()
        python_results = self._python_simulation(steps)
        python_time = time.time() - start_time
        
        return {
            'rust_time': rust_time,
            'python_time': python_time,
            'speedup': python_time / rust_time if rust_time > 0 else float('inf'),
            'rust_steps': len(rust_results),
            'python_steps': len(python_results)
        }
    
    def _python_simulation(self, steps: int):
        """Simple Python implementation for benchmarking."""
        grid = np.random.choice([0, 1], size=(self.height, self.width), p=[0.25, 0.75])
        grid[self.height//2, self.width//2] = 2  # Start fire at center
        
        results = []
        for _ in range(steps):
            results.append(grid.copy())
            new_grid = grid.copy()
            
            # Simple fire spread (much slower than Rust)
            for y in range(1, self.height-1):
                for x in range(1, self.width-1):
                    if grid[y, x] == 1:  # Vegetation
                        neighbors = grid[y-1:y+2, x-1:x+2]
                        if np.any(neighbors == 2):  # Burning neighbor
                            if np.random.random() < 0.3:  # Simple probability
                                new_grid[y, x] = 2
                    elif grid[y, x] == 2:  # Burning
                        new_grid[y, x] = 3  # Burnt
            
            grid = new_grid
            
        return results

def create_visualization(states: List[np.ndarray], title: str = "Bushfire Simulation"):
    """Create a matplotlib visualization of simulation results."""
    
    # Color map for fire states
    colors = ['white', 'green', 'red', 'black']  # Empty, Vegetation, Burning, Burnt
    cmap = plt.matplotlib.colors.ListedColormap(colors)
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(title, fontsize=16)
    
    # Show key frames
    frames = [0, len(states)//3, 2*len(states)//3, -1]
    frame_titles = ['Initial', 'Early Spread', 'Mid Spread', 'Final']
    
    for i, (ax, frame_idx, frame_title) in enumerate(zip(axes.flat, frames, frame_titles)):
        if frame_idx < len(states):
            im = ax.imshow(states[frame_idx], cmap=cmap, vmin=0, vmax=3)
            ax.set_title(f'{frame_title} (Step {frame_idx if frame_idx >= 0 else len(states)-1})')
            ax.set_xticks([])
            ax.set_yticks([])
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=axes, orientation='horizontal', pad=0.1, fraction=0.05)
    cbar.set_ticks([0, 1, 2, 3])
    cbar.set_ticklabels(['Empty', 'Vegetation', 'Burning', 'Burnt'])
    
    plt.tight_layout()
    return fig

__version__ = "0.1.0"
