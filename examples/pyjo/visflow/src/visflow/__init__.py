"""
VisFlow - 3D Interactive Data Visualization Studio

A desktop-style web application that combines Python's data processing power 
with Three.js 3D visualization capabilities.
"""

__version__ = "0.1.0"
__author__ = "VisFlow Team"
__email__ = "team@visflow.dev"

from .server import app
from .data_processor import DataProcessor

__all__ = ["app", "DataProcessor", "__version__"]