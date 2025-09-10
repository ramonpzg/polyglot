"""
Command-line interface for Merengue Cyclone hurricane tracker.
"""

import click
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from .hurricane import (
    HurricaneTracker,
    HurricanePoint,
    calculate_distance,
    estimate_surge,
)
from .server import start_server


@click.group()
@click.version_option(version="0.1.0", prog_name="merengue-cyclone")
def main():
    """
    Merengue Cyclone - High-performance hurricane tracking and analysis.

    Named after the energetic Dominican dance, this tool spins through
    hurricane data with Zig-powered performance.
    """
    pass


@main.command()
@click.option("--scenario", default="maria",
              type=click.Choice(["maria", "georges", "david", "custom"]),
              help="Historical hurricane scenario to simulate")
@click.option("--show", is_flag=True, help="Display visualization")
@click.option("--output", type=click.Path(), help="Save results to JSON file")
def simulate(scenario: str, show: bool, output: Optional[str]):
    """Run hurricane track simulation."""
    click.echo(f"🌀 Simulating Hurricane {scenario.upper()}...")

    tracker = HurricaneTracker()

    # Load scenario data
    if scenario == "maria":
        # Hurricane Maria (2017) - devastating Cat 5 that hit Dominica and PR
        points = [
            HurricanePoint(15.0, -59.0, 958, 241, datetime(2017, 9, 19, 0)),
            HurricanePoint(15.3, -60.1, 950, 257, datetime(2017, 9, 19, 6)),
            HurricanePoint(15.7, -61.2, 930, 280, datetime(2017, 9, 19, 12)),
            HurricanePoint(16.2, -62.4, 925, 295, datetime(2017, 9, 19, 18)),
            HurricanePoint(16.8, -63.7, 920, 280, datetime(2017, 9, 20, 0)),
            HurricanePoint(17.5, -65.0, 925, 270, datetime(2017, 9, 20, 6)),
            HurricanePoint(18.0, -66.5, 935, 250, datetime(2017, 9, 20, 12)),
        ]
    elif scenario == "georges":
        # Hurricane Georges (1998) - directly hit DR
        points = [
            HurricanePoint(16.0, -64.0, 970, 185, datetime(1998, 9, 21, 0)),
            HurricanePoint(16.5, -65.5, 965, 195, datetime(1998, 9, 21, 6)),
            HurricanePoint(17.2, -67.0, 960, 205, datetime(1998, 9, 21, 12)),
            HurricanePoint(17.9, -68.5, 955, 215, datetime(1998, 9, 21, 18)),
            HurricanePoint(18.5, -70.0, 960, 195, datetime(1998, 9, 22, 0)),
        ]
    elif scenario == "david":
        # Hurricane David (1979) - Cat 5 that struck DR
        points = [
            HurricanePoint(14.0, -56.0, 950, 240, datetime(1979, 8, 29, 0)),
            HurricanePoint(14.8, -58.0, 940, 260, datetime(1979, 8, 29, 6)),
            HurricanePoint(15.6, -60.0, 930, 280, datetime(1979, 8, 29, 12)),
            HurricanePoint(16.5, -62.0, 925, 290, datetime(1979, 8, 29, 18)),
            HurricanePoint(17.4, -64.0, 930, 280, datetime(1979, 8, 30, 0)),
            HurricanePoint(18.3, -66.0, 940, 260, datetime(1979, 8, 30, 6)),
        ]
    else:
        # Custom scenario
        points = [
            HurricanePoint(14.0 + i * 0.5, -60.0 - i * 1.5,
                          980 - i * 5, 150 + i * 10,
                          datetime.now() + timedelta(hours=i * 6))
            for i in range(10)
        ]

    # Add points to tracker
    for point in points:
        tracker.add_observation(scenario, point)

    # Analyze track
    analysis = tracker.analyze_track(scenario)
    click.echo(f"📊 Track Analysis:")
    click.echo(f"  • Total distance: {analysis.total_distance:.1f} km")
    click.echo(f"  • Average speed: {analysis.average_speed:.1f} km/h")
    click.echo(f"  • Max intensity: {analysis.max_intensity.wind_speed:.0f} km/h "
              f"(Category {analysis.max_intensity.category})")
    click.echo(f"  • ACE Index: {analysis.ace:.2f}")

    # Predict future track
    predictions = tracker.predict_next_position(scenario, hours=24)
    click.echo(f"\n🔮 24-hour Forecast:")
    for i, pred in enumerate(predictions[::6], 1):  # Show every 6 hours
        click.echo(f"  +{i*6}h: {pred.lat:.1f}°N, {pred.lon:.1f}°W, "
                  f"{pred.wind_speed:.0f} km/h")

    # Dominican Republic impact assessment
    impact = tracker.estimate_dominican_impact(scenario)
    click.echo(f"\n🇩🇴 Dominican Republic Impact Assessment:")
    click.echo(f"  • Risk level: {impact['risk'].upper()}")
    click.echo(f"  • Closest approach: {impact['closest_approach_km']:.0f} km")
    click.echo(f"  • Maximum winds: {impact['max_winds_kmh']:.0f} km/h")
    click.echo(f"  • Storm surge estimate: {impact['estimated_surge_m']:.1f} m")

    if show:
        click.echo("\n📈 Launching visualization...")
        _show_visualization(tracker, scenario)

    if output:
        results = {
            "scenario": scenario,
            "track": [
                {
                    "lat": p.lat, "lon": p.lon,
                    "pressure": p.pressure, "wind_speed": p.wind_speed,
                    "timestamp": p.timestamp.isoformat(),
                    "category": p.category
                }
                for p in points
            ],
            "analysis": {
                "total_distance_km": analysis.total_distance,
                "average_speed_kmh": analysis.average_speed,
                "ace": analysis.ace,
                "max_intensity": {
                    "wind_speed_kmh": analysis.max_intensity.wind_speed,
                    "category": analysis.max_intensity.category,
                }
            },
            "dr_impact": impact,
            "predictions": [
                {
                    "lat": p.lat, "lon": p.lon,
                    "wind_speed": p.wind_speed,
                    "timestamp": p.timestamp.isoformat()
                }
                for p in predictions
            ]
        }

        Path(output).write_text(json.dumps(results, indent=2, default=str))
        click.echo(f"💾 Results saved to {output}")


