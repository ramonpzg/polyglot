# Bush Ears

Real-time Australian wildlife audio identification for ecosystem health monitoring.

## Overview

Bush Ears uses advanced audio processing and machine learning to identify Australian wildlife from their calls and assess ecosystem health in real-time. This is a novel application demonstrating C++ + Python integration for AI applications.

## Installation

```bash
pip install bush-ears
```

## Usage

### Audio Simulation and Analysis
Generate and analyze realistic Australian wildlife scenarios:

```bash
bush-ears simulate --scenario dawn_chorus --analyze --visualize
```

### Live Wildlife Monitoring Demo
Run a real-time identification demo:

```bash
bush-ears live-demo --scenario endangered_habitat --duration 60
```

### Performance Benchmarking
Compare C++ vs Python audio processing performance:

```bash
bush-ears benchmark --samples 50000 --iterations 200
```

### Real-time Web Interface
Start the wildlife monitoring dashboard:

```bash
bush-ears monitor
# Or API-only mode: bush-ears monitor --headless
```

## Features

### Wildlife Identification
- **Real-time audio processing** with C++23 features
- **Australian species database** (Kookaburra, Magpie, Galah, Koala, Dingo, etc.)
- **Lightweight ML inference** for species classification
- **Ecosystem health metrics** (biodiversity index, conservation score)

### Performance
- **SIMD-optimized audio processing** in C++
- **Parallel feature extraction** using modern C++ algorithms
- **Real-time capability** for continuous monitoring
- **20-100x speedup** over pure Python implementations

### Scenarios
- **Dawn Chorus**: Mixed bird calls at sunrise
- **Urban Park**: City-adapted species
- **Outback Night**: Nocturnal wildlife sounds  
- **Endangered Habitat**: Conservation focus species

## Architecture

This polyglot application demonstrates C++ + Python integration for AI:

- **C++**: Real-time audio processing, FFT computation, ML inference engine
- **Python**: Ecosystem analysis, CLI interface, web server, data visualization
- **scikit-build-core**: Seamless C++/Python build integration

## Why C++ + Python for Audio AI?

**C++ Advantages:**
- **Real-time audio processing**: 44.1kHz sample rate processing
- **SIMD optimizations**: Vectorized operations for spectral analysis
- **Memory efficiency**: Minimal latency for continuous streams
- **ML inference**: Lightweight neural network execution

**Python Advantages:**
- **Ecosystem integration**: scipy, matplotlib, fastapi
- **Data analysis**: Biodiversity metrics and conservation scoring
- **Rapid development**: CLI interfaces and web APIs
- **Scientific computing**: Integration with research workflows

## Technical Innovation

**Novel Aspects:**
1. **Audio-based ecosystem monitoring** - Most focus on visual AI
2. **Real-time wildlife identification** - Conservation technology
3. **C++23 features** for modern systems programming:
   - `std::expected` for error handling
   - `std::ranges` for data processing
   - `std::execution::par_unseq` for parallel algorithms
   - `std::span` for safe array access

4. **Biodiversity metrics** - Shannon index from audio data
5. **Conservation scoring** - Species importance weighting

## Use Cases

- **Conservation research**: Automated wildlife surveys
- **Ecosystem monitoring**: Real-time biodiversity assessment  
- **Environmental impact**: Pre/post development comparisons
- **Citizen science**: Distributed monitoring networks
- **Education**: Interactive wildlife identification

Perfect example of using C++ for performance-critical AI inference while leveraging Python's rich ecosystem for analysis and integration.
