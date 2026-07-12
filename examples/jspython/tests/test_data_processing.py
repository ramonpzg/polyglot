"""
Tests for VisFlow data processing functionality
"""

import unittest
import pandas as pd
import numpy as np
from src.visflow.data_processor import load_weather_data, calculate_fire_risk, process_climate_data, convert_to_3d_coordinates

class TestDataProcessor(unittest.TestCase):
    
    def test_load_weather_data(self):
        """Test loading weather data"""
        df = load_weather_data()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 100)
        expected_columns = ['latitude', 'longitude', 'temperature', 'humidity', 'wind_speed', 'pressure']
        for col in expected_columns:
            self.assertIn(col, df.columns)
    
    def test_calculate_fire_risk(self):
        """Test fire risk calculation"""
        temperature = 35.0
        humidity = 40.0
        wind_speed = 20.0
        risk = calculate_fire_risk(temperature, humidity, wind_speed)
        expected = (35.0 * 20.0) / (40.0 + 10)
        self.assertEqual(risk, expected)
    
    def test_process_climate_data(self):
        """Test climate data processing"""
        # Create sample data
        data = {
            'latitude': [0.0, 1.0, 2.0],
            'longitude': [0.0, 1.0, 2.0],
            'temperature': [20.0, 25.0, 30.0],
            'humidity': [50.0, 60.0, 70.0],
            'wind_speed': [10.0, 15.0, 20.0]
        }
        df = pd.DataFrame(data)
        
        # Process the data
        result = process_climate_data(df)
        
        # Check that fire_risk was added
        self.assertIn('fire_risk', result.columns)
        
        # Check that normalized columns were added
        self.assertIn('temperature_normalized', result.columns)
        self.assertIn('humidity_normalized', result.columns)
        self.assertIn('wind_speed_normalized', result.columns)
        self.assertIn('fire_risk_normalized', result.columns)
    
    def test_convert_to_3d_coordinates(self):
        """Test conversion to 3D coordinates"""
        # Create sample data
        data = {
            'latitude': [0.0, 90.0, -90.0],
            'longitude': [0.0, 0.0, 0.0]
        }
        df = pd.DataFrame(data)
        
        # Convert to 3D coordinates
        result = convert_to_3d_coordinates(df)
        
        # Check that 3D coordinates were added
        self.assertIn('x', result.columns)
        self.assertIn('y', result.columns)
        self.assertIn('z', result.columns)
        
        # Check specific values (approximate due to floating point)
        # At lat=0, lon=0, we should be at (R, 0, 0)
        self.assertAlmostEqual(result.iloc[0]['x'], 6371, places=0)
        self.assertAlmostEqual(result.iloc[0]['y'], 0, places=0)
        self.assertAlmostEqual(result.iloc[0]['z'], 0, places=0)

if __name__ == '__main__':
    unittest.main()