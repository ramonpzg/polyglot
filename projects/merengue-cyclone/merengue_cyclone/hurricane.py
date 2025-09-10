"""
Hurricane tracking and analysis module with Zig acceleration.
"""

import ctypes
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import numpy as np
from datetime import datetime, timedelta

# Load the compiled Zig library
_lib_path = Path(__file__).parent / "src" / "hurricane.so"
if not _lib_path.exists():
    # Fallback to pure Python implementation during development
    _lib = None
else:
    _lib = ctypes.CDLL(str(_lib_path))

    # Define function signatures
    _lib.haversine_distance.argtypes = [ctypes.c_double] * 4
    _lib.haversine_distance.restype = ctypes.c_double

    _lib.coriolis_parameter.argtypes = [ctypes.c_double]
    _lib.coriolis_parameter.restype = ctypes.c_double

    _lib.calculate_intensity.argtypes = [ctypes.c_double, ctypes.c_double]
    _lib.calculate_intensity.restype = ctypes.c_double

    _lib.estimate_storm_surge.argtypes = [ctypes.c_double] * 4
    _lib.estimate_storm_surge.restype = ctypes.c_double

    _lib.benchmark_haversine.argtypes = [ctypes.c_uint32]
    _lib.benchmark_haversine.restype = ctypes.c_double


@dataclass
class HurricanePoint:
    """Single point in a hurricane track."""
    lat: float
    lon: float
    pressure: float  # millibars
    wind_speed: float  # km/h
    timestamp: datetime
    category: Optional[int] = None

    def __post_init__(self):
        """Calculate Saffir-Simpson category."""
        if self.wind_speed < 119:
            self.category = 0  # Tropical Storm
        elif self.wind_speed < 154:
            self.category = 1
        elif self.wind_speed < 178:
            self.category = 2
        elif self.wind_speed < 208:
            self.category = 3
        elif self.wind_speed < 252:
            self.category = 4
        else:
            self.category = 5


class TrackAnalysis:
    """Analysis results for a hurricane track."""

    def __init__(self, points: List[HurricanePoint]):
        self.points = points
        self.distances = []
        self.speeds = []
        self.ace = 0.0
        self._analyze()

    def _analyze(self):
        """Analyze the track using Zig acceleration if available."""
        if len(self.points) < 2:
            return

        if _lib:
            # Use Zig for fast calculation
            self._analyze_zig()
        else:
            # Fallback to pure Python
            self._analyze_python()

    def _analyze_python(self):
        """Pure Python track analysis."""
        for i in range(len(self.points) - 1):
            p1, p2 = self.points[i], self.points[i + 1]
            dist = calculate_distance(p1.lat, p1.lon, p2.lat, p2.lon)
            self.distances.append(dist)

            time_diff = (p2.timestamp - p1.timestamp).total_seconds() / 3600
            speed = dist / time_diff if time_diff > 0 else 0
            self.speeds.append(speed)

        # Calculate ACE
        for point in self.points:
            wind_knots = point.wind_speed * 0.539957
            if wind_knots >= 35:
                self.ace += (wind_knots ** 2) / 10000

    def _analyze_zig(self):
        """Zig-accelerated track analysis."""
        # Prepare data for Zig
        n = len(self.points)
        distances = (ctypes.c_double * (n - 1))()
        speeds = (ctypes.c_double * (n - 1))()

        # Create C struct array
        class CHurricanePoint(ctypes.Structure):
            _fields_ = [
                ("lat", ctypes.c_double),
                ("lon", ctypes.c_double),
                ("pressure", ctypes.c_double),
                ("wind_speed", ctypes.c_double),
                ("timestamp", ctypes.c_int64),
            ]

        points_array = (CHurricanePoint * n)()
        for i, p in enumerate(self.points):
            points_array[i].lat = p.lat
            points_array[i].lon = p.lon
            points_array[i].pressure = p.pressure
            points_array[i].wind_speed = p.wind_speed
            points_array[i].timestamp = int(p.timestamp.timestamp())

        _lib.process_track_batch(points_array, n, distances, speeds)

        self.distances = list(distances)
        self.speeds = list(speeds)
        self.ace = _lib.calculate_ace(points_array, n)

    @property
    def max_intensity(self) -> HurricanePoint:
        """Get the point of maximum intensity."""
        return max(self.points, key=lambda p: p.wind_speed)

    @property
    def total_distance(self) -> float:
        """Total distance traveled."""
        return sum(self.distances)

    @property
    def average_speed(self) -> float:
        """Average forward speed."""
        return np.mean(self.speeds) if self.speeds else 0


