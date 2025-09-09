"""Bush Ears - Real-time Australian wildlife audio identification."""

from ._core import (
    AustralianSpecies, 
    AudioProcessor, 
    WildlifeClassifier, 
    EcosystemMonitor, 
    AudioSimulator,
    benchmark_performance
)
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional
import time
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class EcosystemHealth:
    """Ecosystem health assessment based on audio monitoring."""
    biodiversity_index: float
    conservation_score: float
    species_richness: int
    total_detections: int
    monitoring_duration: timedelta
    timestamp: datetime

class BushEarsAnalyzer:
    """High-level Python interface for wildlife audio analysis."""
    
    # Australian species information
    SPECIES_INFO = {
        AustralianSpecies.Kookaburra: {
            'name': 'Laughing Kookaburra',
            'habitat': 'Woodland, urban parks',
            'conservation_status': 'Least Concern',
            'ecosystem_role': 'Top predator, territorial marker'
        },
        AustralianSpecies.Magpie: {
            'name': 'Australian Magpie', 
            'habitat': 'Open woodland, grassland',
            'conservation_status': 'Least Concern',
            'ecosystem_role': 'Insect control, highly intelligent'
        },
        AustralianSpecies.Galah: {
            'name': 'Galah',
            'habitat': 'Open country, urban areas',
            'conservation_status': 'Least Concern',
            'ecosystem_role': 'Seed dispersal, social flocking'
        },
        AustralianSpecies.Koala: {
            'name': 'Koala',
            'habitat': 'Eucalyptus forests',
            'conservation_status': 'Vulnerable',
            'ecosystem_role': 'Eucalyptus forest indicator, flagship species'
        },
        AustralianSpecies.Dingo: {
            'name': 'Dingo',
            'habitat': 'Outback, forest edges',
            'conservation_status': 'Vulnerable',
            'ecosystem_role': 'Apex predator, population control'
        }
    }
    
    def __init__(self):
        self.monitor = EcosystemMonitor()
        self.simulator = AudioSimulator()
        self.session_start = datetime.now()
        self.detection_history = []
        
    def analyze_audio_stream(self, audio_data: np.ndarray) -> Dict:
        """Analyze a chunk of audio for wildlife identification."""
        
        # Process with C++ engine
        result = self.monitor.process_audio_stream(audio_data)
        
        # Add Python-level analysis
        if result.get('species_detected', False):
            species_id = AustralianSpecies(result['species_id'])
            
            # Add ecosystem context
            if species_id in self.SPECIES_INFO:
                species_info = self.SPECIES_INFO[species_id]
                result.update({
                    'habitat': species_info['habitat'],
                    'conservation_status': species_info['conservation_status'],
                    'ecosystem_role': species_info['ecosystem_role'],
                    'detection_time': datetime.now().isoformat()
                })
                
                # Track detection
                self.detection_history.append({
                    'species': species_info['name'],
                    'timestamp': datetime.now(),
                    'conservation_weight': result['conservation_weight']
                })
        
        return result
    
    def get_ecosystem_health(self) -> EcosystemHealth:
        """Get comprehensive ecosystem health assessment."""
        report = self.monitor.get_ecosystem_report()
        
        return EcosystemHealth(
            biodiversity_index=report['biodiversity_index'],
            conservation_score=report['conservation_score'],
            species_richness=len(report['species_counts']),
            total_detections=report['total_detections'],
            monitoring_duration=timedelta(seconds=report['monitoring_duration_seconds']),
            timestamp=datetime.now()
        )
    
    def generate_test_audio(self, scenario: str = 'dawn_chorus') -> np.ndarray:
        """Generate realistic test audio for different scenarios."""
        
        scenarios = {
            'dawn_chorus': [
                AustralianSpecies.Kookaburra,
                AustralianSpecies.Magpie,
                AustralianSpecies.Magpie,
                AustralianSpecies.Galah
            ],
            'urban_park': [
                AustralianSpecies.Magpie,
                AustralianSpecies.Lorikeet,
                AustralianSpecies.Cockatoo
            ],
            'outback_night': [
                AustralianSpecies.Dingo,
                AustralianSpecies.Dingo,
                AustralianSpecies.Koala
            ],
            'endangered_habitat': [
                AustralianSpecies.Koala,
                AustralianSpecies.Koala
            ]
        }
        
        if scenario not in scenarios:
            scenario = 'dawn_chorus'
        
        species_list = [int(species) for species in scenarios[scenario]]
        return self.simulator.generate_ecosystem_audio(species_list, 10.0)
    
    def create_spectrogram_visualization(self, audio_data: np.ndarray) -> plt.Figure:
        """Create publication-ready spectrogram visualization."""
        
        # Generate spectrogram using C++ processor
        processor = AudioProcessor()
        spectrogram = processor.compute_spectrogram(audio_data)
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), 
                                      gridspec_kw={'height_ratios': [1, 2]})
        
        # Time domain plot
        time_axis = np.linspace(0, len(audio_data) / 44100, len(audio_data))
        ax1.plot(time_axis, audio_data, 'k-', linewidth=0.5)
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Amplitude')
        ax1.set_title('Bush Audio Recording')
        ax1.grid(True, alpha=0.3)
        
        # Spectrogram
        extent = [0, len(audio_data) / 44100, 0, 22050]
        im = ax2.imshow(spectrogram.T, aspect='auto', origin='lower', 
                       extent=extent, cmap='inferno')
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Frequency (Hz)')
        ax2.set_title('Spectrogram - Wildlife Audio Analysis')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax2)
        cbar.set_label('Magnitude')
        
        plt.tight_layout()
        return fig
    
    def benchmark_cpp_vs_python(self, audio_length_seconds: int = 30) -> Dict:
        """Compare C++ vs Python audio processing performance."""
        
        # Generate test audio
        audio_samples = int(44100 * audio_length_seconds)
        test_audio = np.random.randn(audio_samples) * 0.1
        
        # C++ benchmark
        cpp_results = benchmark_performance(1024, 100)  # Process 100 windows
        
        # Python comparison (simplified processing)
        start_time = time.time()
        for i in range(100):
            # Simple Python audio processing
            segment = test_audio[i*512:(i*512)+1024]
            if len(segment) >= 1024:
                fft = np.fft.fft(segment * np.hanning(1024))
                magnitude = np.abs(fft[:513])
                
                # Extract basic features
                spectral_centroid = np.sum(magnitude * np.arange(len(magnitude))) / np.sum(magnitude)
                spectral_rolloff = np.where(np.cumsum(magnitude) >= 0.85 * np.sum(magnitude))[0]
                if len(spectral_rolloff) > 0:
                    spectral_rolloff = spectral_rolloff[0]
                else:
                    spectral_rolloff = len(magnitude) - 1
        
        python_time = time.time() - start_time
        
        return {
            'cpp_time': cpp_results['cpp_time'],
            'python_time': python_time,
            'speedup': python_time / cpp_results['cpp_time'],
            'cpp_samples_per_second': cpp_results['samples_per_second'],
            'python_samples_per_second': (audio_samples * 100) / python_time,
            'test_duration': audio_length_seconds
        }
    
    def get_detection_timeline(self, hours_back: int = 24) -> List[Dict]:
        """Get timeline of species detections for analysis."""
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        recent_detections = [
            detection for detection in self.detection_history
            if detection['timestamp'] >= cutoff_time
        ]
        
        # Group by hour for trend analysis
        hourly_data = {}
        for detection in recent_detections:
            hour_key = detection['timestamp'].strftime('%H:00')
            if hour_key not in hourly_data:
                hourly_data[hour_key] = {'species': set(), 'count': 0, 'conservation_value': 0.0}
            
            hourly_data[hour_key]['species'].add(detection['species'])
            hourly_data[hour_key]['count'] += 1
            hourly_data[hour_key]['conservation_value'] += detection['conservation_weight']
        
        # Convert to timeline format
        timeline = []
        for hour, data in sorted(hourly_data.items()):
            timeline.append({
                'hour': hour,
                'species_count': len(data['species']),
                'detection_count': data['count'],
                'species_list': list(data['species']),
                'conservation_value': data['conservation_value'] / data['count']
            })
        
        return timeline
    
    def reset_session(self):
        """Reset monitoring session."""
        self.monitor.reset_metrics()
        self.detection_history.clear()
        self.session_start = datetime.now()

