#!/usr/bin/env python3
"""
Bushfire Visualization Example

This example demonstrates how to create a comprehensive bushfire risk and spread
visualization using VisFlow. It includes:
- Fire risk calculation based on weather conditions
- 3D terrain representation with fire spread animation
- Color-coded risk zones
- Interactive parameter adjustment

Run this with VisFlow:
1. Start VisFlow: `visflow`
2. Upload the bushfire_data.csv sample dataset
3. Copy this code into the editor and run it
"""

import pandas as pd
import numpy as np
import json


def create_bushfire_visualization(data):
    """
    Create a comprehensive 3D bushfire visualization.
    
    Args:
        data: DataFrame with columns ['latitude', 'longitude', 'temperature', 
              'humidity', 'wind_speed', 'fire_intensity', 'elevation', 'time_hours']
    
    Returns:
        Dict containing visualization data for Three.js
    """
    
    # Calculate enhanced fire risk score
    def enhanced_fire_risk(temp, humidity, wind_speed, elevation):
        """Calculate fire risk with elevation factor."""
        base_risk = (temp * wind_speed) / (humidity + 10)
        elevation_factor = 1 + (elevation / 1000)  # Higher elevation = higher risk
        return base_risk * elevation_factor
    
    # Add enhanced risk calculation
    data['enhanced_risk'] = enhanced_fire_risk(
        data['temperature'], 
        data['humidity'], 
        data['wind_speed'],
        data['elevation']
    )
    
    # Create 3D positions (scale coordinates for better visualization)
    lat_center = data['latitude'].mean()
    lon_center = data['longitude'].mean()
    
    positions = np.column_stack([
        (data['longitude'] - lon_center) * 100000,  # Convert to meters approx
        (data['latitude'] - lat_center) * 100000,
        data['elevation'] / 10 + data['fire_intensity'] / 5  # Elevation + fire height
    ])
    
    # Create color mapping based on enhanced risk
    def risk_to_color(risk_values):
        """Convert risk values to fire-like colors."""
        normalized = (risk_values - risk_values.min()) / (risk_values.max() - risk_values.min())
        colors = np.zeros((len(risk_values), 3))
        
        # Fire color gradient: blue -> green -> yellow -> orange -> red
        colors[:, 0] = np.clip(normalized * 2, 0, 1)  # Red channel
        colors[:, 1] = np.clip((1 - normalized) * 2, 0, 1) * 0.5  # Green channel (reduced)
        colors[:, 2] = np.maximum(0, 1 - normalized * 3)  # Blue channel
        
        return colors
    
    colors = risk_to_color(data['enhanced_risk'])
    
    # Size based on fire intensity and time progression
    sizes = np.clip(data['fire_intensity'] / 10 + data['time_hours'] * 2, 2, 20)
    
    # Create the main particle system
    particle_viz = {
        'type': 'particles',
        'positions': positions.tolist(),
        'colors': colors.tolist(),
        'sizes': sizes.tolist(),
        'point_size': 4,
        'opacity': 0.8,
        'material': 'fire'
    }
    
    return particle_viz


def create_terrain_mesh(data):
    """Create a 3D terrain mesh based on elevation data."""
    
    # Create a grid of points for terrain
    lat_range = np.linspace(data['latitude'].min(), data['latitude'].max(), 20)
    lon_range = np.linspace(data['longitude'].min(), data['longitude'].max(), 20)
    
    lat_center = data['latitude'].mean()
    lon_center = data['longitude'].mean()
    
    vertices = []
    for lat in lat_range:
        for lon in lon_range:
            # Find nearest elevation
            distances = np.sqrt((data['latitude'] - lat)**2 + (data['longitude'] - lon)**2)
            nearest_idx = distances.idxmin()
            elevation = data.loc[nearest_idx, 'elevation']
            
            x = (lon - lon_center) * 100000
            y = (lat - lat_center) * 100000
            z = elevation / 15  # Scale down elevation
            
            vertices.append([x, y, z])
    
    # Create faces for the mesh (triangulation)
    faces = []
    n_cols = len(lon_range)
    n_rows = len(lat_range)
    
    for i in range(n_rows - 1):
        for j in range(n_cols - 1):
            # Create two triangles for each quad
            v1 = i * n_cols + j
            v2 = i * n_cols + j + 1
            v3 = (i + 1) * n_cols + j
            v4 = (i + 1) * n_cols + j + 1
            
            faces.extend([[v1, v2, v3], [v2, v4, v3]])
    
    return {
        'type': 'mesh',
        'vertices': vertices,
        'faces': faces,
        'color': 0x8B4513,  # Brown terrain color
        'opacity': 0.6,
        'wireframe': False
    }


