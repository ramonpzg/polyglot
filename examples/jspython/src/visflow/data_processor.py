"""Python data processing module for VisFlow."""

import pandas as pd
import numpy as np

def load_weather_data():
    """Load sample weather data."""
    # This would typically load from a file or database
    # For now, we'll create sample data
    data = {
        'latitude': np.random.uniform(-90, 90, 100),
        'longitude': np.random.uniform(-180, 180, 100),
        'temperature': np.random.uniform(-10, 40, 100),
        'humidity': np.random.uniform(0, 100, 100),
        'wind_speed': np.random.uniform(0, 50, 100),
        'pressure': np.random.uniform(950, 1050, 100)
    }
    return pd.DataFrame(data)

def calculate_fire_risk(temperature, humidity, wind_speed):
    """Calculate fire risk based on weather conditions."""
    return (temperature * wind_speed) / (humidity + 10)

def process_climate_data(df):
    """Process climate data for visualization."""
    # Add calculated fields
    if all(col in df.columns for col in ['temperature', 'humidity', 'wind_speed']):
        df['fire_risk'] = calculate_fire_risk(df['temperature'], df['humidity'], df['wind_speed'])
    
    # Normalize values for visualization
    for col in ['temperature', 'humidity', 'wind_speed', 'fire_risk']:
        if col in df.columns:
            df[f'{col}_normalized'] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
    
    return df

def convert_to_3d_coordinates(df, lat_col='latitude', lon_col='longitude'):
    """Convert latitude/longitude to 3D coordinates."""
    # Earth radius in kilometers
    R = 6371
    
    # Convert to radians
    lat_rad = np.radians(df[lat_col])
    lon_rad = np.radians(df[lon_col])
    
    # Convert to 3D coordinates
    x = R * np.cos(lat_rad) * np.cos(lon_rad)
    y = R * np.cos(lat_rad) * np.sin(lon_rad)
    z = R * np.sin(lat_rad)
    
    df['x'] = x
    df['y'] = y
    df['z'] = z
    
    return df