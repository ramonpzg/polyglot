#!/usr/bin/env python3
"""
Test Suite for VisFlow Data Processing

Comprehensive tests for the data processing module including:
- Dataset storage and retrieval
- Safe code execution
- Visualization data generation
- Utility functions
- Error handling
"""

import pytest
import pandas as pd
import numpy as np
import json
import tempfile
from pathlib import Path
import sys
import os

# Add the src directory to the path so we can import visflow
test_dir = Path(__file__).parent
project_root = test_dir.parent
sys.path.insert(0, str(project_root / "src"))

from visflow.data_processor import DataProcessor, SafeExecutionEnvironment
from visflow.data_processor import calculate_fire_risk, generate_particle_positions, create_heatmap_colors


class TestDataProcessor:
    """Test the main DataProcessor class."""
    
    @pytest.fixture
    def processor(self):
        """Create a fresh DataProcessor instance for each test."""
        return DataProcessor()
    
    @pytest.fixture
    def sample_data(self):
        """Create sample DataFrame for testing."""
        return pd.DataFrame({
            'x': np.random.randn(100),
            'y': np.random.randn(100),
            'z': np.random.randn(100),
            'value': np.random.uniform(0, 100, 100),
            'category': np.random.choice(['A', 'B', 'C'], 100)
        })
    
    def test_store_dataset(self, processor, sample_data):
        """Test dataset storage functionality."""
        # Store a dataset
        dataset_id = processor.store_dataset(sample_data, "test_data.csv")
        
        # Check that dataset was stored
        assert dataset_id in processor.datasets
        assert dataset_id in processor.dataset_metadata
        
        # Check metadata
        metadata = processor.dataset_metadata[dataset_id]
        assert metadata['name'] == "test_data.csv"
        assert metadata['shape'] == sample_data.shape
        assert set(metadata['columns']) == set(sample_data.columns)
        
        # Check that stored data is a copy, not reference
        original_value = sample_data.iloc[0, 0]
        sample_data.iloc[0, 0] = 999999
        stored_value = processor.datasets[dataset_id].iloc[0, 0]
        assert stored_value == original_value
    
    def test_get_dataset(self, processor, sample_data):
        """Test dataset retrieval functionality."""
        # Store and retrieve dataset
        dataset_id = processor.store_dataset(sample_data, "test_data.csv")
        retrieved = processor.get_dataset(dataset_id)
        
        # Check structure
        assert 'data' in retrieved
        assert 'columns' in retrieved
        assert 'shape' in retrieved
        assert 'metadata' in retrieved
        
        # Check data integrity
        assert len(retrieved['data']) == len(sample_data)
        assert set(retrieved['columns']) == set(sample_data.columns)
        
        # Test with limit
        limited = processor.get_dataset(dataset_id, limit=50)
        assert len(limited['data']) == 50
    
    def test_get_dataset_info(self, processor, sample_data):
        """Test dataset info generation."""
        dataset_id = processor.store_dataset(sample_data, "test_data.csv")
        info = processor.get_dataset_info(dataset_id)
        
        # Check basic info
        assert info['name'] == "test_data.csv"
        assert info['shape'] == sample_data.shape
        
        # Check statistics for numeric columns
        assert 'statistics' in info
        numeric_cols = sample_data.select_dtypes(include=[np.number]).columns
        for col in numeric_cols[:10]:  # Only first 10 are included
            assert col in info['statistics']
            stats = info['statistics'][col]
            assert 'mean' in stats
            assert 'std' in stats
            assert 'min' in stats
            assert 'max' in stats
            assert 'null_count' in stats
    
    def test_list_datasets(self, processor, sample_data):
        """Test dataset listing functionality."""
        # Initially empty
        assert processor.list_datasets() == []
        
        # Add some datasets
        id1 = processor.store_dataset(sample_data, "data1.csv")
        id2 = processor.store_dataset(sample_data.head(50), "data2.csv")
        
        datasets = processor.list_datasets()
        assert len(datasets) == 2
        
        # Check that both datasets are listed
        dataset_ids = [d['id'] for d in datasets]
        assert id1 in dataset_ids
        assert id2 in dataset_ids
    
    def test_delete_dataset(self, processor, sample_data):
        """Test dataset deletion."""
        # Store and delete dataset
        dataset_id = processor.store_dataset(sample_data, "test_data.csv")
        assert len(processor.list_datasets()) == 1
        
        processor.delete_dataset(dataset_id)
        assert len(processor.list_datasets()) == 0
        assert dataset_id not in processor.datasets
        assert dataset_id not in processor.dataset_metadata
        
        # Test deleting non-existent dataset
        with pytest.raises(KeyError):
            processor.delete_dataset("non_existent_id")
    
    @pytest.mark.asyncio
    async def test_execute_code_success(self, processor, sample_data):
        """Test successful code execution."""
        # Store dataset first
        dataset_id = processor.store_dataset(sample_data, "test_data.csv")
        
        code = """
import numpy as np
result = np.mean([1, 2, 3, 4, 5])
print(f"Mean is: {result}")
"""
        
        result = await processor.execute_code(code)
        
        assert result['success'] is True
        assert result['error'] is None
        assert "Mean is: 3.0" in result['output']
    
    @pytest.mark.asyncio
    async def test_execute_code_error(self, processor):
        """Test code execution with errors."""
        code = """
# This will cause an error
result = undefined_variable + 5
"""
        
        result = await processor.execute_code(code)
        
        assert result['success'] is False
        assert result['error'] is not None
        assert "NameError" in result['error'] or "undefined_variable" in result['error']
    
    @pytest.mark.asyncio
    async def test_execute_code_with_visualization(self, processor, sample_data):
        """Test code execution that creates visualization data."""
        dataset_id = processor.store_dataset(sample_data, "test_data.csv")
        
        code = f"""
import numpy as np

# Create visualization data
positions = np.random.randn(100, 3).tolist()
colors = np.random.rand(100, 3).tolist()

viz_data = {{
    'type': 'particles',
    'positions': positions,
    'colors': colors
}}
"""
        
        result = await processor.execute_code(code)
        
        assert result['success'] is True
        assert result['visualization_data'] is not None
        assert len(result['visualization_data']) > 0
        
        viz = result['visualization_data'][0]
        assert viz['type'] == 'particles'
        assert 'positions' in viz
        assert 'colors' in viz


