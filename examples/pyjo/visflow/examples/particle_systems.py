#!/usr/bin/env python3
"""
Advanced Particle Systems Examples

This script demonstrates various particle system techniques for 3D data visualization
using VisFlow. Examples include:
- Galaxy spiral formations
- Molecular dynamics simulations
- Fluid flow patterns
- Atmospheric particle clouds
- Data clustering visualizations

Perfect for exploring large datasets with spatial relationships.
"""

import pandas as pd
import numpy as np
from math import pi, sin, cos, exp, sqrt


def create_galaxy_spiral(n_particles=10000, arms=3, arm_spread=0.5):
    """
    Create a spiral galaxy particle system.
    
    Args:
        n_particles: Number of particles
        arms: Number of spiral arms
        arm_spread: How spread out the arms are
    
    Returns:
        Dict containing particle system data
    """
    
    print(f"🌌 Creating galaxy with {n_particles} stars and {arms} spiral arms")
    
    positions = []
    colors = []
    sizes = []
    
    for i in range(n_particles):
        # Spiral parameters
        r = np.random.exponential(20) + 5  # Distance from center
        arm = np.random.randint(arms)  # Which arm
        
        # Spiral angle calculation
        base_angle = (2 * pi * arm) / arms
        spiral_angle = base_angle + (r / 10) * pi + np.random.normal(0, arm_spread)
        
        # 3D position
        x = r * cos(spiral_angle) + np.random.normal(0, 2)
        y = r * sin(spiral_angle) + np.random.normal(0, 2)
        z = np.random.normal(0, r / 10)  # Disk thickness varies with radius
        
        positions.append([x, y, z])
        
        # Color based on distance (blue core, yellow edge, red far)
        color_factor = min(r / 50, 1.0)
        if r < 15:  # Core region - blue/white
            colors.append([0.7 + 0.3 * (1 - r/15), 0.8 + 0.2 * (1 - r/15), 1.0])
        elif r < 30:  # Mid region - yellow
            colors.append([1.0, 1.0, 0.6 + 0.4 * (1 - (r-15)/15)])
        else:  # Outer region - red
            colors.append([1.0, 0.3 + 0.4 * (1 - min((r-30)/20, 1)), 0.2])
        
        # Size based on "brightness" (inverse square law with noise)
        brightness = max(0.5, 10 / (r + 5)) * np.random.uniform(0.5, 2.0)
        sizes.append(min(brightness * 3, 8))
    
    return {
        'type': 'particles',
        'positions': positions,
        'colors': colors,
        'sizes': sizes,
        'point_size': 2,
        'opacity': 0.9
    }


def create_molecular_dynamics(n_molecules=5000, temperature=300):
    """
    Simulate molecular dynamics in a gas cloud.
    
    Args:
        n_molecules: Number of molecules
        temperature: Temperature affecting velocity distribution
    
    Returns:
        Dict containing particle system data
    """
    
    print(f"⚛️  Simulating {n_molecules} molecules at {temperature}K")
    
    # Maxwell-Boltzmann velocity distribution
    k_b = 1.380649e-23  # Boltzmann constant
    mass = 4.65e-26  # Argon atom mass (kg)
    
    # Velocity scale factor
    v_scale = sqrt(k_b * temperature / mass) / 1000  # Scale for visualization
    
    positions = []
    colors = []
    sizes = []
    velocities = []
    
    for i in range(n_molecules):
        # Random position in a sphere
        r = np.random.uniform(0, 30)
        theta = np.random.uniform(0, 2 * pi)
        phi = np.random.uniform(0, pi)
        
        x = r * sin(phi) * cos(theta)
        y = r * sin(phi) * sin(theta)
        z = r * cos(phi)
        
        positions.append([x, y, z])
        
        # Maxwell-Boltzmann velocity distribution
        vx = np.random.normal(0, v_scale)
        vy = np.random.normal(0, v_scale)
        vz = np.random.normal(0, v_scale)
        
        velocity_magnitude = sqrt(vx*vx + vy*vy + vz*vz)
        velocities.append([vx, vy, vz])
        
        # Color based on kinetic energy (velocity)
        energy_factor = min(velocity_magnitude / (v_scale * 3), 1.0)
        
        if energy_factor < 0.3:  # Slow - blue
            colors.append([0.2, 0.5, 1.0])
        elif energy_factor < 0.7:  # Medium - green/yellow
            colors.append([energy_factor, 1.0, 0.3])
        else:  # Fast - red
            colors.append([1.0, 0.5 - energy_factor * 0.3, 0.1])
        
        # Size based on energy
        sizes.append(1 + energy_factor * 3)
    
    # Calculate some statistics
    avg_energy = np.mean([sqrt(sum(v[i]**2 for i in range(3))) for v in velocities])
    print(f"   Average molecular speed: {avg_energy:.2f} (scaled units)")
    
    return {
        'type': 'particles',
        'positions': positions,
        'colors': colors,
        'sizes': sizes,
        'point_size': 2,
        'opacity': 0.7
    }