class IntensityModel:
    """Hurricane intensity prediction model."""

    def __init__(self):
        self.sst_grid = self._load_sst_data()

    def _load_sst_data(self) -> Dict[Tuple[float, float], float]:
        """Load Caribbean sea surface temperature data."""
        # Simulated SST data for the Caribbean
        return {
            (18.5, -69.5): 28.5,  # Near Dominican Republic
            (18.0, -70.0): 28.2,
            (19.0, -69.0): 28.8,
            (17.5, -68.5): 29.0,
            (20.0, -70.5): 27.9,
        }

    def predict_intensity(self, lat: float, lon: float, pressure: float) -> float:
        """Predict hurricane intensity at given location."""
        # Find nearest SST value
        sst = self._get_sst(lat, lon)

        if _lib:
            return _lib.calculate_intensity(sst, pressure)
        else:
            # Pure Python fallback
            if sst < 26.5:
                return 0.0
            efficiency = (sst + 273.15 - 250) / (sst + 273.15)
            pressure_diff = 1013 - pressure
            max_wind = np.sqrt(efficiency * pressure_diff * 100) * 3.6
            return min(max_wind, 300)

    def _get_sst(self, lat: float, lon: float) -> float:
        """Get interpolated SST for location."""
        # Simple nearest neighbor for demo
        min_dist = float('inf')
        nearest_sst = 27.0  # Default Caribbean temperature

        for (grid_lat, grid_lon), sst in self.sst_grid.items():
            dist = ((lat - grid_lat) ** 2 + (lon - grid_lon) ** 2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                nearest_sst = sst

        return nearest_sst


class HurricaneTracker:
    """Main hurricane tracking and prediction system."""

    def __init__(self):
        self.tracks: Dict[str, List[HurricanePoint]] = {}
        self.intensity_model = IntensityModel()
        self.current_track = None

    def add_observation(self, name: str, point: HurricanePoint):
        """Add a new observation to a hurricane track."""
        if name not in self.tracks:
            self.tracks[name] = []
        self.tracks[name].append(point)
        self.current_track = name

    def analyze_track(self, name: str) -> TrackAnalysis:
        """Analyze a complete hurricane track."""
        if name not in self.tracks:
            raise ValueError(f"No track found for {name}")
        return TrackAnalysis(self.tracks[name])

    def predict_next_position(self, name: str, hours: int = 6) -> List[HurricanePoint]:
        """Predict future positions."""
        if name not in self.tracks or len(self.tracks[name]) < 2:
            return []

        predictions = []
        track = self.tracks[name]
        current = track[-1]
        prev = track[-2]

        for h in range(1, hours + 1):
            # Simple linear extrapolation for demo
            dlat = current.lat - prev.lat
            dlon = current.lon - prev.lon

            # Apply Caribbean steering current bias
            caribbean_drift = -0.2  # Westward drift
            coriolis_effect = 0.1 * current.lat / 20  # Poleward drift

            next_point = HurricanePoint(
                lat=current.lat + dlat + coriolis_effect,
                lon=current.lon + dlon + caribbean_drift,
                pressure=current.pressure,
                wind_speed=current.wind_speed,
                timestamp=current.timestamp + timedelta(hours=h)
            )

            # Update intensity based on SST
            next_point.wind_speed = self.intensity_model.predict_intensity(
                next_point.lat, next_point.lon, next_point.pressure
            )

            predictions.append(next_point)
            prev, current = current, next_point

        return predictions

    def estimate_dominican_impact(self, name: str) -> Dict[str, Any]:
        """Estimate potential impact on Dominican Republic."""
        if name not in self.tracks:
            return {"risk": "unknown"}

        track = self.tracks[name]
        predictions = self.predict_next_position(name, hours=48)
        all_points = track + predictions

        # Check proximity to DR
        dr_center = (18.7357, -70.1627)  # Geographic center
        min_distance = float('inf')
        closest_point = None

        for point in all_points:
            dist = calculate_distance(
                point.lat, point.lon, dr_center[0], dr_center[1]
            )
            if dist < min_distance:
                min_distance = dist
                closest_point = point

        # Calculate risk level
        if min_distance < 100:
            risk = "extreme"
        elif min_distance < 250:
            risk = "high"
        elif min_distance < 500:
            risk = "moderate"
        else:
            risk = "low"

        # Estimate storm surge for coastal areas
        surge = estimate_surge(
            closest_point.wind_speed,
            closest_point.pressure,
            20,  # Average coastal depth
            30   # Typical approach angle
        ) if closest_point else 0

        return {
            "risk": risk,
            "closest_approach_km": min_distance,
            "max_winds_kmh": closest_point.wind_speed if closest_point else 0,
            "estimated_surge_m": surge,
            "impact_time": closest_point.timestamp if closest_point else None,
            "category": closest_point.category if closest_point else 0,
        }

    def benchmark_performance(self, iterations: int = 10000) -> Dict[str, float]:
        """Benchmark Zig vs Python performance."""
        results = {}

        # Test data
        points = [
            HurricanePoint(18.5 + i * 0.1, -70 + i * 0.1, 980 - i, 150 + i * 5,
                          datetime.now() + timedelta(hours=i))
            for i in range(100)
        ]

        # Python benchmark
        start = time.perf_counter()
        for _ in range(iterations // 100):
            analysis = TrackAnalysis(points)
            _ = analysis.total_distance
        results['python_ms'] = (time.perf_counter() - start) * 1000

        # Zig benchmark
        if _lib:
            start = time.perf_counter()
            _lib.benchmark_haversine(iterations)
            results['zig_ms'] = (time.perf_counter() - start) * 1000
            results['speedup'] = results['python_ms'] / results['zig_ms']

        return results


# Utility functions
def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points."""
    if _lib:
        return _lib.haversine_distance(lat1, lon1, lat2, lon2)
    else:
        # Pure Python haversine
        R = 6371  # Earth radius in km
        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)
        a = (np.sin(dlat / 2) ** 2 +
             np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) *
             np.sin(dlon / 2) ** 2)
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        return R * c


def predict_track(current: HurricanePoint, previous: HurricanePoint,
                 hours: int = 6) -> List[HurricanePoint]:
    """Quick track prediction."""
    tracker = HurricaneTracker()
    tracker.add_observation("temp", previous)
    tracker.add_observation("temp", current)
    return tracker.predict_next_position("temp", hours)


def estimate_surge(wind_speed: float, pressure: float,
                  depth: float = 20, angle: float = 45) -> float:
    """Estimate storm surge height."""
    if _lib:
        return _lib.estimate_storm_surge(wind_speed, pressure, depth, angle)
    else:
        # Pure Python estimation
        wind_ms = wind_speed / 3.6
        pressure_deficit = 1013 - pressure
        cd = 0.0025
        wind_stress = cd * 1025 * wind_ms ** 2
        depth_factor = 50 / max(depth, 10)
        angle_factor = np.cos(np.radians(angle))
        surge = (pressure_deficit * 0.01 + wind_stress * 0.0001 * depth_factor) * angle_factor
        return max(0, min(surge, 10))
