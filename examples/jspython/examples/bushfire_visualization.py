"""
Australian Bushfire Visualization Example
This script demonstrates how to visualize bushfire risk data in 3D
"""

import pandas as pd
import numpy as np

# Load sample bushfire data
# In a real scenario, this would come from the uploaded CSV
data = pd.read_csv('src/visflow/static/sample_data/bushfire_data.csv')

# Calculate fire risk based on weather conditions
def calculate_fire_risk(temperature, humidity, wind_speed):
    """Calculate fire risk based on weather conditions"""
    return (temperature * wind_speed) / (humidity + 10)

# Add fire risk to the dataset
data['fire_risk'] = calculate_fire_risk(data['temperature'], data['humidity'], data['wind_speed'])

# Normalize values for visualization
data['fire_risk_normalized'] = (data['fire_risk'] - data['fire_risk'].min()) / (data['fire_risk'].max() - data['fire_risk'].min())
data['temp_normalized'] = (data['temperature'] - data['temperature'].min()) / (data['temperature'].max() - data['temperature'].min())

# Prepare data for 3D visualization
# We'll use latitude, longitude, and time (converted to numeric) as coordinates
# Fire risk will determine color and size
data['time_numeric'] = pd.to_datetime(data['timestamp']).astype(int) / 10**9
data['time_normalized'] = (data['time_numeric'] - data['time_numeric'].min()) / (data['time_numeric'].max() - data['time_numeric'].min())

# Send to visualization
result = data[['latitude', 'longitude', 'time_normalized', 'fire_risk_normalized', 'temp_normalized']]