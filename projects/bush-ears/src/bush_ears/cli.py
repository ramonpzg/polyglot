"""Command line interface for Bush Ears wildlife monitoring."""

import click
import numpy as np
import matplotlib.pyplot as plt
import time
import webbrowser
import threading
from pathlib import Path
from . import BushEarsAnalyzer, AustralianSpecies, create_ecosystem_health_report
from .server import run_server

@click.group()
def main():
    """🦘 Bush Ears - Real-time Australian wildlife audio identification"""
    pass

@main.command()
@click.option('--scenario', 
              type=click.Choice(['dawn_chorus', 'urban_park', 'outback_night', 'endangered_habitat']),
              default='dawn_chorus',
              help='Audio scenario to simulate')
@click.option('--duration', default=10, help='Audio duration in seconds')
@click.option('--analyze', is_flag=True, help='Run real-time analysis on generated audio')
@click.option('--visualize', is_flag=True, help='Create spectrogram visualization')
def simulate(scenario, duration, analyze, visualize):
    """Generate and analyze synthetic Australian wildlife audio."""
    
    click.echo("🦘 BUSH EARS AUDIO SIMULATION")
    click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    analyzer = BushEarsAnalyzer()
    
    click.echo(f"\n🎵 Generating {scenario.replace('_', ' ').title()} audio ({duration}s)...")
    
    # Generate test audio
    audio = analyzer.generate_test_audio(scenario)
    
    click.echo(f"   Generated {len(audio):,} audio samples")
    click.echo(f"   Sample rate: 44,100 Hz")
    click.echo(f"   Duration: {len(audio) / 44100:.1f} seconds")
    
    if analyze:
        click.echo(f"\n🔍 Analyzing audio for wildlife identification...")
        
        # Process audio in chunks (simulate real-time)
        chunk_size = 4410  # 0.1 second chunks
        detections = []
        
        for i in range(0, len(audio) - chunk_size, chunk_size):
            chunk = audio[i:i + chunk_size]
            result = analyzer.analyze_audio_stream(chunk)
            
            if result.get('species_detected', False):
                detections.append({
                    'time': i / 44100,
                    'species': result['common_name'],
                    'confidence': result.get('conservation_weight', 0.5)
                })
        
        if detections:
            click.echo(f"\n📊 Species Detected:")
            for detection in detections:
                click.echo(f"   {detection['time']:5.1f}s - {detection['species']} "
                          f"(confidence: {detection['confidence']:.2f})")
        else:
            click.echo("\n📊 No species detected in this simulation")
        
        # Get ecosystem health report
        health = analyzer.get_ecosystem_health()
        click.echo(f"\n🌱 Ecosystem Health:")
        click.echo(f"   Biodiversity Index: {health.biodiversity_index:.2f}")
        click.echo(f"   Conservation Score: {health.conservation_score:.2f}")
        click.echo(f"   Species Richness: {health.species_richness}")
        click.echo(f"   Total Detections: {health.total_detections}")
    
    if visualize:
        click.echo(f"\n📈 Creating spectrogram visualization...")
        
        fig = analyzer.create_spectrogram_visualization(audio)
        filename = f"bush_ears_{scenario}_{duration}s.png"
        fig.savefig(filename, dpi=150, bbox_inches='tight')
        
        click.echo(f"   Saved spectrogram to: {filename}")
        
        try:
            webbrowser.open(f'file://{Path(filename).resolve()}')
            click.echo("   Opening visualization...")
        except:
            pass

