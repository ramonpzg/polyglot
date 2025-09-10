"""
Merengue Cyclone - High-performance hurricane tracking and analysis
=====================================================================

A Python package for hurricane track analysis and prediction, accelerated
with Zig for critical performance paths. Designed for Caribbean hurricane
monitoring with a focus on Dominican Republic weather patterns.
"""

__version__ = "0.1.0"

# Dominican Republic hurricane season peaks
HURRICANE_SEASON_PEAKS = {
    "early": (6, 1),   # June 1
    "peak": (9, 10),   # September 10
    "late": (11, 30),  # November 30
}

# Major Dominican Republic monitoring stations
DR_STATIONS = {
    "santo_domingo": {"lat": 18.4861, "lon": -69.9312, "name": "Santo Domingo"},
    "punta_cana": {"lat": 18.5601, "lon": -68.3725, "name": "Punta Cana"},
    "puerto_plata": {"lat": 19.7808, "lon": -70.6871, "name": "Puerto Plata"},
    "santiago": {"lat": 19.4517, "lon": -70.6970, "name": "Santiago"},
    "samana": {"lat": 19.2056, "lon": -69.3361, "name": "Samaná"},
}

# Core imports that don't require additional dependencies
from .hurricane import (
    HurricaneTracker,
    HurricanePoint,
    TrackAnalysis,
    IntensityModel,
    calculate_distance,
    predict_track,
    estimate_surge,
)

__all__ = [
    # Main classes
    "HurricaneTracker",
    "HurricanePoint",
    "TrackAnalysis",
    "IntensityModel",

    # Core functions
    "calculate_distance",
    "predict_track",
    "estimate_surge",

    # Constants
    "HURRICANE_SEASON_PEAKS",
    "DR_STATIONS",

    # Version
    "__version__",
]

# Optional imports for CLI and server (require additional dependencies)
try:
    from .cli import main as cli_main
    __all__.append("cli_main")
except ImportError:
    cli_main = None

try:
    from .server import app, start_server
    __all__.extend(["app", "start_server"])
except ImportError:
    app = None
    start_server = None