def create_fluid_flow(n_particles=8000, flow_type='vortex'):
    """
    Create fluid flow particle system.
    
    Args:
        n_particles: Number of particles
        flow_type: 'vortex', 'laminar', or 'turbulent'
    
    Returns:
        Dict containing particle system data
    """
    
    print(f"🌊 Creating {flow_type} fluid flow with {n_particles} particles")
    
    positions = []
    colors = []
    sizes = []
    
    for i in range(n_particles):
        if flow_type == 'vortex':
            # Vortex flow pattern
            r = np.random.uniform(5, 40)
            theta = np.random.uniform(0, 2 * pi)
            height = np.random.uniform(-20, 20)
            
            # Vortex velocity field
            v_theta = 30 / r  # Tangential velocity
            v_r = -2  # Slight inward flow
            
            x = r * cos(theta)
            y = r * sin(theta)
            z = height
            
            # Color based on velocity
            velocity = sqrt(v_theta**2 + v_r**2)
            vel_factor = min(velocity / 10, 1.0)
            
        elif flow_type == 'laminar':
            # Laminar pipe flow
            x = np.random.uniform(-50, 50)
            r = np.random.uniform(0, 15)
            theta = np.random.uniform(0, 2 * pi)
            y = r * cos(theta)
            z = r * sin(theta)
            
            # Parabolic velocity profile
            velocity = 10 * (1 - (r / 15)**2)
            vel_factor = velocity / 10
            
        else:  # turbulent
            # Turbulent flow with eddies
            x = np.random.uniform(-40, 40)
            y = np.random.uniform(-25, 25)
            z = np.random.uniform(-25, 25)
            
            # Turbulent velocity with random fluctuations
            velocity = 5 + 3 * abs(sin(x/10) * cos(y/8)) + np.random.normal(0, 2)
            vel_factor = min(abs(velocity) / 8, 1.0)
        
        positions.append([x, y, z])
        
        # Color based on velocity (blue=slow, red=fast)
        colors.append([vel_factor, 0.3, 1.0 - vel_factor])
        sizes.append(1 + vel_factor * 2)
    
    return {
        'type': 'particles',
        'positions': positions,
        'colors': colors,
        'sizes': sizes,
        'point_size': 2,
        'opacity': 0.6
    }


def create_data_clusters(n_clusters=5, points_per_cluster=800):
    """
    Create clustered data points to demonstrate data analysis visualization.
    
    Args:
        n_clusters: Number of clusters
        points_per_cluster: Points per cluster
    
    Returns:
        Dict containing particle system data
    """
    
    print(f"📊 Creating {n_clusters} data clusters with {points_per_cluster} points each")
    
    positions = []
    colors = []
    sizes = []
    
    # Generate cluster centers
    cluster_centers = []
    cluster_colors = []
    
    for i in range(n_clusters):
        center = [np.random.uniform(-40, 40) for _ in range(3)]
        cluster_centers.append(center)
        
        # Unique color for each cluster
        hue = i / n_clusters * 2 * pi
        color = [
            0.5 + 0.5 * cos(hue),
            0.5 + 0.5 * cos(hue + 2*pi/3),
            0.5 + 0.5 * cos(hue + 4*pi/3)
        ]
        cluster_colors.append(color)
    
    # Generate points around each center
    for cluster_idx in range(n_clusters):
        center = cluster_centers[cluster_idx]
        base_color = cluster_colors[cluster_idx]
        
        # Cluster size and shape parameters
        cluster_size = np.random.uniform(8, 15)
        elongation = np.random.uniform(0.5, 2.0)  # Make some clusters elongated
        
        for _ in range(points_per_cluster):
            # Generate point around cluster center
            angle = np.random.uniform(0, 2 * pi)
            elevation = np.random.uniform(-pi/2, pi/2)
            
            # Distance from center (exponential distribution for natural clustering)
            distance = np.random.exponential(cluster_size / 3)
            
            # Apply elongation in random direction
            stretch_direction = np.random.choice([0, 1, 2])
            stretch_factor = elongation if np.random.random() > 0.5 else 1.0
            
            # Calculate position
            dx = distance * cos(elevation) * cos(angle)
            dy = distance * cos(elevation) * sin(angle) 
            dz = distance * sin(elevation)
            
            # Apply stretch
            if stretch_direction == 0:
                dx *= stretch_factor
            elif stretch_direction == 1:
                dy *= stretch_factor
            else:
                dz *= stretch_factor
            
            x = center[0] + dx
            y = center[1] + dy
            z = center[2] + dz
            
            positions.append([x, y, z])
            
            # Color variation within cluster
            color_variation = 0.3
            color = [
                max(0, min(1, base_color[0] + np.random.normal(0, color_variation))),
                max(0, min(1, base_color[1] + np.random.normal(0, color_variation))),
                max(0, min(1, base_color[2] + np.random.normal(0, color_variation)))
            ]
            colors.append(color)
            
            # Size based on distance from cluster center (core is larger)
            core_distance = sqrt(dx*dx + dy*dy + dz*dz)
            size_factor = max(0.3, 1 / (1 + core_distance / cluster_size))
            sizes.append(1 + size_factor * 3)
    
    return {
        'type': 'particles',
        'positions': positions,
        'colors': colors,
        'sizes': sizes,
        'point_size': 2,
        'opacity': 0.8
    }


