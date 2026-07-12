"""
Particle Systems Visualization Example
This script demonstrates how to create particle systems for large datasets
"""

import pandas as pd
import numpy as np

# Create a large particle system dataset
num_particles = 50000

# Generate random particle data
data = {
    'x': np.random.uniform(-50, 50, num_particles),
    'y': np.random.uniform(-30, 30, num_particles),
    'z': np.random.uniform(0, 100, num_particles),
    'velocity_x': np.random.uniform(-2, 2, num_particles),
    'velocity_y': np.random.uniform(-2, 2, num_particles),
    'velocity_z': np.random.uniform(-1, 1, num_particles),
    'temperature': np.random.uniform(20, 100, num_particles),
    'pressure': np.random.uniform(950, 1050, num_particles)
}

# Create DataFrame
df = pd.DataFrame(data)

# Normalize values for visualization
for col in ['temperature', 'pressure']:
    df[f'{col}_normalized'] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

# Add color mapping based on temperature
df['color_r'] = df['temperature_normalized']
df['color_g'] = 0.5 * (1 - df['temperature_normalized'])
df['color_b'] = 0.2

# Send to visualization
result = df[['x', 'y', 'z', 'temperature_normalized', 'color_r', 'color_g', 'color_b']]