def analyze_fire_progression(data):
    """Analyze fire progression over time and print insights."""
    
    print("🔥 BUSHFIRE ANALYSIS REPORT")
    print("=" * 50)
    
    # Time-based analysis
    time_groups = data.groupby('time_hours')
    
    print(f"📊 Data Summary:")
    print(f"   • Total data points: {len(data)}")
    print(f"   • Time range: {data['time_hours'].min()}-{data['time_hours'].max()} hours")
    print(f"   • Geographic area: {len(data)} monitoring stations")
    print()
    
    print(f"🌡️  Weather Conditions:")
    print(f"   • Temperature: {data['temperature'].min():.1f}°C - {data['temperature'].max():.1f}°C")
    print(f"   • Humidity: {data['humidity'].min():.1f}% - {data['humidity'].max():.1f}%")
    print(f"   • Wind Speed: {data['wind_speed'].min():.1f} - {data['wind_speed'].max():.1f} km/h")
    print()
    
    print(f"🔥 Fire Intensity Progression:")
    for hour in sorted(data['time_hours'].unique()):
        hour_data = data[data['time_hours'] == hour]
        avg_intensity = hour_data['fire_intensity'].mean()
        max_intensity = hour_data['fire_intensity'].max()
        print(f"   Hour {hour}: Avg {avg_intensity:.1f}, Max {max_intensity:.1f}")
    
    print()
    
    # Risk zones
    data['risk_zone'] = pd.cut(data['fire_intensity'], 
                              bins=[0, 70, 90, 110, float('inf')],
                              labels=['Low', 'Moderate', 'High', 'Extreme'])
    
    print(f"⚠️  Risk Zone Distribution:")
    risk_counts = data['risk_zone'].value_counts()
    for zone, count in risk_counts.items():
        percentage = (count / len(data)) * 100
        print(f"   • {zone}: {count} points ({percentage:.1f}%)")
    
    return data


# Main visualization script
if 'bushfire_data' in locals() or 'data' in locals():
    # Use loaded dataset
    df = locals().get('bushfire_data', locals().get('data'))
    
    # Analyze the data
    analyzed_data = analyze_fire_progression(df)
    
    # Create visualizations
    print("\n🎨 Creating 3D visualization...")
    
    # Main fire particles
    fire_particles = create_bushfire_visualization(analyzed_data)
    
    # Terrain mesh
    terrain = create_terrain_mesh(analyzed_data)
    
    # Combine visualizations
    viz_data = [fire_particles, terrain]
    
    print("✅ Visualization created successfully!")
    print("\n🎮 3D Scene Controls:")
    print("   • Mouse: Rotate view")
    print("   • Scroll: Zoom in/out") 
    print("   • Right-click + drag: Pan")
    print("   • Press 'Reset View' to center camera")
    
else:
    print("⚠️  No bushfire dataset found!")
    print("📁 Please upload the 'bushfire_data.csv' sample dataset first.")
    print("   Or load it from: Examples → Bushfire Dataset")
    
    # Create sample data for demonstration
    print("\n🔄 Creating sample data for preview...")
    
    n_points = 500
    sample_data = pd.DataFrame({
        'latitude': np.random.uniform(-37.2, -37.0, n_points),
        'longitude': np.random.uniform(144.5, 144.8, n_points),
        'temperature': np.random.normal(40, 5, n_points),
        'humidity': np.random.normal(25, 10, n_points),
        'wind_speed': np.random.exponential(15, n_points),
        'fire_intensity': np.random.exponential(50, n_points) + 30,
        'elevation': np.random.normal(300, 100, n_points),
        'time_hours': np.random.choice([0, 1, 2, 3, 4, 5, 6], n_points)
    })
    
    # Create visualization with sample data
    analyzed_sample = analyze_fire_progression(sample_data)
    fire_particles = create_bushfire_visualization(analyzed_sample)
    terrain = create_terrain_mesh(analyzed_sample)
    
    viz_data = [fire_particles, terrain]
    
    print("✅ Sample visualization ready!")