@main.command()
@click.option("--size", default=100, help="Number of track points to process")
@click.option("--iterations", default=10000, help="Number of iterations")
@click.option("--compare", is_flag=True, help="Compare Zig vs Python performance")
def benchmark(size: int, iterations: int, compare: bool):
    """Benchmark performance of hurricane calculations."""
    click.echo("⚡ Running performance benchmark...")

    tracker = HurricaneTracker()

    # Create test data
    click.echo(f"  • Generating {size} track points...")
    points = []
    for i in range(size):
        points.append(HurricanePoint(
            lat=15.0 + i * 0.1,
            lon=-60.0 - i * 0.15,
            pressure=980 - (i % 20),
            wind_speed=150 + (i % 30) * 5,
            timestamp=datetime.now() + timedelta(hours=i * 3)
        ))

    # Add to tracker
    for point in points:
        tracker.add_observation("benchmark", point)

    click.echo(f"  • Running {iterations} distance calculations...")

    if compare:
        results = tracker.benchmark_performance(iterations)

        click.echo("\n📊 Performance Results:")
        if 'python_ms' in results:
            click.echo(f"  • Python: {results['python_ms']:.2f} ms")
        if 'zig_ms' in results:
            click.echo(f"  • Zig: {results['zig_ms']:.2f} ms")
        if 'speedup' in results:
            click.echo(f"  • 🚀 Speedup: {results['speedup']:.1f}x faster with Zig!")
    else:
        # Just benchmark the current implementation
        start = time.perf_counter()

        # Distance calculations
        for _ in range(iterations // 100):
            for i in range(len(points) - 1):
                calculate_distance(
                    points[i].lat, points[i].lon,
                    points[i+1].lat, points[i+1].lon
                )

        elapsed = (time.perf_counter() - start) * 1000

        click.echo(f"\n📊 Performance Results:")
        click.echo(f"  • Time: {elapsed:.2f} ms")
        click.echo(f"  • Operations/sec: {(iterations / elapsed * 1000):.0f}")

    # Track analysis benchmark
    click.echo("\n🔬 Analyzing complete track...")
    start = time.perf_counter()
    analysis = tracker.analyze_track("benchmark")
    analysis_time = (time.perf_counter() - start) * 1000

    click.echo(f"  • Track analysis time: {analysis_time:.2f} ms")
    click.echo(f"  • ACE calculation: {analysis.ace:.2f}")
    click.echo(f"  • Points processed: {len(points)}")


@main.command()
@click.option("--port", default=8000, help="Port to run server on")
@click.option("--host", default="127.0.0.1", help="Host to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
def serve(port: int, host: str, reload: bool):
    """Start the hurricane tracking web server."""
    click.echo(f"🌀 Starting Merengue Cyclone server...")
    click.echo(f"   Dancing at http://{host}:{port} 💃")
    click.echo(f"\n   Press Ctrl+C to stop")

    start_server(host=host, port=port, reload=reload)


@main.command()
@click.option("--location", default="santo_domingo",
              type=click.Choice(["santo_domingo", "punta_cana", "puerto_plata", "santiago"]),
              help="Location to check surge risk")
@click.option("--wind-speed", default=200.0, help="Wind speed in km/h")
@click.option("--pressure", default=950.0, help="Central pressure in millibars")
@click.option("--depth", default=20.0, help="Coastal water depth in meters")
@click.option("--angle", default=45.0, help="Storm approach angle in degrees")
def surge(location: str, wind_speed: float, pressure: float, depth: float, angle: float):
    """Calculate storm surge estimate for Dominican Republic locations."""

    locations = {
        "santo_domingo": {"name": "Santo Domingo", "depth": 25, "typical_angle": 60},
        "punta_cana": {"name": "Punta Cana", "depth": 15, "typical_angle": 45},
        "puerto_plata": {"name": "Puerto Plata", "depth": 30, "typical_angle": 30},
        "santiago": {"name": "Santiago", "depth": 0, "typical_angle": 0},  # Inland
    }

    loc_info = locations[location]

    if location == "santiago":
        click.echo(f"🏔️ {loc_info['name']} is inland - no direct storm surge risk")
        click.echo("   However, flooding from rainfall is still a major concern!")
        return

    # Use location-specific depth if not overridden
    if depth == 20.0:
        depth = loc_info['depth']
    if angle == 45.0:
        angle = loc_info['typical_angle']

    surge_height = estimate_surge(wind_speed, pressure, depth, angle)

    click.echo(f"🌊 Storm Surge Estimate for {loc_info['name']}:")
    click.echo(f"  • Wind speed: {wind_speed:.0f} km/h")
    click.echo(f"  • Central pressure: {pressure:.0f} mb")
    click.echo(f"  • Coastal depth: {depth:.0f} m")
    click.echo(f"  • Approach angle: {angle:.0f}°")
    click.echo(f"\n  📏 Estimated surge: {surge_height:.1f} meters")

    # Risk assessment
    if surge_height < 1.0:
        risk = "Low"
        emoji = "🟢"
    elif surge_height < 2.0:
        risk = "Moderate"
        emoji = "🟡"
    elif surge_height < 3.0:
        risk = "High"
        emoji = "🟠"
    else:
        risk = "Extreme"
        emoji = "🔴"

    click.echo(f"  {emoji} Risk level: {risk}")

    if surge_height > 2.0:
        click.echo("\n  ⚠️  WARNING: Life-threatening storm surge possible!")
        click.echo("     Immediate evacuation of coastal areas recommended")


def _show_visualization(tracker: HurricaneTracker, scenario: str):
    """Display matplotlib visualization of hurricane track."""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        click.echo("⚠️  Matplotlib not installed. Install with: pip install matplotlib")
        return

    track = tracker.tracks[scenario]
    predictions = tracker.predict_next_position(scenario, hours=48)

    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Track map
    lats = [p.lat for p in track]
    lons = [p.lon for p in track]
    pred_lats = [p.lat for p in predictions]
    pred_lons = [p.lon for p in predictions]

    ax1.plot(lons, lats, 'b-', linewidth=2, label='Historical Track')
    ax1.plot(pred_lons, pred_lats, 'r--', linewidth=2, label='Predicted Track')

    # Mark Dominican Republic
    ax1.plot(-70.16, 18.73, 'g*', markersize=15, label='Dominican Republic')

    # Add intensity colors
    for p in track:
        color = ['gray', 'yellow', 'orange', 'red', 'darkred', 'purple'][p.category]
        ax1.plot(p.lon, p.lat, 'o', color=color, markersize=8)

    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude')
    ax1.set_title(f'Hurricane {scenario.upper()} Track')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Intensity timeline
    times = [(p.timestamp - track[0].timestamp).total_seconds() / 3600 for p in track]
    winds = [p.wind_speed for p in track]

    ax2.plot(times, winds, 'b-', linewidth=2)
    ax2.fill_between(times, 0, winds, alpha=0.3)
    ax2.axhline(y=119, color='yellow', linestyle='--', label='Cat 1')
    ax2.axhline(y=154, color='orange', linestyle='--', label='Cat 2')
    ax2.axhline(y=178, color='red', linestyle='--', label='Cat 3')
    ax2.axhline(y=208, color='darkred', linestyle='--', label='Cat 4')
    ax2.axhline(y=252, color='purple', linestyle='--', label='Cat 5')

    ax2.set_xlabel('Hours from Start')
    ax2.set_ylabel('Wind Speed (km/h)')
    ax2.set_title('Intensity Over Time')
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
