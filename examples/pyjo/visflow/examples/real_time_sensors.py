#!/usr/bin/env python3
"""
Real-time Sensor Network Visualization

This example demonstrates how to visualize streaming sensor data in real-time
using VisFlow. It simulates various types of sensor networks:
- Environmental monitoring stations
- IoT device networks  
- Smart city infrastructure
- Agricultural sensor arrays
- Industrial monitoring systems

Features live data updates, alert systems, and network topology visualization.
"""

import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import json
import random


class SensorNetwork:
    """Simulates a network of sensors with real-time data generation."""
    
    def __init__(self, n_sensors=50, sensor_types=['temperature', 'humidity', 'pressure', 'air_quality']):
        self.n_sensors = n_sensors
        self.sensor_types = sensor_types
        self.sensors = self._initialize_sensors()
        self.data_history = []
        self.current_time = datetime.now()
        
    def _initialize_sensors(self):
        """Initialize sensor network with random positions and properties."""
        sensors = []
        
        for i in range(self.n_sensors):
            # Random geographic positions (simulating a city area)
            lat = np.random.uniform(-33.95, -33.80)  # Sydney-like coordinates
            lon = np.random.uniform(151.10, 151.30)
            elevation = max(0, np.random.normal(50, 30))  # Above sea level
            
            sensor = {
                'id': f'SENSOR_{i:03d}',
                'type': np.random.choice(self.sensor_types),
                'latitude': lat,
                'longitude': lon,
                'elevation': elevation,
                'status': 'active',
                'battery_level': np.random.uniform(20, 100),
                'last_maintenance': datetime.now() - timedelta(days=np.random.randint(1, 180)),
                'installation_date': datetime.now() - timedelta(days=np.random.randint(30, 1095))
            }
            
            sensors.append(sensor)
            
        return sensors
    
    def generate_reading(self, sensor):
        """Generate realistic sensor reading based on type."""
        current_hour = self.current_time.hour
        base_noise = np.random.normal(0, 0.1)
        
        if sensor['type'] == 'temperature':
            # Daily temperature cycle
            daily_cycle = 10 * np.sin(2 * np.pi * (current_hour - 6) / 24)
            base_temp = 20 + daily_cycle + np.random.normal(0, 2)
            return max(-10, min(50, base_temp + base_noise))
            
        elif sensor['type'] == 'humidity':
            # Inversely related to temperature cycle
            daily_cycle = -15 * np.sin(2 * np.pi * (current_hour - 6) / 24)
            base_humidity = 60 + daily_cycle + np.random.normal(0, 5)
            return max(10, min(100, base_humidity + base_noise * 10))
            
        elif sensor['type'] == 'pressure':
            # Atmospheric pressure with weather patterns
            weather_pattern = 5 * np.sin(2 * np.pi * current_hour / 168)  # Weekly cycle
            base_pressure = 1013.25 + weather_pattern + np.random.normal(0, 3)
            return max(980, min(1050, base_pressure + base_noise * 5))
            
        elif sensor['type'] == 'air_quality':
            # Air quality index (0-500, lower is better)
            rush_hour_factor = 0
            if 7 <= current_hour <= 9 or 17 <= current_hour <= 19:
                rush_hour_factor = 30  # Higher pollution during rush hour
            
            base_aqi = 50 + rush_hour_factor + np.random.normal(0, 15)
            return max(0, min(500, base_aqi + base_noise * 20))
            
        return 0
    
    def simulate_time_step(self, minutes=5):
        """Advance time and generate new sensor readings."""
        self.current_time += timedelta(minutes=minutes)
        
        readings = []
        for sensor in self.sensors:
            # Simulate sensor failures
            if sensor['status'] == 'active' and np.random.random() < 0.001:
                sensor['status'] = 'fault'
            elif sensor['status'] == 'fault' and np.random.random() < 0.1:
                sensor['status'] = 'active'
            
            # Degrade battery
            sensor['battery_level'] -= np.random.uniform(0.01, 0.05)
            if sensor['battery_level'] <= 0:
                sensor['status'] = 'low_battery'
            
            # Generate reading if sensor is working
            if sensor['status'] == 'active':
                value = self.generate_reading(sensor)
            else:
                value = None
            
            reading = {
                'sensor_id': sensor['id'],
                'timestamp': self.current_time,
                'value': value,
                'type': sensor['type'],
                'latitude': sensor['latitude'],
                'longitude': sensor['longitude'],
                'elevation': sensor['elevation'],
                'status': sensor['status'],
                'battery_level': sensor['battery_level']
            }
            
            readings.append(reading)
        
        return readings