class TestSafeExecutionEnvironment:
    """Test the safe execution environment."""
    
    @pytest.fixture
    def env(self):
        """Create a SafeExecutionEnvironment instance."""
        return SafeExecutionEnvironment()
    
    def test_allowed_modules(self, env):
        """Test that allowed modules are available."""
        globals_dict = env.get_globals({}, {})
        
        # Check that allowed modules are present
        assert 'pandas' in globals_dict
        assert 'numpy' in globals_dict
        assert 'math' in globals_dict
        assert 'json' in globals_dict
        assert 'datetime' in globals_dict
    
    def test_restricted_builtins(self, env):
        """Test that only safe builtins are available."""
        globals_dict = env.get_globals({}, {})
        builtins = globals_dict['__builtins__']
        
        # Check that safe functions are present
        safe_functions = ['len', 'range', 'print', 'int', 'float', 'str']
        for func in safe_functions:
            assert func in builtins
        
        # Check that dangerous functions are not present
        dangerous_functions = ['eval', 'exec', 'compile', '__import__', 'open', 'input']
        for func in dangerous_functions:
            assert func not in builtins
    
    def test_utility_functions(self, env):
        """Test that utility functions are available."""
        globals_dict = env.get_globals({}, {})
        
        utility_functions = [
            'stream_to_threejs',
            'create_particle_system',
            'create_mesh_visualization',
            'create_line_visualization'
        ]
        
        for func in utility_functions:
            assert func in globals_dict
            assert callable(globals_dict[func])
    
    def test_stream_to_threejs(self, env):
        """Test the stream_to_threejs utility function."""
        coordinates = [[1, 2, 3], [4, 5, 6]]
        values = [10, 20]
        
        result = env._stream_to_threejs(coordinates, values, color='red', size=5)
        
        assert result['type'] == 'particle_system'
        assert result['coordinates'] == coordinates
        assert result['values'] == values
        assert result['options']['color'] == 'red'
        assert result['options']['size'] == 5
    
    def test_create_particle_system(self, env):
        """Test the create_particle_system utility function."""
        positions = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        colors = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        sizes = [1, 2, 3]
        
        result = env._create_particle_system(positions, colors, sizes, material='points')
        
        assert result['type'] == 'particles'
        assert result['positions'] == positions
        assert result['colors'] == colors
        assert result['sizes'] == sizes
        assert result['material'] == 'points'
    
    def test_create_mesh_visualization(self, env):
        """Test the create_mesh_visualization utility function."""
        vertices = [[0, 0, 0], [1, 0, 0], [0, 1, 0]]
        faces = [[0, 1, 2]]
        
        result = env._create_mesh_visualization(vertices, faces, wireframe=True)
        
        assert result['type'] == 'mesh'
        assert result['vertices'] == vertices
        assert result['faces'] == faces
        assert result['wireframe'] is True
    
    def test_create_line_visualization(self, env):
        """Test the create_line_visualization utility function."""
        points = [[0, 0, 0], [1, 1, 1], [2, 2, 2]]
        
        result = env._create_line_visualization(points, linewidth=2)
        
        assert result['type'] == 'lines'
        assert result['points'] == points
        assert result['linewidth'] == 2