def create_atmospheric_clouds(n_particles=6000, cloud_type='cumulus'):
    """
    Create atmospheric cloud particle system.
    
    Args:
        n_particles: Number of particles
        cloud_type: 'cumulus', 'stratus', or 'cirrus'
    
    Returns:
        Dict containing particle system data
    """
    
    print(f"☁️  Creating {cloud_type} cloud with {n_particles} particles")
    
    positions = []
    colors = []
    sizes = []
    
    for i in range(n_particles):
        if cloud_type == 'cumulus':
            # Puffy cumulus clouds - vertical development
            base_r = np.random.exponential(15)
            theta = np.random.uniform(0, 2 * pi)
            
            x = base_r * cos(theta) + np.random.normal(0, 3)
            y = base_r * sin(theta) + np.random.normal(0, 3)
            z = abs(np.random.normal(0, 12)) + np.random.exponential(8)  # Vertical bias
            
            # Density decreases with height
            density = exp(-z / 20)
            
        elif cloud_type == 'stratus':
            # Layered stratus clouds - horizontal
            x = np.random.uniform(-50, 50)
            y = np.random.uniform(-30, 30)
            z = np.random.normal(15, 3)  # Relatively flat
            
            density = exp(-abs(z - 15) / 5)  # Dense in the middle layer
            
        else:  # cirrus
            # High, wispy cirrus clouds
            x = np.random.uniform(-60, 60) 
            y = np.random.uniform(-20, 20)
            z = np.random.normal(35, 5)  # High altitude
            
            # Wispy, streaky pattern
            streak_factor = sin(x / 10) * cos(y / 15)
            density = 0.3 + 0.4 * abs(streak_factor)
        
        positions.append([x, y, z])
        
        # Cloud color - white to gray based on density
        gray_level = 0.4 + 0.6 * density
        colors.append([gray_level, gray_level, gray_level])
        
        # Size based on density
        sizes.append(0.5 + density * 4)
    
    return {
        'type': 'particles',
        'positions': positions,
        'colors': colors,
        'sizes': sizes,
        'point_size': 3,
        'opacity': 0.4
    }


# Main execution
print("🎆 Advanced Particle Systems Showcase")
print("=" * 50)

# Create multiple particle systems
examples = [
    ("Galaxy Spiral", lambda: create_galaxy_spiral(8000, 4, 0.3)),
    ("Molecular Gas", lambda: create_molecular_dynamics(4000, 500)),
    ("Vortex Flow", lambda: create_fluid_flow(6000, 'vortex')),
    ("Data Clusters", lambda: create_data_clusters(6, 600)),
    ("Cumulus Clouds", lambda: create_atmospheric_clouds(5000, 'cumulus'))
]

print("\n🎮 Available Examples:")
for i, (name, _) in enumerate(examples):
    print(f"   {i+1}. {name}")

# Let user choose or show all
selected_example = 0  # Default to galaxy

if selected_example == 0:
    print(f"\n🌟 Creating: {examples[0][0]}")
    viz_data = examples[0][1]()
else:
    print(f"\n🌟 Creating: {examples[selected_example-1][0]}")
    viz_data = examples[selected_example-1][1]()

print("\n✅ Particle system created successfully!")
print(f"   • Particles: {len(viz_data['positions'])}")
print(f"   • Colors: {'Custom' if 'colors' in viz_data else 'Default'}")
print(f"   • Sizes: {'Variable' if 'sizes' in viz_data else 'Uniform'}")

print("\n🎮 Interaction Tips:")
print("   • Mouse wheel: Zoom in/out")
print("   • Left click + drag: Rotate view")
print("   • Right click + drag: Pan camera")
print("   • Try different examples by changing 'selected_example' variable!")

# Uncomment to create multiple visualizations at once:
# print("\n🎨 Creating all examples...")
# viz_data = []
# for name, creator in examples[:3]:  # First 3 examples
#     print(f"Adding {name}...")
#     viz_data.append(creator())