"""Command line interface for Bushfire Simulation."""

import click
import matplotlib.pyplot as plt
import numpy as np
from .server import run_server
from . import BushfireModel, create_visualization
import threading
import time
import webbrowser

@click.group()
def main():
    """🔥 Bushfire Simulation - Real-time fire spread modeling"""
    pass

@main.command()
@click.option('--danger', type=click.Choice(['low', 'moderate', 'high', 'very_high', 'severe', 'extreme', 'catastrophic']), 
              default='moderate', help='Australian fire danger rating')
@click.option('--size', default=80, help='Grid size (width=height)')
@click.option('--steps', default=30, help='Simulation steps')
@click.option('--ignition', default='center', help='Ignition pattern: center, random, multiple')
@click.option('--show', is_flag=True, help='Show matplotlib visualization')
def simulate(danger, size, steps, ignition, show):
    """Run a bushfire simulation with specified parameters."""
    
    click.echo("🔥 BUSHFIRE SIMULATION")
    click.echo("━━━━━━━━━━━━━━━━━━━━━━")
    
    model = BushfireModel(size, size)
    conditions = model.set_conditions(danger)
    
    click.echo(f"\n🌡️  Conditions: {danger.upper()}")
    click.echo(f"   Wind: {conditions['wind']} km/h")
    click.echo(f"   Humidity: {conditions['humidity']}%")
    click.echo(f"   Temperature: {conditions['temp']}°C")
    
    # Set ignition points
    ignition_points = []
    if ignition == 'center':
        ignition_points = [(size//2, size//2)]
    elif ignition == 'random':
        np.random.seed(42)
        ignition_points = [(np.random.randint(size), np.random.randint(size))]
    elif ignition == 'multiple':
        ignition_points = [
            (size//4, size//4),
            (3*size//4, size//4),
            (size//2, 3*size//4)
        ]
    
    model.ignite(ignition_points)
    click.echo(f"\n🎯 Ignition: {len(ignition_points)} point(s)")
    
    # Run simulation
    click.echo(f"\n⏱️  Running {steps} steps...")
    start_time = time.time()
    states = model.simulate_steps(steps)
    sim_time = time.time() - start_time
    
    # Show results
    final_stats = model.get_stats()
    click.echo(f"\n📊 Results:")
    click.echo(f"   Simulation time: {sim_time:.3f}s")
    click.echo(f"   Fire spread: {final_stats['fire_spread_pct']:.1f}% of area")
    click.echo(f"   Active fires: {final_stats['active_fire_pct']:.1f}% of area")
    click.echo(f"   Burnt cells: {final_stats['burnt']:,}")
    click.echo(f"   Burning cells: {final_stats['burning']:,}")
    
    if show:
        click.echo("\n📈 Creating visualization...")
        fig = create_visualization(states, f"Bushfire Simulation - {danger.title()} Conditions")
        
        # Save to file and display path instead of trying to show
        filename = f"bushfire_{danger}_{steps}steps.png"
        fig.savefig(filename, dpi=150, bbox_inches='tight')
        click.echo(f"   Saved visualization to: {filename}")
        
        # Try to open it if possible
        try:
            import webbrowser
            import os
            webbrowser.open(f'file://{os.path.abspath(filename)}')
            click.echo("   Opening in default image viewer...")
        except:
            pass

@main.command()
@click.option('--size', default=100, help='Grid size for benchmark')
@click.option('--steps', default=50, help='Steps to simulate')
def benchmark(size, steps):
    """Benchmark Rust vs Python performance."""
    
    click.echo("⚡ PERFORMANCE BENCHMARK")
    click.echo("━━━━━━━━━━━━━━━━━━━━━━━")
    
    model = BushfireModel(size, size)
    model.set_conditions('high')
    
    click.echo(f"\nBenchmarking {size}x{size} grid, {steps} steps...")
    click.echo("Running Rust and Python implementations...")
    
    results = model.benchmark_rust_vs_python(steps)
    
    click.echo(f"\n⏱️  Results:")
    click.echo(f"   Rust (parallel): {results['rust_time']:.4f}s")
    click.echo(f"   Python (single-threaded): {results['python_time']:.4f}s")
    click.echo(f"   Performance improvement: {results['speedup']:.1f}x faster")
    
    click.echo(f"\n💡 Analysis:")
    if results['speedup'] > 50:
        click.echo("   🚀 Exceptional speedup! Rust's parallel processing + memory")
        click.echo("      efficiency enables real-time applications impossible in Python.")
    elif results['speedup'] > 10:
        click.echo("   ✅ Significant performance gain. Rust eliminates Python's GIL")
        click.echo("      limitations and provides true parallel cellular automata.")
    elif results['speedup'] > 3:
        click.echo("   📈 Clear performance benefits from Rust's systems programming")
        click.echo("      approach to intensive computational tasks.")
    else:
        click.echo("   📊 Modest improvement - overhead may be limiting benefits")
        click.echo("      for this grid size. Try larger grids for better comparison.")

@main.command()
@click.option('--port', default=8001, help='Port to run server on')
@click.option('--no-browser', is_flag=True, help='Don\'t open browser automatically')
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.option('--headless', is_flag=True, help='API-only mode (no web UI)')
def serve(port, no_browser, debug, headless):
    """Start the real-time web interface."""
    
    click.echo("🌐 BUSHFIRE WEB INTERFACE")
    click.echo("━━━━━━━━━━━━━━━━━━━━━━━━")
    
    click.echo(f"\n🖥️  Starting server on port {port}...")
    
    # Start server in background thread
    server_thread = threading.Thread(
        target=run_server,
        args=("127.0.0.1", port, debug, headless),
        daemon=True
    )
    server_thread.start()
    
    # Wait for server to start
    time.sleep(2)
    
    url = f"http://localhost:{port}"
    
    if headless:
        click.echo(f"\n🔌 API server running at {url}")
        click.echo(f"   • WebSocket: ws://localhost:{port}/ws/{{danger_level}}")
        click.echo(f"   • Danger levels: GET {url}/api/danger-levels")
        click.echo("   • Available levels: moderate, high, very_high, severe, extreme, catastrophic")
        click.echo("   • Connect your own UI to the WebSocket API")
        click.echo("   • Press Ctrl+C to stop")
    else:
        if not no_browser:
            webbrowser.open(url)
            click.echo(f"🚀 Opening browser to {url}")
        
        click.echo(f"\n📊 Web interface running at {url}")
        click.echo("   • Adjust fire danger levels")
        click.echo("   • Set ignition points")
        click.echo("   • Watch real-time fire spread")
        click.echo("   • Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        click.echo("\n\n🛑 Shutting down Bushfire Simulation")
        click.echo("Stay fire-safe! 🚒")

if __name__ == "__main__":
    main()
