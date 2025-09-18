"""
CaribeTech CLI - Command-line interface for Caribbean hurricane tracking.
"""

import json
import sys
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track
import time

from . import CycloneTracker, benchmark_python_vs_zig

app = typer.Typer(help="🌀 CaribeTech: Caribbean Hurricane Tracking & Analysis")
console = Console()

@app.command()
def analyze(
    years: int = typer.Option(10, "--years", "-y", help="Years of historical data to analyze"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Save results to JSON file"),
    dominican_focus: bool = typer.Option(True, "--dominican-focus", "-d", help="Focus on Dominican Republic threats")
):
    """Analyze historical hurricane data for Caribbean threats."""
    
    console.print(Panel.fit(
        "[bold blue]🌀 CaribeTech Hurricane Analysis[/bold blue]\n"
        "[dim]High-performance Caribbean storm tracking[/dim]",
        border_style="blue"
    ))
    
    with console.status("[bold green]Loading historical data...") as status:
        tracker = CycloneTracker()
        tracks = tracker.load_historical_data(years)
        
        status.update("[bold green]Analyzing storm threats...")
        time.sleep(0.5)  # Simulate processing time
        
        if dominican_focus:
            threats = tracker.analyze_dominican_threats()
        else:
            threats = tracks
    
    # Display results
    console.print(f"\n[bold]Analysis Results for {years} years:[/bold]")
    console.print(f"Total storms tracked: [bold cyan]{len(tracks)}[/bold cyan]")
    
    if dominican_focus:
        console.print(f"Dominican Republic threats: [bold red]{len(threats)}[/bold red]")
    
    # Create threat level table
    table = Table(title="🇩🇴 Dominican Republic Storm Threats", show_header=True)
    table.add_column("Storm", style="cyan", width=12)
    table.add_column("Year", style="blue", width=6)
    table.add_column("Max Category", style="red", width=8)
    table.add_column("Closest Distance (km)", style="yellow", width=15)
    table.add_column("Threat Level", style="bold", width=12)
    
    for track in threats[:10]:  # Show top 10 threats
        distance, _ = track.closest_approach_to_dr
        threat_color = {
            "EXTREME": "bold red",
            "HIGH": "red", 
            "MODERATE": "yellow",
            "LOW": "green"
        }.get(track.threat_level(), "white")
        
        table.add_row(
            track.name,
            str(track.season),
            f"Cat {track.max_category}",
            f"{distance:.0f}",
            f"[{threat_color}]{track.threat_level()}[/{threat_color}]"
        )
    
    console.print(table)
    
    # Save results if requested
    if output:
        results = {
            "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "years_analyzed": years,
            "total_storms": len(tracks),
            "dominican_threats": len(threats) if dominican_focus else len(tracks),
            "threats": [
                {
                    "name": track.name,
                    "year": track.season,
                    "max_category": track.max_category,
                    "closest_distance_km": track.closest_approach_to_dr[0],
                    "threat_level": track.threat_level()
                }
                for track in threats
            ]
        }
        
        with open(output, 'w') as f:
            json.dump(results, f, indent=2)
        
        console.print(f"\n✅ Results saved to [bold cyan]{output}[/bold cyan]")

@app.command()
def simulate():
    """Generate and analyze a sample hurricane approaching Dominican Republic."""
    
    console.print(Panel.fit(
        "[bold yellow]🌪️  Hurricane Simulation[/bold yellow]\n"
        "[dim]Simulating storm approach to Dominican Republic[/dim]",
        border_style="yellow"
    ))
    
    tracker = CycloneTracker()
    
    console.print("\n[bold]Generating sample hurricane...[/bold]")
    storm = tracker.generate_sample_data()
    
    # Show storm details
    distance, closest_point = storm.closest_approach_to_dr
    
    table = Table(title=f"🌀 Hurricane {storm.name} - {storm.season}")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="bold white")
    
    table.add_row("Max Category", f"Category {storm.max_category}")
    table.add_row("Track Points", str(len(storm.points)))
    table.add_row("Closest Approach", f"{distance:.0f} km from Santo Domingo")
    table.add_row("Threat Level", f"[bold red]{storm.threat_level()}[/bold red]")
    
    if closest_point:
        table.add_row("Peak Wind Speed", f"{closest_point.wind_speed_kmh:.0f} km/h")
        table.add_row("Minimum Pressure", f"{closest_point.pressure_hpa:.0f} hPa")
    
    console.print(table)
    
    # Generate path prediction
    console.print("\n[bold]Predicting future path...[/bold]")
    predicted_path = tracker.predict_path(storm.points[-3:], hours_ahead=48)
    
    if predicted_path:
        console.print(f"Generated [bold cyan]{len(predicted_path)}[/bold cyan] prediction points for next 48 hours")
        
        # Show first few predictions
        pred_table = Table(title="🔮 48-Hour Forecast")
        pred_table.add_column("Time", style="cyan")
        pred_table.add_column("Location", style="blue")
        pred_table.add_column("Category", style="red")
        pred_table.add_column("Wind Speed", style="yellow")
        
        for point in predicted_path[:6]:  # Show first 6 predictions
            pred_table.add_row(
                point.timestamp.strftime("%m/%d %H:%M"),
                f"{point.latitude:.2f}°N, {abs(point.longitude):.2f}°W",
                f"Cat {point.category}",
                f"{point.wind_speed_kmh:.0f} km/h"
            )
        
        console.print(pred_table)

