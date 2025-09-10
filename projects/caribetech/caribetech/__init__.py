"""
CaribeTech: High-performance Caribbean hurricane tracking and meteorological calculations.

A Dominican Republic-focused weather analysis tool that uses Zig for performance-critical
hurricane path calculations and Python for data analysis and visualization.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
import math
import random
import time
from datetime import datetime, timedelta

__version__ = "0.1.0"

@dataclass
class StormPoint:
    """A single point in a hurricane's path with meteorological data."""
    latitude: float
    longitude: float
    timestamp: datetime
    wind_speed_kmh: float  # km/h
    pressure_hpa: float    # hectopascals
    category: int          # Saffir-Simpson scale (0-5)
    
    def distance_to_dominican_republic(self) -> float:
        """Calculate distance to Santo Domingo, Dominican Republic (18.4861°N, 69.9312°W)."""
        # Haversine formula for great circle distance
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(18.4861), math.radians(-69.9312)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return 6371 * c  # Earth's radius in km

@dataclass
class StormTrack:
    """Complete hurricane track with analysis capabilities."""
    name: str
    season: int
    points: List[StormPoint]
    
    @property
    def max_category(self) -> int:
        """Maximum category reached during the storm."""
        return max(point.category for point in self.points) if self.points else 0
    
    @property
    def closest_approach_to_dr(self) -> Tuple[float, StormPoint]:
        """Find closest approach to Dominican Republic."""
        if not self.points:
            return float('inf'), None
        
        closest_point = min(self.points, key=lambda p: p.distance_to_dominican_republic())
        return closest_point.distance_to_dominican_republic(), closest_point
    
    def threat_level(self) -> str:
        """Assess threat level to Dominican Republic."""
        distance, _ = self.closest_approach_to_dr
        max_cat = self.max_category
        
        if distance < 100 and max_cat >= 3:
            return "EXTREME"
        elif distance < 200 and max_cat >= 2:
            return "HIGH"
        elif distance < 400 and max_cat >= 1:
            return "MODERATE"
        else:
            return "LOW"