def create_ecosystem_health_report(health_data: EcosystemHealth) -> str:
    """Create a formatted ecosystem health report."""
    
    report = f"""
🌿 BUSH EARS ECOSYSTEM HEALTH REPORT
Generated: {health_data.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
Monitoring Duration: {health_data.monitoring_duration}

BIODIVERSITY METRICS:
• Species Richness: {health_data.species_richness} species detected
• Shannon Diversity Index: {health_data.biodiversity_index:.2f}
• Conservation Score: {health_data.conservation_score:.2f}
• Total Audio Detections: {health_data.total_detections}

ECOSYSTEM ASSESSMENT:
"""
    
    if health_data.biodiversity_index > 1.5:
        report += "🟢 HIGH BIODIVERSITY - Healthy ecosystem with good species variety\n"
    elif health_data.biodiversity_index > 0.8:
        report += "🟡 MODERATE BIODIVERSITY - Ecosystem functioning but could improve\n"
    else:
        report += "🔴 LOW BIODIVERSITY - Ecosystem may be under stress\n"
    
    if health_data.conservation_score > 0.7:
        report += "🦘 HIGH CONSERVATION VALUE - Important species present\n"
    elif health_data.conservation_score > 0.4:
        report += "📊 MODERATE CONSERVATION VALUE - Mixed species composition\n"
    else:
        report += "⚠️ LOW CONSERVATION VALUE - Few high-priority species detected\n"
    
    return report

__version__ = "0.1.0"
