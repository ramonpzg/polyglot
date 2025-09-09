"""
Australian Bushfire Risk Modeler
================================

A high-performance bushfire simulation and risk analysis system combining:
- C++20/23 computational engine for speed
- Python orchestration for flexibility
- Modern polyglot architecture

This project showcases how Python can elegantly orchestrate complex simulations
while C++ handles the performance-critical computations. Perfect example of
each language doing what it does best.

Key Features:
- Real-time bushfire spread simulation
- Monte Carlo risk analysis (massively parallel)
- Australian-specific fire danger indices
- Interactive visualization and analysis
- Modern C++ features (concepts, ranges, constexpr, parallel algorithms)
"""

# Import the C++ core engine
from ._core import (
    # Core simulation classes
    BushfireSimulator,
    WeatherCondition,
    TerrainCell,
    
    # Enums and types
    VegetationType,
    FireDangerRating,
    
    # Submodules
    fire_index,
    utility,
    
    # Version info
    __version__,
    __cpp_standard__,
    __has_concepts__,
    __has_ranges__,
)

# Python orchestration layer
from .orchestrator import (
    BushfireAnalyst,
    RiskAssessment,
    create_blue_mountains_scenario,
    create_extreme_weather_scenario,
)

from .visualization import (
    BushfireVisualizer,
    plot_risk_surface,
    animate_fire_spread,
    create_danger_rating_chart,
)

from .benchmarks import (
    BenchmarkRunner,
    compare_python_vs_cpp,
    run_performance_suite,
)

# Make common operations more Pythonic
def quick_simulation(width=100, height=100, steps=50, weather=None):
    """
    Quick bushfire simulation for exploration.
    
    Perfect for Jupyter notebooks and rapid prototyping.
    The heavy lifting happens in C++, Python just orchestrates.
    """
    if weather is None:
        weather = WeatherCondition(
            temperature=35.0,  # Hot day in Sydney
            humidity=25.0,     # Low humidity = danger
            wind_speed=25.0,   # Moderate wind
            fuel_moisture=8.0  # Dry fuel
        )
    
    # Create simulator (C++ constructor)
    sim = BushfireSimulator(width, height)
    
    # Generate realistic terrain (C++ utility function)
    elevations, fuel_loads, vegetation = utility.load_nsw_terrain_data("blue_mountains")
    sim.initialize_terrain_from_data(elevations, fuel_loads, vegetation)
    
    # Start fire in center
    sim.ignite_location(width // 2, height // 2)
    
    # Run simulation (C++ parallel algorithms do the work)
    for step in range(steps):
        sim.simulate_timestep(weather)
    
    return sim

def main() -> None:
    """Demo the system capabilities"""
    print("🔥 Australian Bushfire Risk Modeler")
    print("=" * 40)
    
    # Quick demo
    sim = quick_simulation(50, 50, 20)
    burned_area = sim.get_total_burned_area()
    max_intensity = sim.get_maximum_intensity()
    
    print(f"Simulation complete:")
    print(f"  Burned area: {burned_area:.1f} hectares")
    print(f"  Max intensity: {max_intensity:.2f}")
    print(f"  C++ Standard: {__cpp_standard__}")
    print(f"  Has Concepts: {__has_concepts__}")
    print(f"  Has Ranges: {__has_ranges__}")

# Expose key constants
AUSTRALIAN_FIRE_SEASONS = {
    'summer': (12, 1, 2),    # Dec, Jan, Feb
    'autumn': (3, 4, 5),     # Mar, Apr, May  
    'winter': (6, 7, 8),     # Jun, Jul, Aug
    'spring': (9, 10, 11),   # Sep, Oct, Nov
}

EXTREME_CONDITIONS = WeatherCondition(
    temperature=47.0,    # Black Summer 2019-2020 levels
    humidity=15.0,       # Dangerously low
    wind_speed=60.0,     # Severe wind warning
    fuel_moisture=5.0    # Critically dry
)

# Export all the important bits
__all__ = [
    # C++ core
    'BushfireSimulator',
    'WeatherCondition', 
    'TerrainCell',
    'VegetationType',
    'FireDangerRating',
    'fire_index',
    'utility',
    
    # Python orchestration
    'BushfireAnalyst',
    'RiskAssessment',
    'BushfireVisualizer',
    'BenchmarkRunner',
    
    # Convenience functions
    'quick_simulation',
    'compare_python_vs_cpp',
    'plot_risk_surface',
    'animate_fire_spread',
    
    # Scenarios
    'create_blue_mountains_scenario',
    'create_extreme_weather_scenario',
    'AUSTRALIAN_FIRE_SEASONS',
    'EXTREME_CONDITIONS',
    
    # Version info
    '__version__',
]