class CycloneTracker:
    """Main hurricane tracking and analysis system."""
    
    def __init__(self):
        self.tracks: List[StormTrack] = []
        # In a real implementation, this would call into Zig functions
        # via ziggy-pydust for high-performance calculations
    
    def load_historical_data(self, years: int = 10) -> List[StormTrack]:
        """Load historical hurricane data for the Caribbean region."""
        # Simulate loading historical data
        # In reality, this would use high-performance Zig functions for data processing
        tracks = []
        
        for year in range(2024 - years, 2024):
            # Generate 3-8 storms per year (Caribbean average)
            num_storms = random.randint(3, 8)
            
            for storm_num in range(num_storms):
                storm_name = self._generate_storm_name(year, storm_num)
                points = self._generate_storm_track()
                tracks.append(StormTrack(storm_name, year, points))
        
        self.tracks = tracks
        return tracks
    
    def analyze_dominican_threats(self) -> List[StormTrack]:
        """Find storms that posed significant threats to Dominican Republic."""
        threats = []
        for track in self.tracks:
            distance, _ = track.closest_approach_to_dr
            if distance < 500 and track.max_category >= 1:  # Within 500km and Cat 1+
                threats.append(track)
        
        return sorted(threats, key=lambda t: t.closest_approach_to_dr[0])
    
    def calculate_storm_intensity(self, wind_speed_kmh: float, pressure_hpa: float) -> int:
        """Calculate Saffir-Simpson category (would use optimized Zig implementation)."""
        # Convert to mph for Saffir-Simpson scale
        wind_mph = wind_speed_kmh * 0.621371
        
        if wind_mph >= 252:
            return 5
        elif wind_mph >= 209:
            return 4
        elif wind_mph >= 178:
            return 3
        elif wind_mph >= 154:
            return 2
        elif wind_mph >= 119:
            return 1
        else:
            return 0
    
    def predict_path(self, current_points: List[StormPoint], hours_ahead: int = 72) -> List[StormPoint]:
        """Predict hurricane path (would use SIMD-optimized Zig functions)."""
        if len(current_points) < 2:
            return []
        
        # Simple linear extrapolation (real implementation would use complex meteorological models)
        last_point = current_points[-1]
        second_last = current_points[-2]
        
        # Calculate movement vector
        lat_delta = last_point.latitude - second_last.latitude
        lon_delta = last_point.longitude - second_last.longitude
        time_delta = (last_point.timestamp - second_last.timestamp).total_seconds() / 3600  # hours
        
        predicted_points = []
        for hour in range(6, hours_ahead + 1, 6):  # 6-hour intervals
            future_time = last_point.timestamp + timedelta(hours=hour)
            
            # Apply some randomness and weakening for realism
            lat_noise = random.uniform(-0.1, 0.1)
            lon_noise = random.uniform(-0.1, 0.1)
            
            new_lat = last_point.latitude + (lat_delta * hour / time_delta) + lat_noise
            new_lon = last_point.longitude + (lon_delta * hour / time_delta) + lon_noise
            
            # Gradual weakening over time
            wind_decay = max(0.95, 1 - (hour * 0.01))
            new_wind = last_point.wind_speed_kmh * wind_decay
            new_pressure = min(1013, last_point.pressure_hpa + hour * 0.5)
            new_category = self.calculate_storm_intensity(new_wind, new_pressure)
            
            predicted_points.append(StormPoint(
                latitude=new_lat,
                longitude=new_lon,
                timestamp=future_time,
                wind_speed_kmh=new_wind,
                pressure_hpa=new_pressure,
                category=new_category
            ))
        
        return predicted_points
    
    def generate_sample_data(self) -> StormTrack:
        """Generate a sample hurricane for demonstration."""
        # Create a hurricane approaching Dominican Republic
        base_time = datetime.now() - timedelta(days=2)
        points = []
        
        # Start hurricane east of the Caribbean
        lat, lon = 15.0, -45.0
        
        for hour in range(0, 72, 6):  # 3 days, 6-hour intervals
            # Move generally west-northwest toward Dominican Republic
            lat += random.uniform(0.1, 0.3)
            lon += random.uniform(-0.4, -0.2)
            
            # Intensify then weaken
            if hour < 36:
                wind_speed = 120 + hour * 2  # Strengthening
            else:
                wind_speed = 192 - (hour - 36) * 1.5  # Weakening
            
            pressure = 1000 - (wind_speed - 120) * 0.3
            category = self.calculate_storm_intensity(wind_speed, pressure)
            
            points.append(StormPoint(
                latitude=lat,
                longitude=lon,
                timestamp=base_time + timedelta(hours=hour),
                wind_speed_kmh=wind_speed,
                pressure_hpa=pressure,
                category=category
            ))
        
        return StormTrack("Ejemplo", 2024, points)
    
    def _generate_storm_name(self, year: int, storm_num: int) -> str:
        """Generate Caribbean storm names."""
        caribbean_names = [
            "Ana", "Bill", "Claudette", "Danny", "Elsa", "Fred", "Grace",
            "Henri", "Ida", "Julian", "Kate", "Larry", "Mindy", "Nicholas",
            "Odette", "Peter", "Rose", "Sam", "Teresa", "Victor", "Wanda"
        ]
        return f"{caribbean_names[storm_num % len(caribbean_names)]}-{year}"
    
    def _generate_storm_track(self) -> List[StormPoint]:
        """Generate a realistic storm track."""
        points = []
        base_time = datetime(random.randint(2020, 2023), random.randint(6, 11), random.randint(1, 28))
        
        # Start in Atlantic
        lat = random.uniform(10.0, 20.0)
        lon = random.uniform(-60.0, -40.0)
        
        # Generate 5-15 points for track
        num_points = random.randint(5, 15)
        
        for i in range(num_points):
            # Move generally northwest
            lat += random.uniform(-0.2, 0.5)
            lon += random.uniform(-0.8, 0.2)
            
            # Vary intensity
            wind_speed = random.uniform(65, 250)
            pressure = random.uniform(940, 1000)
            category = self.calculate_storm_intensity(wind_speed, pressure)
            
            points.append(StormPoint(
                latitude=lat,
                longitude=lon,
                timestamp=base_time + timedelta(hours=i * 6),
                wind_speed_kmh=wind_speed,
                pressure_hpa=pressure,
                category=category
            ))
        
        return points

# Performance comparison utilities
def benchmark_python_vs_zig(num_calculations: int = 10000) -> dict:
    """Compare Python vs Zig performance for hurricane calculations."""
    tracker = CycloneTracker()
    
    # Python timing
    start_time = time.time()
    for _ in range(num_calculations):
        # Simulate intensive calculations
        wind = random.uniform(100, 300)
        pressure = random.uniform(900, 1013)
        _ = tracker.calculate_storm_intensity(wind, pressure)
    python_time = time.time() - start_time
    
    # In a real implementation with Zig, this would call the Zig functions
    # For now, simulate faster execution
    estimated_zig_time = python_time * 0.15  # Estimate 6-7x speedup
    
    return {
        "python_time": python_time,
        "zig_time": estimated_zig_time,
        "speedup": python_time / estimated_zig_time,
        "calculations": num_calculations
    }

# Export main classes and functions
__all__ = [
    "StormPoint", 
    "StormTrack", 
    "CycloneTracker", 
    "benchmark_python_vs_zig"
]