@main.command()
@click.option('--samples', default=50000, help='Number of audio samples to process')
@click.option('--iterations', default=100, help='Number of processing iterations')
def benchmark(samples, iterations):
    """Benchmark C++ vs Python audio processing performance."""
    
    click.echo("⚡ AUDIO PROCESSING BENCHMARK")
    click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    analyzer = BushEarsAnalyzer()
    
    click.echo(f"\nBenchmarking audio processing:")
    click.echo(f"• {samples:,} samples per iteration")
    click.echo(f"• {iterations} iterations")
    click.echo(f"• Total: {samples * iterations:,} samples processed")
    
    results = analyzer.benchmark_cpp_vs_python(samples // 44100)  # Convert to seconds
    
    click.echo(f"\n⏱️ Performance Results:")
    click.echo(f"   C++ time: {results['cpp_time']:.4f}s")
    click.echo(f"   Python time: {results['python_time']:.4f}s") 
    click.echo(f"   Performance improvement: {results['speedup']:.1f}x faster")
    
    click.echo(f"\n📊 Processing Rates:")
    click.echo(f"   C++: {results['cpp_samples_per_second']:,.0f} samples/second")
    click.echo(f"   Python: {results['python_samples_per_second']:,.0f} samples/second")
    
    # Real-time capability analysis
    realtime_samples_per_sec = 44100
    cpp_realtime_ratio = results['cpp_samples_per_second'] / realtime_samples_per_sec
    python_realtime_ratio = results['python_samples_per_second'] / realtime_samples_per_sec
    
    click.echo(f"\n🎧 Real-time Capability:")
    if cpp_realtime_ratio >= 1.0:
        click.echo(f"   ✅ C++ can process {cpp_realtime_ratio:.1f}x real-time speed")
    else:
        click.echo(f"   ❌ C++ cannot keep up with real-time ({cpp_realtime_ratio:.1f}x)")
    
    if python_realtime_ratio >= 1.0:
        click.echo(f"   ✅ Python can process {python_realtime_ratio:.1f}x real-time speed")
    else:
        click.echo(f"   ❌ Python cannot keep up with real-time ({python_realtime_ratio:.1f}x)")
    
    click.echo(f"\n💡 Analysis:")
    if results['speedup'] > 20:
        click.echo("   🚀 Exceptional speedup! C++ enables real-time wildlife")
        click.echo("      monitoring impossible with pure Python audio processing.")
    elif results['speedup'] > 5:
        click.echo("   ✅ Significant performance gain enabling responsive")
        click.echo("      wildlife monitoring systems.")
    else:
        click.echo("   📈 Modest improvement - overhead may limit benefits")
        click.echo("      for this workload size.")

@main.command()
@click.option('--port', default=8002, help='Port to run server on')
@click.option('--no-browser', is_flag=True, help='Don\'t open browser automatically')
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.option('--headless', is_flag=True, help='API-only mode (no web UI)')
def monitor(port, no_browser, debug, headless):
    """Start real-time wildlife monitoring web interface."""
    
    click.echo("🌿 BUSH EARS MONITORING STATION")
    click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    click.echo(f"\n🖥️ Starting monitoring server on port {port}...")
    
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
        click.echo(f"   • WebSocket: ws://localhost:{port}/ws/{{scenario}}")
        click.echo(f"   • Species info: GET {url}/api/species")
        click.echo("   • Send audio data for real-time wildlife identification")
        click.echo("   • Ecosystem health monitoring and reporting")
        click.echo("   • Press Ctrl+C to stop")
    else:
        if not no_browser:
            webbrowser.open(url)
            click.echo(f"🚀 Opening browser to {url}")
        
        click.echo(f"\n🦜 Wildlife monitoring interface at {url}")
        click.echo("   • Generate test audio scenarios")
        click.echo("   • Real-time species identification")  
        click.echo("   • Ecosystem health dashboard")
        click.echo("   • Audio spectrogram visualization")
        click.echo("   • Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        click.echo("\n\n🛑 Shutting down Bush Ears")
        click.echo("Thanks for monitoring Australian wildlife! 🦘")

@main.command()
@click.option('--scenario', 
              type=click.Choice(['dawn_chorus', 'urban_park', 'outback_night', 'endangered_habitat']),
              default='dawn_chorus')
@click.option('--duration', default=30, help='Monitoring session duration in seconds') 
def live_demo(scenario, duration):
    """Run a live wildlife identification demo."""
    
    click.echo("🎤 LIVE WILDLIFE IDENTIFICATION DEMO")
    click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    analyzer = BushEarsAnalyzer()
    
    click.echo(f"\n🌅 Scenario: {scenario.replace('_', ' ').title()}")
    click.echo(f"⏱️ Duration: {duration} seconds")
    click.echo(f"🎯 Monitoring for Australian wildlife...")
    
    # Generate and process audio in real-time chunks
    audio = analyzer.generate_test_audio(scenario)
    chunk_size = 4410  # 0.1 second chunks
    
    click.echo(f"\n🔊 Starting audio analysis...")
    
    detections = []
    start_time = time.time()
    
    for i in range(0, min(len(audio), int(duration * 44100)), chunk_size):
        current_time = time.time() - start_time
        
        if current_time >= duration:
            break
        
        chunk = audio[i:i + chunk_size]
        result = analyzer.analyze_audio_stream(chunk)
        
        if result.get('species_detected', False):
            species_name = result['common_name']
            habitat = result.get('habitat', 'Unknown')
            
            click.echo(f"{current_time:5.1f}s - 🦜 {species_name} detected ({habitat})")
            detections.append((current_time, species_name, result))
        
        # Show progress occasionally
        if i % (chunk_size * 50) == 0:  # Every 5 seconds
            progress = (current_time / duration) * 100
            click.echo(f"{current_time:5.1f}s - 📡 Monitoring... ({progress:.0f}%)")
        
        # Simulate real-time by sleeping
        time.sleep(0.05)  # 50ms delay between chunks
    
    # Final ecosystem report
    health = analyzer.get_ecosystem_health()
    
    click.echo(f"\n📋 Session Summary:")
    click.echo(f"   Duration: {current_time:.1f} seconds")
    click.echo(f"   Species detected: {len(set(d[1] for d in detections))}")
    click.echo(f"   Total detections: {len(detections)}")
    click.echo(f"   Biodiversity index: {health.biodiversity_index:.2f}")
    click.echo(f"   Conservation score: {health.conservation_score:.2f}")
    
    if detections:
        click.echo(f"\n🦘 Detected Species:")
        species_summary = {}
        for _, species, result in detections:
            species_summary[species] = species_summary.get(species, 0) + 1
        
        for species, count in species_summary.items():
            click.echo(f"   • {species}: {count} detections")

if __name__ == "__main__":
    main()
