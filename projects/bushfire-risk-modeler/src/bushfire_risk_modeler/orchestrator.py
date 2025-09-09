"""
Python Orchestration Layer
==========================

This module demonstrates Python's strengths:
- High-level coordination and workflow management
- Data analysis and interpretation  
- Integration with scientific Python ecosystem
- Flexible scenario creation and management

While C++ crunches the numbers, Python makes sense of them.
"""

import time
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path

from ._core import (
    BushfireSimulator, WeatherCondition, VegetationType, 
    FireDangerRating, fire_index, utility
)


@dataclass
class RiskAssessment:
    """
    Container for risk analysis results.
    
    Python's dataclasses make this clean and readable,
    while the heavy computation happened in C++.
    """
    scenario_name: str
    total_area_at_risk: float  # hectares
    probability_distribution: np.ndarray
    weather_conditions: List[WeatherCondition]
    ignition_sources: List[Tuple[int, int]]
    fire_danger_rating: FireDangerRating
    confidence_interval: Tuple[float, float]
    computation_time: float
    
    # Analysis metadata
    monte_carlo_runs: int = field(default=1000)
    grid_resolution: Tuple[int, int] = field(default=(100, 100))
    created_at: str = field(default_factory=lambda: time.strftime('%Y-%m-%d %H:%M:%S'))
    
    def to_summary_dict(self) -> Dict:
        """Convert to dictionary for easy reporting"""
        return {
            'Scenario': self.scenario_name,
            'Area at Risk (ha)': f"{self.total_area_at_risk:.1f}",
            'Danger Rating': self.fire_danger_rating.name,
            'Confidence Interval': f"{self.confidence_interval[0]:.1f}-{self.confidence_interval[1]:.1f} ha",
            'Monte Carlo Runs': self.monte_carlo_runs,
            'Computation Time': f"{self.computation_time:.2f}s",
            'Created': self.created_at,
        }
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert probability distribution to DataFrame for analysis"""
        return pd.DataFrame({
            'x': np.repeat(np.arange(self.grid_resolution[1]), self.grid_resolution[0]),
            'y': np.tile(np.arange(self.grid_resolution[0]), self.grid_resolution[1]),
            'risk_probability': self.probability_distribution.flatten(),
        })


class BushfireAnalyst:
    """
    High-level coordinator for bushfire risk analysis.
    
    This is where Python shines - orchestrating complex workflows,
    managing data, and providing a clean API for researchers.
    The actual simulation runs are delegated to C++.
    """
    
    def __init__(self, grid_size: Tuple[int, int] = (200, 200)):
        self.grid_size = grid_size
        self.scenarios: Dict[str, RiskAssessment] = {}
        
    def create_scenario(self, name: str, terrain_type: str = "blue_mountains") -> BushfireSimulator:
        """Create a new simulation scenario with realistic terrain"""
        sim = BushfireSimulator(*self.grid_size)
        
        # Load terrain data (C++ utility does the heavy lifting)
        elevations, fuel_loads, vegetation = utility.load_nsw_terrain_data(terrain_type)
        sim.initialize_terrain_from_data(elevations, fuel_loads, vegetation)
        
        return sim
        
    def assess_risk(
        self,
        scenario_name: str,
        weather_scenarios: List[WeatherCondition],
        potential_ignitions: List[Tuple[int, int]],
        monte_carlo_runs: int = 1000
    ) -> RiskAssessment:
        """
        Comprehensive risk assessment using Monte Carlo simulation.
        
        Python coordinates the analysis while C++ does the parallel computation.
        This is the perfect division of labor.
        """
        print(f"🔬 Running risk assessment for: {scenario_name}")
        print(f"   Weather scenarios: {len(weather_scenarios)}")
        print(f"   Ignition points: {len(potential_ignitions)}")
        print(f"   Monte Carlo runs: {monte_carlo_runs}")
        
        # Create fresh simulator for this assessment
        sim = self.create_scenario(scenario_name)
        
        start_time = time.perf_counter()
        
        # Convert ignition points to NumPy array for C++
        ignition_array = np.array(potential_ignitions, dtype=np.uintp)
        
        # Run the Monte Carlo analysis (this is where C++ parallel algorithms shine)
        risk_distribution = sim.monte_carlo_risk_analysis(
            weather_scenarios, ignition_array, monte_carlo_runs
        )
        
        computation_time = time.perf_counter() - start_time
        
        # Python takes over for analysis and interpretation
        total_risk_area = np.sum(risk_distribution > 0.1) * (30 * 30 / 10000)  # Convert to hectares
        
        # Calculate confidence intervals
        sorted_risks = np.sort(risk_distribution.flatten())
        lower_ci = np.percentile(sorted_risks[sorted_risks > 0], 25)
        upper_ci = np.percentile(sorted_risks[sorted_risks > 0], 75)
        
        # Determine fire danger rating from weather
        avg_fdi = np.mean([
            fire_index.mcarthur_forest_fire_danger_index(
                w.temperature, w.humidity, w.wind_speed, 10.0  # Assume moderate drought
            ) for w in weather_scenarios
        ])
        danger_rating = fire_index.fdi_to_rating(avg_fdi)
        
        # Create comprehensive assessment
        assessment = RiskAssessment(
            scenario_name=scenario_name,
            total_area_at_risk=total_risk_area,
            probability_distribution=risk_distribution,
            weather_conditions=weather_scenarios,
            ignition_sources=potential_ignitions,
            fire_danger_rating=danger_rating,
            confidence_interval=(lower_ci * total_risk_area, upper_ci * total_risk_area),
            computation_time=computation_time,
            monte_carlo_runs=monte_carlo_runs,
            grid_resolution=self.grid_size,
        )
        
        self.scenarios[scenario_name] = assessment
        
        print(f"✅ Assessment complete in {computation_time:.2f}s")
        print(f"   Total area at risk: {total_risk_area:.1f} hectares")
        print(f"   Fire danger rating: {danger_rating.name}")
        
        return assessment
    
    def compare_scenarios(self, scenario_names: List[str]) -> pd.DataFrame:
        """Compare multiple risk assessments"""
        comparisons = []
        for name in scenario_names:
            if name in self.scenarios:
                comparisons.append(self.scenarios[name].to_summary_dict())
        
        return pd.DataFrame(comparisons)
    
    def export_results(self, filepath: Union[str, Path], format: str = "xlsx"):
        """Export all scenarios to file"""
        filepath = Path(filepath)
        
        if format == "xlsx":
            with pd.ExcelWriter(filepath) as writer:
                # Summary sheet
                summary_data = [scenario.to_summary_dict() for scenario in self.scenarios.values()]
                pd.DataFrame(summary_data).to_excel(writer, sheet_name="Summary", index=False)
                
                # Individual scenario sheets
                for name, scenario in self.scenarios.items():
                    scenario.to_dataframe().to_excel(writer, sheet_name=name[:31], index=False)
        
        print(f"📊 Results exported to {filepath}")


def create_blue_mountains_scenario() -> Tuple[List[WeatherCondition], List[Tuple[int, int]]]:
    """
    Create a realistic Blue Mountains fire scenario.
    
    Based on historical fire conditions in the region.
    Python handles the scenario logic, C++ will run the simulation.
    """
    
    # Generate realistic Blue Mountains weather patterns
    weather_scenarios = []
    
    # Summer fire season conditions
    for temp in [35, 40, 45]:  # Celsius
        for humidity in [15, 25, 35]:  # %
            for wind in [20, 35, 50]:  # km/h
                weather_scenarios.append(WeatherCondition(
                    temperature=float(temp),
                    humidity=float(humidity),
                    wind_speed=float(wind),
                    wind_direction=np.random.uniform(0, 360),
                    rainfall=0.0,  # Dry conditions
                    fuel_moisture=max(5.0, humidity * 0.3)  # Correlated with humidity
                ))
    
    # Potential ignition sources (power lines, campsites, lightning)
    ignition_points = [
        (50, 100),   # Power line corridor
        (150, 75),   # Camping area
        (100, 50),   # Lightning strike zone
        (175, 125),  # Urban-wildland interface
        (25, 150),   # Remote lightning
    ]
    
    return weather_scenarios, ignition_points


def create_extreme_weather_scenario() -> Tuple[List[WeatherCondition], List[Tuple[int, int]]]:
    """
    Create an extreme weather scenario (Black Summer 2019-20 style).
    
    This tests the system under catastrophic conditions.
    """
    
    # Extreme conditions based on Black Summer
    extreme_weather = [
        WeatherCondition(
            temperature=47.0,    # Record-breaking heat
            humidity=8.0,        # Critically low
            wind_speed=80.0,     # Severe winds
            wind_direction=45.0,  # NE winds (dangerous in NSW)
            rainfall=0.0,
            fuel_moisture=3.0    # Bone dry
        ),
        WeatherCondition(
            temperature=45.0,
            humidity=12.0,
            wind_speed=65.0,
            wind_direction=225.0,  # SW change
            rainfall=0.0,
            fuel_moisture=4.0
        ),
        WeatherCondition(
            temperature=43.0,
            humidity=15.0,
            wind_speed=55.0,
            wind_direction=90.0,   # E winds
            rainfall=0.0,
            fuel_moisture=5.0
        )
    ]
    
    # Multiple ignition sources in extreme conditions
    ignition_points = [
        (30, 30),    # Multiple
        (60, 80),    # simultaneous
        (120, 40),   # ignitions
        (90, 110),   # create
        (140, 160),  # megafires
        (170, 70),
        (40, 180),
    ]
    
    return extreme_weather, ignition_points


# Quick analysis functions for interactive use
def quick_risk_assessment(scenario: str = "blue_mountains") -> RiskAssessment:
    """
    One-line risk assessment for rapid exploration.
    Perfect for Jupyter notebooks.
    """
    analyst = BushfireAnalyst(grid_size=(100, 100))
    
    if scenario == "blue_mountains":
        weather, ignitions = create_blue_mountains_scenario()
    elif scenario == "extreme":
        weather, ignitions = create_extreme_weather_scenario()
    else:
        # Default moderate scenario
        weather = [WeatherCondition(temperature=30, humidity=40, wind_speed=20)]
        ignitions = [(50, 50)]
    
    return analyst.assess_risk(
        scenario_name=scenario,
        weather_scenarios=weather,
        potential_ignitions=ignitions,
        monte_carlo_runs=500  # Faster for interactive use
    )


if __name__ == "__main__":
    # Demo the orchestration system
    print("🔥 Bushfire Risk Analysis System")
    print("Python orchestrates, C++ computes")
    print("=" * 50)
    
    # Quick demo
    assessment = quick_risk_assessment("blue_mountains")
    print(f"\nRisk assessment complete!")
    print(f"Area at risk: {assessment.total_area_at_risk:.1f} hectares")
    print(f"Danger rating: {assessment.fire_danger_rating.name}")
    print(f"Computation time: {assessment.computation_time:.2f} seconds")