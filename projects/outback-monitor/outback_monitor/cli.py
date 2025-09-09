"""Command line interface for Outback Monitor."""

import click
import webbrowser
import time
from .server import run_server, REGIONS
import threading

@click.command()
@click.option('--region', type=click.Choice(list(REGIONS.keys())), 
              help='Region to monitor (will prompt if not provided)')
@click.option('--port', default=8000, help='Port to run server on')
@click.option('--no-browser', is_flag=True, help='Don\'t open browser automatically')
def main(region, port, no_browser):
    """Start Outback Monitor - Real-time agricultural dashboard."""
    
    click.echo("🌾 OUTBACK MONITOR")
    click.echo("━━━━━━━━━━━━━━━━━━━")
    
    if not region:
        click.echo("\nAvailable regions:")
        for i, (key, config) in enumerate(REGIONS.items(), 1):
            click.echo(f"  {i}. {key.title()}")
        
        choice = click.prompt("\nSelect region (number or name)", type=str)
        
        # Handle numeric choice
        if choice.isdigit():
            regions_list = list(REGIONS.keys())
            if 1 <= int(choice) <= len(regions_list):
                region = regions_list[int(choice) - 1]
            else:
                click.echo("Invalid choice")
                return
        else:
            # Handle name choice
            region = choice.lower()
            if region not in REGIONS:
                click.echo("Invalid region")
                return
    
    click.echo(f"\n🎯 Monitoring: {region.title()}")
    click.echo(f"🌐 Server: http://localhost:{port}")
    
    # Start server in background thread
    server_thread = threading.Thread(
        target=run_server,
        args=("127.0.0.1", port),
        daemon=True
    )
    server_thread.start()
    
    # Wait a moment for server to start
    time.sleep(2)
    
    # Open browser
    if not no_browser:
        url = f"http://localhost:{port}"
        webbrowser.open(url)
        click.echo(f"🚀 Opening browser to {url}")
    
    click.echo("\n📊 Dashboard running...")
    click.echo("   • Select your region in the browser")
    click.echo("   • Click START to begin monitoring")
    click.echo("   • Press Ctrl+C to stop")
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        click.echo("\n\n🛑 Shutting down Outback Monitor")
        click.echo("Thanks for monitoring the outback! 🌅")

if __name__ == "__main__":
    main()
