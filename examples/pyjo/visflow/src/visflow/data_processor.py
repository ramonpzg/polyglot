"""
VisFlow Data Processor

Core data processing engine that handles pandas operations, Python code execution,
and data transformation for 3D visualizations.
"""

import asyncio
import io
import json
import sys
import traceback
import uuid
from contextlib import redirect_stdout, redirect_stderr
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


class SafeExecutionEnvironment:
    """Restricted environment for safe Python code execution."""
    
    def __init__(self):
        self.allowed_modules = {
            'pandas': pd,
            'numpy': np,
            'math': __import__('math'),
            'json': json,
            'datetime': __import__('datetime'),
        }
        
        self.allowed_builtins = {
            'len', 'range', 'enumerate', 'zip', 'sorted', 'reversed',
            'min', 'max', 'sum', 'abs', 'round', 'int', 'float', 'str',
            'list', 'dict', 'tuple', 'set', 'bool', 'type', 'isinstance',
            'hasattr', 'getattr', 'print'
        }
    
    def get_globals(self, datasets: Dict[str, pd.DataFrame], extra_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a restricted global environment."""
        restricted_globals = {
            '__builtins__': {name: __builtins__[name] for name in self.allowed_builtins if name in __builtins__}
        }
        
        # Add allowed modules
        restricted_globals.update(self.allowed_modules)
        
        # Add datasets
        restricted_globals.update(datasets)
        
        # Add extra context
        restricted_globals.update(extra_context)
        
        # Add utility functions
        restricted_globals.update({
            'stream_to_threejs': self._stream_to_threejs,
            'create_particle_system': self._create_particle_system,
            'create_mesh_visualization': self._create_mesh_visualization,
            'create_line_visualization': self._create_line_visualization,
        })
        
        return restricted_globals
    
    def _stream_to_threejs(self, coordinates, values, **kwargs):
        """Utility function to format data for Three.js visualization."""
        return {
            'type': 'particle_system',
            'coordinates': coordinates.tolist() if hasattr(coordinates, 'tolist') else coordinates,
            'values': values.tolist() if hasattr(values, 'tolist') else values,
            'options': kwargs
        }
    
    def _create_particle_system(self, positions, colors=None, sizes=None, **kwargs):
        """Create particle system data for Three.js."""
        data = {
            'type': 'particles',
            'positions': positions.tolist() if hasattr(positions, 'tolist') else positions,
        }
        
        if colors is not None:
            data['colors'] = colors.tolist() if hasattr(colors, 'tolist') else colors
        
        if sizes is not None:
            data['sizes'] = sizes.tolist() if hasattr(sizes, 'tolist') else sizes
        
        data.update(kwargs)
        return data
    
    def _create_mesh_visualization(self, vertices, faces=None, colors=None, **kwargs):
        """Create mesh visualization data for Three.js."""
        data = {
            'type': 'mesh',
            'vertices': vertices.tolist() if hasattr(vertices, 'tolist') else vertices,
        }
        
        if faces is not None:
            data['faces'] = faces.tolist() if hasattr(faces, 'tolist') else faces
        
        if colors is not None:
            data['colors'] = colors.tolist() if hasattr(colors, 'tolist') else colors
        
        data.update(kwargs)
        return data
    
    def _create_line_visualization(self, points, colors=None, **kwargs):
        """Create line visualization data for Three.js."""
        data = {
            'type': 'lines',
            'points': points.tolist() if hasattr(points, 'tolist') else points,
        }
        
        if colors is not None:
            data['colors'] = colors.tolist() if hasattr(colors, 'tolist') else colors
        
        data.update(kwargs)
        return data


class DataProcessor:
    """Main data processing engine for VisFlow."""
    
    def __init__(self):
        self.datasets: Dict[str, pd.DataFrame] = {}
        self.dataset_metadata: Dict[str, Dict[str, Any]] = {}
        self.execution_env = SafeExecutionEnvironment()
        self.visualization_results = []
    
    def store_dataset(self, df: pd.DataFrame, name: str) -> str:
        """Store a dataset and return its ID."""
        dataset_id = str(uuid.uuid4())
        self.datasets[dataset_id] = df.copy()
        self.dataset_metadata[dataset_id] = {
            'name': name,
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'created_at': pd.Timestamp.now().isoformat()
        }
        return dataset_id
    
    def get_dataset(self, dataset_id: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """Get dataset by ID with optional row limit."""
        if dataset_id not in self.datasets:
            raise KeyError(f"Dataset {dataset_id} not found")
        
        df = self.datasets[dataset_id]
        if limit:
            df = df.head(limit)
        
        return {
            'data': df.to_dict('records'),
            'columns': list(df.columns),
            'shape': df.shape,
            'metadata': self.dataset_metadata[dataset_id]
        }
    
    def get_dataset_info(self, dataset_id: str) -> Dict[str, Any]:
        """Get basic information about a dataset."""
        if dataset_id not in self.datasets:
            raise KeyError(f"Dataset {dataset_id} not found")
        
        df = self.datasets[dataset_id]
        info = self.dataset_metadata[dataset_id].copy()
        
        # Add statistical information
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            info['statistics'] = {
                col: {
                    'mean': float(df[col].mean()) if not df[col].isna().all() else None,
                    'std': float(df[col].std()) if not df[col].isna().all() else None,
                    'min': float(df[col].min()) if not df[col].isna().all() else None,
                    'max': float(df[col].max()) if not df[col].isna().all() else None,
                    'null_count': int(df[col].isna().sum())
                }
                for col in numeric_cols[:10]  # Limit to first 10 numeric columns
            }
        
        return info
    
    def list_datasets(self) -> List[Dict[str, Any]]:
        """List all stored datasets."""
        return [
            {
                'id': dataset_id,
                'metadata': metadata
            }
            for dataset_id, metadata in self.dataset_metadata.items()
        ]
    
    def delete_dataset(self, dataset_id: str):
        """Delete a dataset."""
        if dataset_id not in self.datasets:
            raise KeyError(f"Dataset {dataset_id} not found")
        
        del self.datasets[dataset_id]
        del self.dataset_metadata[dataset_id]
    
    async def execute_code(self, code: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute Python code in a safe environment."""
        if context is None:
            context = {}
        
        # Prepare execution environment
        globals_dict = self.execution_env.get_globals(self.datasets, context)
        locals_dict = {}
        
        # Capture output
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        # Clear previous visualization results
        self.visualization_results.clear()
        
        result = {
            'success': True,
            'output': '',
            'error': None,
            'visualization_data': None,
            'returned_data': None
        }
        
        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # Execute the code
                exec_result = exec(code, globals_dict, locals_dict)
                
                # Capture any visualization data created during execution
                visualization_data = self._extract_visualization_data(locals_dict)
                
                result.update({
                    'output': stdout_capture.getvalue(),
                    'visualization_data': visualization_data,
                    'returned_data': self._extract_data_for_frontend(locals_dict)
                })
        
        except Exception as e:
            result.update({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc(),
                'output': stdout_capture.getvalue(),
                'stderr': stderr_capture.getvalue()
            })
        
        return result
    
    def _extract_visualization_data(self, locals_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract visualization data from execution locals."""
        viz_data = []
        
        # Look for common visualization variable names
        viz_keys = ['viz_data', 'visualization', 'vis_data', 'plot_data', 'three_js_data']
        
        for key in viz_keys:
            if key in locals_dict:
                data = locals_dict[key]
                if isinstance(data, dict) and 'type' in data:
                    viz_data.append(data)
        
        # Also check for data formatted by utility functions
        for key, value in locals_dict.items():
            if isinstance(value, dict) and value.get('type') in ['particles', 'mesh', 'lines', 'particle_system']:
                viz_data.append(value)
        
        return viz_data if viz_data else None
    
    def _extract_data_for_frontend(self, locals_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract general data that might be useful for the frontend."""
        extracted = {}
        
        for key, value in locals_dict.items():
            # Skip private variables and functions
            if key.startswith('_'):
                continue
            
            # Extract pandas DataFrames
            if isinstance(value, pd.DataFrame):
                # Limit size for performance
                df_sample = value.head(1000) if len(value) > 1000 else value
                extracted[key] = {
                    'type': 'dataframe',
                    'data': df_sample.to_dict('records'),
                    'columns': list(value.columns),
                    'shape': value.shape
                }
            
            # Extract numpy arrays
            elif isinstance(value, np.ndarray):
                # Limit size for performance
                if value.size > 10000:
                    array_sample = value.flatten()[:10000]
                else:
                    array_sample = value
                
                extracted[key] = {
                    'type': 'array',
                    'data': array_sample.tolist(),
                    'shape': value.shape,
                    'dtype': str(value.dtype)
                }
            
            # Extract basic Python types
            elif isinstance(value, (int, float, str, bool, list, dict)):
                # Avoid very large data structures
                if isinstance(value, (list, dict)):
                    if len(str(value)) > 50000:  # Skip very large objects
                        continue
                
                extracted[key] = {
                    'type': 'basic',
                    'data': value
                }
        
        return extracted if extracted else None


# Utility functions for common data processing tasks
def calculate_fire_risk(temperature: pd.Series, humidity: pd.Series, wind_speed: pd.Series) -> pd.Series:
    """Calculate fire risk based on weather conditions."""
    return (temperature * wind_speed) / (humidity + 10)


def generate_particle_positions(coords: pd.DataFrame, z_column: str = None) -> np.ndarray:
    """Generate 3D positions for particle visualization."""
    if z_column and z_column in coords.columns:
        return coords[['x', 'y', z_column]].values
    elif len(coords.columns) >= 2:
        # Use first two columns as x,y and add zero for z
        positions = np.zeros((len(coords), 3))
        positions[:, 0] = coords.iloc[:, 0]
        positions[:, 1] = coords.iloc[:, 1]
        return positions
    else:
        raise ValueError("Need at least 2 coordinate columns")


def create_heatmap_colors(values: pd.Series, colormap: str = 'viridis') -> np.ndarray:
    """Create color values for heatmap visualization."""
    # Normalize values to 0-1 range
    normalized = (values - values.min()) / (values.max() - values.min())
    
    # Simple color mapping (red to blue)
    if colormap == 'fire':
        colors = np.zeros((len(values), 3))
        colors[:, 0] = 1.0  # Red component
        colors[:, 1] = 1.0 - normalized  # Green component (inverse)
        colors[:, 2] = 1.0 - normalized  # Blue component (inverse)
    else:  # Default viridis-like
        colors = np.zeros((len(values), 3))
        colors[:, 0] = normalized * 0.267  # Purple to yellow
        colors[:, 1] = normalized * 0.967
        colors[:, 2] = 0.329 + normalized * 0.527
    
    return colors