def create_sensor_network_visualization(sensor_data):
    """
    Create 3D visualization of sensor network.
    
    Args:
        sensor_data: List of sensor readings
        
    Returns:
        List of visualization objects
    """
    
    print(f"📡 Visualizing sensor network with {len(sensor_data)} sensors")
    
    # Convert to DataFrame for easier processing
    df = pd.DataFrame(sensor_data)
    
    # Create 3D positions
    lat_center = df['latitude'].mean()
    lon_center = df['longitude'].mean()
    
    positions = []
    colors = []
    sizes = []
    
    for _, sensor in df.iterrows():
        # Convert lat/lon to local coordinates (meters)
        x = (sensor['longitude'] - lon_center) * 111320 * np.cos(np.radians(lat_center))
        y = (sensor['latitude'] - lat_center) * 110540
        z = sensor['elevation'] / 10  # Scale elevation
        
        positions.append([x, y, z])
        
        # Color based on sensor status and value
        if sensor['status'] != 'active' or pd.isna(sensor['value']):
            # Red for faults, orange for low battery
            if sensor['status'] == 'fault':
                colors.append([1.0, 0.0, 0.0])
            elif sensor['status'] == 'low_battery':
                colors.append([1.0, 0.5, 0.0])
            else:
                colors.append([0.5, 0.5, 0.5])  # Gray for unknown
        else:
            # Color based on sensor type and value
            if sensor['type'] == 'temperature':
                # Blue (cold) to Red (hot)
                temp_norm = max(0, min(1, (sensor['value'] - (-10)) / 60))
                colors.append([temp_norm, 0.2, 1.0 - temp_norm])
                
            elif sensor['type'] == 'humidity':
                # Brown (dry) to Blue (humid)  
                hum_norm = sensor['value'] / 100
                colors.append([0.6 - 0.6*hum_norm, 0.3, 0.2 + 0.8*hum_norm])
                
            elif sensor['type'] == 'pressure':
                # Purple (low) to Yellow (high)
                press_norm = (sensor['value'] - 980) / 70
                colors.append([0.8, press_norm, 1.0 - press_norm])
                
            elif sensor['type'] == 'air_quality':
                # Green (good) to Red (bad)
                aqi_norm = min(1, sensor['value'] / 200)
                colors.append([aqi_norm, 1.0 - aqi_norm, 0.2])
        
        # Size based on battery level
        if not pd.isna(sensor['battery_level']):
            size_factor = 0.5 + (sensor['battery_level'] / 100) * 1.5
            sizes.append(size_factor * 4)
        else:
            sizes.append(2)
    
    return {
        'type': 'particles',
        'positions': positions,
        'colors': colors,
        'sizes': sizes,
        'point_size': 3,
        'opacity': 0.9
    }


def create_network_connections(sensor_data, max_distance=5000):
    """Create visualization of network connections between sensors."""
    
    print(f"🔗 Creating network topology (max distance: {max_distance}m)")
    
    df = pd.DataFrame(sensor_data)
    active_sensors = df[df['status'] == 'active']
    
    if len(active_sensors) < 2:
        return None
    
    # Calculate positions
    lat_center = df['latitude'].mean()
    lon_center = df['longitude'].mean()
    
    positions = []
    for _, sensor in active_sensors.iterrows():
        x = (sensor['longitude'] - lon_center) * 111320 * np.cos(np.radians(lat_center))
        y = (sensor['latitude'] - lat_center) * 110540
        z = sensor['elevation'] / 10
        positions.append([x, y, z])
    
    # Create connections between nearby sensors
    connection_points = []
    colors = []
    
    n_sensors = len(positions)
    for i in range(n_sensors):
        for j in range(i + 1, n_sensors):
            pos1, pos2 = positions[i], positions[j]
            
            # Calculate distance
            distance = np.sqrt(sum((pos1[k] - pos2[k])**2 for k in range(3)))
            
            if distance <= max_distance:
                # Add line from sensor i to sensor j
                connection_points.extend([pos1, pos2])
                
                # Color based on connection strength (distance)
                strength = 1.0 - (distance / max_distance)
                colors.extend([[0.2, strength, 0.8], [0.2, strength, 0.8]])
    
    if not connection_points:
        return None
    
    return {
        'type': 'lines',
        'points': connection_points,
        'colors': colors,
        'opacity': 0.5,
        'linewidth': 1
    }