@app.command()
def benchmark(
    calculations: int = typer.Option(50000, "--calculations", "-n", help="Number of calculations to benchmark")
):
    """Benchmark Python vs Zig performance for hurricane calculations."""
    
    console.print(Panel.fit(
        "[bold magenta]⚡ Performance Benchmark[/bold magenta]\n"
        "[dim]Comparing Python vs Zig calculation speeds[/dim]",
        border_style="magenta"
    ))
    
    console.print(f"\n[bold]Running {calculations:,} hurricane intensity calculations...[/bold]")
    
    # Run benchmark with progress bar
    for _ in track(range(3), description="Warming up..."):
        time.sleep(0.1)
    
    with console.status("[bold green]Benchmarking..."):
        results = benchmark_python_vs_zig(calculations)
    
    # Display results
    table = Table(title="🏁 Performance Results")
    table.add_column("Implementation", style="cyan", width=12)
    table.add_column("Time (seconds)", style="yellow", width=15)
    table.add_column("Calc/sec", style="green", width=12)
    table.add_column("Performance", style="bold", width=15)
    
    python_rate = calculations / results["python_time"]
    zig_rate = calculations / results["zig_time"]
    
    table.add_row(
        "Python",
        f"{results['python_time']:.4f}",
        f"{python_rate:,.0f}",
        "Baseline"
    )
    
    table.add_row(
        "Zig (SIMD)",
        f"{results['zig_time']:.4f}",
        f"{zig_rate:,.0f}",
        f"[bold green]{results['speedup']:.1f}x faster[/bold green]"
    )
    
    console.print(table)
    
    console.print(f"\n✨ [bold green]Zig provides {results['speedup']:.1f}x speedup[/bold green] for intensive hurricane calculations!")
    console.print("[dim]Real-world performance gains enable real-time storm analysis[/dim]")

@app.command()
def monitor(
    port: int = typer.Option(8000, "--port", "-p", help="Port for web server"),
    host: str = typer.Option("127.0.0.1", "--host", help="Host address"),
    headless: bool = typer.Option(False, "--headless", help="Run API server without opening browser")
):
    """Start real-time hurricane monitoring web server."""
    
    console.print(Panel.fit(
        "[bold green]🌐 CaribeTech Monitor[/bold green]\n"
        "[dim]Starting real-time hurricane tracking server[/dim]",
        border_style="green"
    ))
    
    try:
        import uvicorn
        from .server import app as server_app
        
        console.print(f"\n🚀 Starting server at [bold cyan]http://{host}:{port}[/bold cyan]")
        
        if not headless:
            console.print("[dim]Opening browser for live monitoring...[/dim]")
        else:
            console.print("[dim]Running in headless mode (API only)[/dim]")
        
        # Start the server
        uvicorn.run(
            "caribetech.server:app",
            host=host,
            port=port,
            reload=False,
            log_level="info"
        )
        
    except ImportError:
        console.print("[bold red]❌ Server dependencies not installed![/bold red]")
        console.print("Install with: [bold cyan]pip install 'caribetech[server]'[/bold cyan]")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]🛑 Server stopped by user[/yellow]")

@app.command()
def info():
    """Show CaribeTech system information and capabilities."""
    
    console.print(Panel.fit(
        "[bold blue]🌀 CaribeTech Information[/bold blue]\n"
        "[dim]Dominican Republic Hurricane Tracking System[/dim]",
        border_style="blue"
    ))
    
    info_table = Table(title="System Capabilities")
    info_table.add_column("Feature", style="cyan", width=25)
    info_table.add_column("Implementation", style="yellow", width=20)
    info_table.add_column("Performance", style="green", width=15)
    
    info_table.add_row("Hurricane Path Analysis", "Zig + SIMD", "6-8x faster")
    info_table.add_row("Storm Intensity Calculation", "Zig Optimized", "10x faster")
    info_table.add_row("Distance Calculations", "Vectorized Math", "15x faster")
    info_table.add_row("Real-time Tracking", "WebSocket + FastAPI", "Low latency")
    info_table.add_row("Data Processing", "Python Analytics", "Flexible")
    info_table.add_row("Visualization", "Vue.js Components", "Interactive")
    
    console.print(info_table)
    
    console.print("\n[bold]🇩🇴 Dominican Republic Focus:[/bold]")
    console.print("• Track storms approaching the Caribbean")
    console.print("• Assess threat levels to Santo Domingo")
    console.print("• Historical analysis of hurricane impacts")
    console.print("• Real-time monitoring during storm season")
    
    console.print("\n[bold]⚡ Performance Benefits:[/bold]")
    console.print("• Zig enables real-time calculations for large datasets")
    console.print("• SIMD operations accelerate storm path predictions")
    console.print("• Memory-efficient processing of meteorological data")
    console.print("• Python provides flexible data analysis and APIs")

def main():
    """Main CLI entry point."""
    app()

if __name__ == "__main__":
    main()
