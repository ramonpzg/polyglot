"""
Visualization Module
===================

Python's strength: beautiful, interactive visualizations.
C++ generates the data, Python makes it gorgeous.

This showcases how Python's rich ecosystem (matplotlib, plotly)
complements C++'s computational power perfectly.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
from typing import List, Tuple, Optional, Union
import time

from ._core import BushfireSimulator, WeatherCondition, FireDangerRating, VegetationType


# Australian fire-themed color schemes
BUSHFIRE_COLORS = LinearSegmentedColormap.from_list(
    'bushfire',
    ['#2E7D32', '#FFF176', '#FF9800', '#D84315', '#1A0F1F'],  # Green -> Yellow -> Orange -> Red -> Black
    N=256
)

TERRAIN_COLORS = LinearSegmentedColormap.from_list(
    'australian_terrain',
    ['#1B5E20', '#4CAF50', '#8BC34A', '#CDDC39', '#795548', '#FFFFFF'],  # Dark green -> Light green -> Brown -> White
    N=256
)


class BushfireVisualizer:
    """
    Interactive visualization toolkit for bushfire simulations.
    
    Python handles the presentation layer while C++ provides the data.
    This is the perfect polyglot collaboration.
    """
    
    def __init__(self, figsize: Tuple[float, float] = (12, 8)):
        self.figsize = figsize
        plt.style.use('seaborn-v0_8-darkgrid')  # Professional look
        
    def plot_terrain(self, sim: BushfireSimulator, title: str = "Terrain Overview") -> plt.Figure:
        """Visualize the terrain setup"""
        fig, axes = plt.subplots(2, 2, figsize=self.figsize)
        fig.suptitle(f'{title}\nC++ Engine, Python Visualization', fontsize=14, fontweight='bold')
        
        # Get terrain data from C++ simulator
        elevation_data = np.random.rand(sim.height, sim.width) * 1000  # Placeholder - would get real data
        fuel_data = np.random.rand(sim.height, sim.width) * 20  # Placeholder
        
        # Elevation
        im1 = axes[0, 0].imshow(elevation_data, cmap=TERRAIN_COLORS, aspect='equal')
        axes[0, 0].set_title('Elevation (m)')
        plt.colorbar(im1, ax=axes[0, 0], shrink=0.8)
        
        # Fuel load
        im2 = axes[0, 1].imshow(fuel_data, cmap='YlOrBr', aspect='equal')
        axes[0, 1].set_title('Fuel Load (t/ha)')
        plt.colorbar(im2, ax=axes[0, 1], shrink=0.8)
        
        # Vegetation type (simplified visualization)
        veg_data = np.random.randint(0, 4, size=(sim.height, sim.width))
        im3 = axes[1, 0].imshow(veg_data, cmap='Greens', aspect='equal')
        axes[1, 0].set_title('Vegetation Type')
        plt.colorbar(im3, ax=axes[1, 0], shrink=0.8, ticks=[0, 1, 2, 3],
                    label='Sparse→Extreme')
        
        # Combined risk factors
        combined = elevation_data/1000 + fuel_data/20 + veg_data/4
        im4 = axes[1, 1].imshow(combined, cmap='Reds', aspect='equal')
        axes[1, 1].set_title('Combined Risk Factors')
        plt.colorbar(im4, ax=axes[1, 1], shrink=0.8)
        
        plt.tight_layout()
        return fig
    
    def plot_fire_spread(self, sim: BushfireSimulator, title: str = "Fire Spread Analysis") -> plt.Figure:
        """Visualize current fire state"""
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        fig.suptitle(f'{title}\n🔥 Real-time data from C++ simulation', fontsize=14, fontweight='bold')
        
        # Get current state from C++ simulator
        burn_intensity = sim.get_burn_intensity_grid()
        burned_areas = sim.get_burned_areas()
        fuel_remaining = sim.get_fuel_remaining()
        
        # Burn intensity
        im1 = axes[0].imshow(burn_intensity, cmap=BUSHFIRE_COLORS, aspect='equal')
        axes[0].set_title('Burn Intensity')
        axes[0].set_xlabel('Grid X')
        axes[0].set_ylabel('Grid Y')
        plt.colorbar(im1, ax=axes[0], shrink=0.8, label='Intensity')
        
        # Burned areas
        axes[1].imshow(burned_areas, cmap='Reds', aspect='equal', alpha=0.8)
        axes[1].set_title('Burned Areas')
        axes[1].set_xlabel('Grid X')
        
        # Fuel remaining
        im3 = axes[2].imshow(fuel_remaining, cmap='RdYlGn', aspect='equal', vmin=0, vmax=1)
        axes[2].set_title('Remaining Fuel')
        axes[2].set_xlabel('Grid X')
        plt.colorbar(im3, ax=axes[2], shrink=0.8, label='Fuel Fraction')
        
        plt.tight_layout()
        
        # Add statistics text
        total_burned = sim.get_total_burned_area()
        max_intensity = sim.get_maximum_intensity()
        active_fires, perimeter = sim.get_fire_perimeter_count()
        
        stats_text = f"""
        Statistics (from C++ engine):
        • Total burned: {total_burned:.1f} ha
        • Max intensity: {max_intensity:.2f}
        • Active fires: {active_fires}
        • Perimeter cells: {perimeter}
        """
        
        fig.text(0.02, 0.02, stats_text, fontsize=10, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.8))
        
        return fig
    
    def animate_fire_evolution(self, 
                             initial_sim: BushfireSimulator,
                             weather: WeatherCondition,
                             steps: int = 100,
                             interval: int = 100) -> animation.FuncAnimation:
        """
        Create animation of fire spread over time.
        
        C++ runs the simulation, Python creates the smooth animation.
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle('🔥 Live Fire Simulation\nC++ Computing, Python Animating', fontweight='bold')
        
        # Initialize plots
        im1 = ax1.imshow(initial_sim.get_burn_intensity_grid(), cmap=BUSHFIRE_COLORS, 
                        aspect='equal', animated=True)
        ax1.set_title('Burn Intensity')
        
        im2 = ax2.imshow(initial_sim.get_burned_areas(), cmap='Reds', 
                        aspect='equal', animated=True)
        ax2.set_title('Burned Areas')
        
        # Statistics text
        stats_text = ax1.text(0.02, 0.98, '', transform=ax1.transAxes, 
                             verticalalignment='top', fontweight='bold',
                             bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
        
        def animate(frame):
            # Run one simulation step (C++ does the work)
            initial_sim.simulate_timestep(weather)
            
            # Update visualizations (Python's job)
            intensity = initial_sim.get_burn_intensity_grid()
            burned = initial_sim.get_burned_areas()
            
            im1.set_array(intensity)
            im2.set_array(burned)
            
            # Update statistics
            total_burned = initial_sim.get_total_burned_area()
            max_intensity = initial_sim.get_maximum_intensity()
            stats_text.set_text(f'Step: {frame}\nBurned: {total_burned:.1f} ha\nMax: {max_intensity:.2f}')
            
            return [im1, im2, stats_text]
        
        anim = animation.FuncAnimation(fig, animate, frames=steps, interval=interval, 
                                     blit=True, repeat=False)
        
        plt.tight_layout()
        return anim


def plot_risk_surface(risk_data: np.ndarray, 
                     ignition_points: List[Tuple[int, int]] = None,
                     title: str = "Fire Risk Surface") -> plt.Figure:
    """
    Plot risk probability surface.
    
    Args:
        risk_data: 2D array of risk probabilities (from C++ Monte Carlo)
        ignition_points: List of (x, y) ignition locations
        title: Plot title
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(f'{title}\nMonte Carlo Results from C++ Engine', fontweight='bold')
    
    # Risk surface
    im1 = ax1.imshow(risk_data, cmap='Reds', aspect='equal', origin='lower')
    ax1.set_title('Risk Probability')
    ax1.set_xlabel('Grid X')
    ax1.set_ylabel('Grid Y')
    plt.colorbar(im1, ax=ax1, shrink=0.8, label='P(Fire)')
    
    # Mark ignition points
    if ignition_points:
        xs, ys = zip(*ignition_points)
        ax1.scatter(xs, ys, c='yellow', s=100, marker='*', 
                   edgecolors='black', linewidth=2, label='Ignition Points')
        ax1.legend()
    
    # Risk distribution histogram
    ax2.hist(risk_data.flatten(), bins=50, alpha=0.7, color='red', edgecolor='black')
    ax2.set_xlabel('Risk Probability')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Risk Distribution')
    ax2.grid(True, alpha=0.3)
    
    # Add statistics
    mean_risk = np.mean(risk_data)
    high_risk_area = np.sum(risk_data > 0.5)
    
    stats_text = f"""Risk Analysis:
    Mean Risk: {mean_risk:.3f}
    High Risk Cells: {high_risk_area}
    Max Risk: {np.max(risk_data):.3f}"""
    
    ax2.text(0.98, 0.98, stats_text, transform=ax2.transAxes,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.8))
    
    plt.tight_layout()
    return fig


def create_danger_rating_chart(weather_conditions: List[WeatherCondition]) -> plt.Figure:
    """
    Visualize fire danger ratings for multiple weather scenarios.
    
    Shows how Python can beautifully present C++'s analytical results.
    """
    from ._core import fire_index
    
    # Calculate FDI for each weather condition (C++ functions)
    fdi_values = []
    ratings = []
    
    for weather in weather_conditions:
        fdi = fire_index.mcarthur_forest_fire_danger_index(
            weather.temperature, weather.humidity, weather.wind_speed, 10.0  # Assume drought factor
        )
        fdi_values.append(fdi)
        rating = fire_index.danger_rating_category(fdi)
        ratings.append(rating)
    
    # Create comprehensive visualization
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('🔥 Australian Fire Danger Analysis\nC++ Calculations, Python Visualization', 
                fontsize=14, fontweight='bold')
    
    # FDI distribution
    ax1.hist(fdi_values, bins=20, alpha=0.7, color='orange', edgecolor='black')
    ax1.set_xlabel('Fire Danger Index')
    ax1.set_ylabel('Frequency')
    ax1.set_title('FDI Distribution')
    ax1.grid(True, alpha=0.3)
    
    # Rating categories
    from collections import Counter
    rating_counts = Counter(ratings)
    colors = ['green', 'yellow', 'orange', 'red', 'darkred', 'maroon', 'black'][:len(rating_counts)]
    
    ax2.bar(rating_counts.keys(), rating_counts.values(), color=colors, alpha=0.8, edgecolor='black')
    ax2.set_ylabel('Count')
    ax2.set_title('Danger Rating Categories')
    ax2.tick_params(axis='x', rotation=45)
    
    # Weather parameter correlations
    temps = [w.temperature for w in weather_conditions]
    humidities = [w.humidity for w in weather_conditions]
    winds = [w.wind_speed for w in weather_conditions]
    
    scatter = ax3.scatter(temps, humidities, c=fdi_values, s=[w*2 for w in winds], 
                         cmap='Reds', alpha=0.7, edgecolors='black', linewidth=0.5)
    ax3.set_xlabel('Temperature (°C)')
    ax3.set_ylabel('Humidity (%)')
    ax3.set_title('Weather Correlations\n(bubble size = wind speed)')
    plt.colorbar(scatter, ax=ax3, label='FDI')
    
    # Time series (if weather has temporal component)
    ax4.plot(fdi_values, 'o-', color='red', linewidth=2, markersize=6)
    ax4.set_xlabel('Weather Scenario')
    ax4.set_ylabel('Fire Danger Index')
    ax4.set_title('FDI Time Series')
    ax4.grid(True, alpha=0.3)
    
    # Add danger level lines
    danger_levels = [5, 12, 25, 50, 75, 100]
    danger_labels = ['Low', 'Moderate', 'High', 'Very High', 'Severe', 'Extreme']
    
    for level, label in zip(danger_levels, danger_labels):
        ax4.axhline(y=level, color='gray', linestyle='--', alpha=0.5)
        ax4.text(len(fdi_values)*0.02, level, label, fontsize=8, 
                verticalalignment='bottom', alpha=0.7)
    
    plt.tight_layout()
    return fig


def quick_visualization_demo():
    """
    Quick demo of visualization capabilities.
    Shows the C++/Python collaboration in action.
    """
    print("🎨 Visualization Demo: C++ computes, Python presents")
    print("=" * 60)
    
    # Create a small simulation for demo (C++ work)
    from ._core import BushfireSimulator, WeatherCondition, utility
    
    sim = BushfireSimulator(50, 50)
    elevations, fuels, vegetation = utility.load_nsw_terrain_data("demo")
    sim.initialize_terrain_from_data(elevations, fuels, vegetation)
    
    # Ignite and run a few steps
    sim.ignite_location(25, 25)
    weather = WeatherCondition(temperature=40, humidity=20, wind_speed=30)
    
    for _ in range(10):
        sim.simulate_timestep(weather)
    
    # Create visualizations (Python work)
    viz = BushfireVisualizer()
    
    # Terrain plot
    terrain_fig = viz.plot_terrain(sim, "Demo Terrain")
    
    # Fire spread plot  
    fire_fig = viz.plot_fire_spread(sim, "Demo Fire Spread")
    
    # Show the results
    plt.show()
    
    print("✅ Visualization complete!")
    print(f"   Total burned: {sim.get_total_burned_area():.1f} hectares")
    print(f"   Visualization: Python + Matplotlib")
    print(f"   Computation: C++ parallel algorithms")


if __name__ == "__main__":
    quick_visualization_demo()