class TestUtilityFunctions:
    """Test standalone utility functions."""
    
    def test_calculate_fire_risk(self):
        """Test fire risk calculation function."""
        temp = pd.Series([30, 40, 50])
        humidity = pd.Series([60, 40, 20])
        wind_speed = pd.Series([10, 15, 25])
        
        risk = calculate_fire_risk(temp, humidity, wind_speed)
        
        # Check that risk increases with temperature and wind speed
        # and decreases with humidity
        assert len(risk) == 3
        assert risk.iloc[2] > risk.iloc[1] > risk.iloc[0]  # Should increase
        assert all(risk > 0)  # Should be positive
    
    def test_generate_particle_positions(self):
        """Test particle position generation."""
        # Test with 3D data
        coords_3d = pd.DataFrame({
            'x': [1, 2, 3],
            'y': [4, 5, 6],
            'z': [7, 8, 9]
        })
        
        positions = generate_particle_positions(coords_3d, 'z')
        assert positions.shape == (3, 3)
        np.testing.assert_array_equal(positions[:, 0], [1, 2, 3])
        np.testing.assert_array_equal(positions[:, 1], [4, 5, 6])
        np.testing.assert_array_equal(positions[:, 2], [7, 8, 9])
        
        # Test with 2D data (should add zero z-coordinate)
        coords_2d = pd.DataFrame({
            'x': [1, 2, 3],
            'y': [4, 5, 6]
        })
        
        positions = generate_particle_positions(coords_2d)
        assert positions.shape == (3, 3)
        np.testing.assert_array_equal(positions[:, 2], [0, 0, 0])
        
        # Test with insufficient columns
        coords_1d = pd.DataFrame({'x': [1, 2, 3]})
        with pytest.raises(ValueError):
            generate_particle_positions(coords_1d)
    
    def test_create_heatmap_colors(self):
        """Test heatmap color creation."""
        values = pd.Series([0, 50, 100])
        
        # Test fire colormap
        colors_fire = create_heatmap_colors(values, 'fire')
        assert colors_fire.shape == (3, 3)
        assert np.all(colors_fire >= 0) and np.all(colors_fire <= 1)
        
        # Test default colormap
        colors_default = create_heatmap_colors(values)
        assert colors_default.shape == (3, 3)
        assert np.all(colors_default >= 0) and np.all(colors_default <= 1)
        
        # Check that colors change with values
        assert not np.array_equal(colors_fire[0], colors_fire[2])


class TestIntegration:
    """Integration tests combining multiple components."""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test a complete workflow from data loading to visualization."""
        processor = DataProcessor()
        
        # Create sample bushfire-like data
        sample_data = pd.DataFrame({
            'latitude': np.random.uniform(-37.5, -36.5, 100),
            'longitude': np.random.uniform(144.5, 145.5, 100),
            'temperature': np.random.normal(35, 5, 100),
            'humidity': np.random.normal(30, 10, 100),
            'wind_speed': np.random.exponential(15, 100),
            'fire_intensity': np.random.exponential(50, 100) + 30,
        })
        
        # Store dataset
        dataset_id = processor.store_dataset(sample_data, "bushfire_test.csv")
        
        # Execute visualization code
        code = f"""
import pandas as pd
import numpy as np

# Access the stored dataset
data = list(locals().values())[0]  # Get first dataset

# Calculate positions
lat_center = data['latitude'].mean()
lon_center = data['longitude'].mean()

positions = np.column_stack([
    (data['longitude'] - lon_center) * 100,
    (data['latitude'] - lat_center) * 100,
    data['fire_intensity'] / 10
])

# Create colors
colors = create_heatmap_colors(data['fire_intensity'], 'fire')

# Create visualization
viz_data = create_particle_system(
    positions=positions,
    colors=colors,
    sizes=data['fire_intensity'] / 20
)

print(f"Created visualization with {{len(positions)}} points")
"""
        
        result = await processor.execute_code(code, {dataset_id: processor.datasets[dataset_id]})
        
        # Check that execution was successful
        assert result['success'] is True
        assert result['visualization_data'] is not None
        assert len(result['visualization_data']) > 0
        
        # Check visualization structure
        viz = result['visualization_data'][0]
        assert viz['type'] == 'particles'
        assert len(viz['positions']) == 100
        assert len(viz['colors']) == 100
        assert len(viz['sizes']) == 100


def run_tests():
    """Run all tests."""
    print("🧪 Running VisFlow Test Suite")
    print("=" * 50)
    
    # Run pytest with verbose output
    import subprocess
    import sys
    
    test_file = __file__
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        test_file, "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0


if __name__ == "__main__":
    # Run tests when executed directly
    success = run_tests()
    sys.exit(0 if success else 1)