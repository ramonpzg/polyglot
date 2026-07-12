"""
Real-time Sensors Visualization Example
This script demonstrates how to visualize real-time sensor data
"""

import pandas as pd
import numpy as np
import time

# Simulate real-time sensor data
def generate_sensor_data(num_sensors=100):
    """Generate simulated sensor data"""
    data = {
        'sensor_id': range(num_sensors),
        'latitude': np.random.uniform(-90, 90, num_sensors),
        'longitude': np.random.uniform(-180, 180, num_sensors),
        'temperature': np.random.uniform(-10, 50, num_sensors),
        'humidity': np.random.uniform(0, 100, num_sensors),
        'pressure': np.random.uniform(950, 1050, num_sensors),
        'timestamp': [time.time()] * num_sensors
    }
    return pd.DataFrame(data)

# Generate initial data
df = generate_sensor_data()

# Add some anomalies for visualization interest
anomaly_indices = np.random.choice(df.index, size=5, replace=False)
df.loc[anomaly_indices, 'temperature'] = np.random.uniform(80, 100, 5)

# Normalize values for visualization
for col in ['temperature', 'humidity', 'pressure']:
    df[f'{col}_normalized'] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

# Convert lat/lon to 3D coordinates for visualization
R = 6371  # Earth radius in km
lat_rad = np.radians(df['latitude'])
lon_rad = np.radians(df['longitude'])
df['x'] = R * np.cos(lat_rad) * np.cos(lon_rad)
df['y'] = R * np.cos(lat_rad) * np.sin(lon_rad)
df['z'] = R * np.sin(lat_rad)

# Send to visualization
result = df[['x', 'y', 'z', 'temperature_normalized', 'humidity_normalized', 'pressure_normalized']]