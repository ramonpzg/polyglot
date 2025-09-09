# Bushfire Simulation

Real-time bushfire spread modeling with Rust acceleration for Australian conditions.

## Installation

```bash
pip install bushfire-sim
```

## Usage

### CLI Simulation
Run a basic simulation with visualization:
```bash
bushfire-sim simulate --danger severe --show
```

### Performance Benchmark
Compare Rust vs Python performance:
```bash
bushfire-sim benchmark --size 100 --steps 50
```

### Real-time Web Interface
Start interactive web dashboard:
```bash
bushfire-sim serve
```

## Features

- **Rust-accelerated fire spread modeling** using cellular automata
- **Australian fire danger ratings** (low to catastrophic)
- **Real-time visualization** with matplotlib and web interface
- **Performance benchmarking** showing 10-100x speedup over pure Python
- **Realistic fire behavior** modeling wind, humidity, and temperature effects

## Architecture

This is a polyglot application demonstrating Python + Rust integration:

- **Rust**: High-performance cellular automata simulation, parallel processing with Rayon
- **Python**: High-level interface, visualization, CLI, web server
- **maturin**: Build system for seamless Python-Rust integration

Perfect example of using Rust for computational bottlenecks while keeping Python's ease of use.

## Why Rust + Python?

Bushfire modeling requires processing thousands of cells per simulation step. Pure Python would be too slow for real-time applications. Rust provides:

- **100x+ performance** improvement over pure Python
- **Memory safety** for long-running simulations  
- **Parallel processing** with Rayon for multi-core utilization
- **Zero-cost abstractions** for optimal performance

Python provides the ergonomic API, visualization, and integration ecosystem.