def analyze_sensor_network(sensor_data):
    """Analyze sensor network performance and generate alerts."""
    
    df = pd.DataFrame(sensor_data)
    
    print("📊 SENSOR NETWORK STATUS REPORT")
    print("=" * 50)
    print(f"🕐 Current Time: {df['timestamp'].iloc[0].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📡 Total Sensors: {len(df)}")
    
    # Status breakdown
    status_counts = df['status'].value_counts()
    print(f"\n📈 Sensor Status:")
    for status, count in status_counts.items():
        percentage = (count / len(df)) * 100
        status_emoji = {'active': '✅', 'fault': '❌', 'low_battery': '🔋'}.get(status, '❓')
        print(f"   {status_emoji} {status.title()}: {count} ({percentage:.1f}%)")
    
    # Sensor type breakdown
    type_counts = df['type'].value_counts()
    print(f"\n🔧 Sensor Types:")
    for sensor_type, count in type_counts.items():
        print(f"   • {sensor_type.title()}: {count}")
    
    # Data quality metrics
    active_sensors = df[df['status'] == 'active']
    if len(active_sensors) > 0:
        print(f"\n📊 Current Readings (Active Sensors Only):")
        
        for sensor_type in df['type'].unique():
            type_data = active_sensors[active_sensors['type'] == sensor_type]['value'].dropna()
            if len(type_data) > 0:
                avg_val = type_data.mean()
                min_val = type_data.min()
                max_val = type_data.max()
                
                if sensor_type == 'temperature':
                    unit = '°C'
                elif sensor_type == 'humidity':
                    unit = '%'
                elif sensor_type == 'pressure':
                    unit = ' hPa'
                elif sensor_type == 'air_quality':
                    unit = ' AQI'
                else:
                    unit = ''
                
                print(f"   🌡️  {sensor_type.title()}: {avg_val:.1f}{unit} (range: {min_val:.1f}-{max_val:.1f})")
    
    # Alerts
    alerts = []
    
    # Low battery alerts
    low_battery = df[df['battery_level'] < 20]
    if len(low_battery) > 0:
        alerts.append(f"🔋 {len(low_battery)} sensors have low battery (<20%)")
    
    # Fault alerts  
    faults = df[df['status'] == 'fault']
    if len(faults) > 0:
        alerts.append(f"❌ {len(faults)} sensors reporting faults")
    
    # Data quality alerts
    missing_data = df[pd.isna(df['value']) & (df['status'] == 'active')]
    if len(missing_data) > 0:
        alerts.append(f"📊 {len(missing_data)} active sensors not reporting data")
    
    if alerts:
        print(f"\n🚨 ALERTS:")
        for alert in alerts:
            print(f"   {alert}")
    else:
        print(f"\n✅ No alerts - network operating normally")
    
    # Network coverage
    coverage_area = calculate_coverage_area(df)
    print(f"\n🗺️  Network Coverage: ~{coverage_area:.1f} km²")
    
    return df


def calculate_coverage_area(df):
    """Calculate approximate coverage area of sensor network."""
    if len(df) < 3:
        return 0
    
    # Calculate bounding box
    lat_range = df['latitude'].max() - df['latitude'].min()
    lon_range = df['longitude'].max() - df['longitude'].min()
    
    # Convert to approximate km²
    lat_km = lat_range * 110.54  # 1 degree latitude ≈ 110.54 km
    lon_km = lon_range * 111.32 * np.cos(np.radians(df['latitude'].mean()))  # Longitude varies by latitude
    
    return lat_km * lon_km


# Main execution
print("📡 Real-time Sensor Network Simulation")
print("=" * 50)

# Initialize sensor network
print("🔧 Initializing sensor network...")
network = SensorNetwork(n_sensors=75, sensor_types=['temperature', 'humidity', 'pressure', 'air_quality'])

print(f"✅ Created network with {network.n_sensors} sensors")
print(f"📍 Geographic area: Sydney metropolitan region")
print(f"🔧 Sensor types: {', '.join(network.sensor_types)}")

# Simulate some time steps to get realistic data
print("\n⏳ Simulating sensor data...")
for _ in range(12):  # Simulate 1 hour of data (5-minute intervals)
    readings = network.simulate_time_step(minutes=5)

# Get current readings
current_readings = network.simulate_time_step(minutes=0)

# Analyze network
analyzed_data = analyze_sensor_network(current_readings)

# Create visualizations
print("\n🎨 Creating 3D visualization...")

# Main sensor visualization
sensor_viz = create_sensor_network_visualization(current_readings)

# Network topology
network_viz = create_network_connections(current_readings, max_distance=3000)

# Combine visualizations
viz_data = [sensor_viz]
if network_viz:
    viz_data.append(network_viz)

print("✅ Real-time sensor visualization created!")
print(f"   • Sensor nodes: {len(sensor_viz['positions'])}")
print(f"   • Network connections: {'Yes' if network_viz else 'No'}")

print("\n🎮 Visualization Guide:")
print("   🔴 Red sensors: Hardware fault")
print("   🟠 Orange sensors: Low battery")
print("   🔵 Blue/Purple: Temperature/Pressure sensors")  
print("   🟢 Green/Yellow: Humidity/Air quality sensors")
print("   📏 Size indicates battery level")
print("   🔗 Lines show network connectivity")

print("\n💡 Try This:")
print("   • Modify 'n_sensors' to change network size")
print("   • Adjust 'max_distance' for network topology")
print("   • Run multiple time steps to see changes over time")
print("   • Add new sensor types in 'sensor_types' list")