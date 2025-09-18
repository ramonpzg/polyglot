# Rust Tutorial Part 3: Python Integration and Real-World Applications

*Complete the journey - building production-ready Rust + Python applications with PyO3, performance optimization, and deployment*

## Table of Contents
1. [Python Integration with PyO3](#python-integration-with-pyo3)
2. [Building Python Extensions](#building-python-extensions)
3. [Performance Optimization](#performance-optimization)
4. [Memory Management and Safety](#memory-management-and-safety)
5. [Testing and Debugging](#testing-and-debugging)
6. [Production Deployment](#production-deployment)
7. [Building Our Complete Bushfire System](#building-our-complete-bushfire-system)
8. [When to Use Rust vs Python](#when-to-use-rust-vs-python)

---

## Python Integration with PyO3

PyO3 is like a **universal translator** between Rust and Python. It lets you write Rust code that Python can call as if it were a native Python module.

### Basic PyO3 Setup

First, let's understand the project structure we built in our bushfire simulation:

```toml
# Cargo.toml
[package]
name = "bushfire_sim"
version = "0.1.0"
edition = "2021"

[lib]
name = "_core"  # Python will import this as bushfire_sim._core
crate-type = ["cdylib"]

[dependencies]
pyo3 = { version = "0.22.4", features = ["extension-module", "abi3-py39"] }
rand = "0.8"
rayon = "1.8"
```

### Simple Python Function Exports

```rust
use pyo3::prelude::*;

// Export a simple function to Python
#[pyfunction]
fn calculate_fire_danger(temperature: f64, humidity: f64, wind_speed: f64) -> String {
    if temperature > 40.0 && humidity < 15.0 && wind_speed > 60.0 {
        "CATASTROPHIC".to_string()
    } else if temperature > 35.0 && humidity < 20.0 && wind_speed > 40.0 {
        "EXTREME".to_string()
    } else if temperature > 30.0 && humidity < 25.0 && wind_speed > 30.0 {
        "SEVERE".to_string()
    } else if temperature > 25.0 && humidity < 40.0 && wind_speed > 20.0 {
        "HIGH".to_string()
    } else {
        "MODERATE".to_string()
    }
}

// Export a function that works with Python lists
#[pyfunction]
fn process_temperature_readings(readings: Vec<f64>) -> PyResult<(f64, f64, f64)> {
    if readings.is_empty() {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            "Cannot process empty readings list"
        ));
    }
    
    let sum: f64 = readings.iter().sum();
    let count = readings.len() as f64;
    let average = sum / count;
    
    let min_temp = readings.iter().fold(f64::INFINITY, |acc, &x| acc.min(x));
    let max_temp = readings.iter().fold(f64::NEG_INFINITY, |acc, &x| acc.max(x));
    
    Ok((average, min_temp, max_temp))
}

// Export a function that returns a Python dictionary
#[pyfunction]
fn analyze_weather_conditions(temp: f64, humidity: f64, wind_speed: f64) -> PyResult<PyObject> {
    Python::with_gil(|py| {
        let result = pyo3::types::PyDict::new(py);
        
        result.set_item("temperature_celsius", temp)?;
        result.set_item("temperature_fahrenheit", temp * 9.0 / 5.0 + 32.0)?;
        result.set_item("humidity_percent", humidity)?;
        result.set_item("wind_speed_kmh", wind_speed)?;
        result.set_item("fire_danger", calculate_fire_danger(temp, humidity, wind_speed))?;
        result.set_item("is_dangerous", temp > 35.0 && humidity < 30.0)?;
        
        Ok(result.into())
    })
}

// The Python module definition
#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(calculate_fire_danger, m)?)?;
    m.add_function(wrap_pyfunction!(process_temperature_readings, m)?)?;
    m.add_function(wrap_pyfunction!(analyze_weather_conditions, m)?)?;
    Ok(())
}
```

### Exporting Classes to Python

```rust
use pyo3::prelude::*;
use std::collections::HashMap;

// A Rust struct that Python can use as a class
#[pyclass]
pub struct WeatherStation {
    #[pyo3(get, set)]  // Make these fields accessible from Python
    pub id: String,
    #[pyo3(get, set)]
    pub location: String,
    
    // Private fields (not accessible from Python)
    readings: Vec<WeatherReading>,
    last_update: Option<u64>,
}

#[pyclass]
#[derive(Clone, Debug)]
pub struct WeatherReading {
    #[pyo3(get)]
    pub temperature: f64,
    #[pyo3(get)]
    pub humidity: f64,
    #[pyo3(get)]
    pub wind_speed: f64,
    #[pyo3(get)]
    pub timestamp: u64,
}

#[pymethods]
impl WeatherStation {
    // Constructor (called from Python as WeatherStation(id, location))
    #[new]
    fn new(id: String, location: String) -> Self {
        WeatherStation {
            id,
            location,
            readings: Vec::new(),
            last_update: None,
        }
    }
    
    // Method callable from Python
    fn add_reading(&mut self, temperature: f64, humidity: f64, wind_speed: f64) {
        let reading = WeatherReading {
            temperature,
            humidity,
            wind_speed,
            timestamp: current_timestamp(),
        };
        
        self.readings.push(reading);
        self.last_update = Some(current_timestamp());
    }
    
    // Method that returns Python-compatible data
    fn get_latest_reading(&self) -> Option<WeatherReading> {
        self.readings.last().cloned()
    }
    
    // Method returning Python list
    fn get_all_readings(&self) -> Vec<WeatherReading> {
        self.readings.clone()
    }
    
    // Method with Python keyword arguments
    #[pyo3(signature = (hours_back = 24, include_metadata = true))]
    fn get_recent_readings(&self, hours_back: u64, include_metadata: bool) -> PyResult<Vec<PyObject>> {
        let cutoff_time = current_timestamp() - (hours_back * 3600);
        
        let recent: Vec<_> = self.readings
            .iter()
            .filter(|reading| reading.timestamp >= cutoff_time)
            .collect();
        
        Python::with_gil(|py| {
            let mut result = Vec::new();
            
            for reading in recent {
                if include_metadata {
                    // Return full reading as dictionary
                    let dict = pyo3::types::PyDict::new(py);
                    dict.set_item("temperature", reading.temperature)?;
                    dict.set_item("humidity", reading.humidity)?;
                    dict.set_item("wind_speed", reading.wind_speed)?;
                    dict.set_item("timestamp", reading.timestamp)?;
                    dict.set_item("age_hours", (current_timestamp() - reading.timestamp) / 3600)?;
                    result.push(dict.into());
                } else {
                    // Return just temperature as float
                    result.push(reading.temperature.into_py(py));
                }
            }
            
            Ok(result)
        })
    }
    
    // Property getter (accessed as station.reading_count in Python)
    #[getter]
    fn reading_count(&self) -> usize {
        self.readings.len()
    }
    
    // Property getter with calculation
    #[getter]
    fn average_temperature(&self) -> Option<f64> {
        if self.readings.is_empty() {
            None
        } else {
            let sum: f64 = self.readings.iter().map(|r| r.temperature).sum();
            Some(sum / self.readings.len() as f64)
        }
    }
    
    // String representation for Python
    fn __repr__(&self) -> String {
        format!("WeatherStation(id='{}', location='{}', readings={})",
                self.id, self.location, self.readings.len())
    }
    
    // Support iteration from Python
    fn __iter__(slf: PyRef<'_, Self>) -> PyResult<WeatherStationIterator> {
        Ok(WeatherStationIterator {
            station: slf.into(),
            index: 0,
        })
    }
}

// Iterator support for Python
#[pyclass]
struct WeatherStationIterator {
    station: Py<WeatherStation>,
    index: usize,
}

#[pymethods]
impl WeatherStationIterator {
    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }
    
    fn __next__(&mut self, py: Python) -> Option<WeatherReading> {
        let station = self.station.borrow(py);
        if self.index < station.readings.len() {
            let reading = station.readings[self.index].clone();
            self.index += 1;
            Some(reading)
        } else {
            None
        }
    }
}

fn current_timestamp() -> u64 {
    use std::time::{SystemTime, UNIX_EPOCH};
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs()
}

// Add to module
#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<WeatherStation>()?;
    m.add_class::<WeatherReading>()?;
    // ... other functions
    Ok(())
}
```

### Error Handling Between Rust and Python

```rust
use pyo3::prelude::*;
use pyo3::exceptions::{PyValueError, PyRuntimeError, PyFileNotFoundError};

// Custom error type that converts to Python exceptions
#[derive(Debug)]
enum SimulationError {
    InvalidCoordinates(String),
    ConfigurationError(String),
    FileError(String),
    ComputationError(String),
}

impl From<SimulationError> for PyErr {
    fn from(error: SimulationError) -> PyErr {
        match error {
            SimulationError::InvalidCoordinates(msg) => {
                PyValueError::new_err(format!("Invalid coordinates: {}", msg))
            },
            SimulationError::ConfigurationError(msg) => {
                PyValueError::new_err(format!("Configuration error: {}", msg))
            },
            SimulationError::FileError(msg) => {
                PyFileNotFoundError::new_err(format!("File error: {}", msg))
            },
            SimulationError::ComputationError(msg) => {
                PyRuntimeError::new_err(format!("Computation error: {}", msg))
            },
        }
    }
}

#[pyfunction]
fn risky_operation(value: f64) -> PyResult<f64> {
    if value < 0.0 {
        return Err(SimulationError::InvalidCoordinates(
            "Value must be positive".to_string()
        ).into());
    }
    
    if value > 100.0 {
        return Err(SimulationError::ComputationError(
            "Value too large for computation".to_string()
        ).into());
    }
    
    Ok(value * 2.0)
}

#[pyfunction]
fn process_file_data(filename: String) -> PyResult<Vec<f64>> {
    use std::fs;
    
    // Read file - convert std::io::Error to PyErr
    let contents = fs::read_to_string(&filename)
        .map_err(|_| SimulationError::FileError(format!("Cannot read file: {}", filename)))?;
    
    // Parse each line as f64
    let mut values = Vec::new();
    for (line_num, line) in contents.lines().enumerate() {
        let value = line.trim().parse::<f64>()
            .map_err(|_| SimulationError::ConfigurationError(
                format!("Invalid number on line {}: '{}'", line_num + 1, line)
            ))?;
        values.push(value);
    }
    
    if values.is_empty() {
        return Err(SimulationError::FileError("File is empty".to_string()).into());
    }
    
    Ok(values)
}
```

---

## Building Python Extensions

Let's see how our bushfire simulation integrates with Python, using the same structure as the project we built:

### The Complete Fire Simulation Class

```rust
use pyo3::prelude::*;
use rayon::prelude::*;
use rand::Rng;

#[pyclass]
pub struct FireSimulation {
    width: usize,
    height: usize,
    grid: Vec<Vec<CellState>>,
    wind_speed: f64,
    wind_direction: f64,
    humidity: f64,
    temperature: f64,
    step: u32,
}

#[derive(Clone, Copy, PartialEq)]
enum CellState {
    Empty = 0,
    Vegetation = 1,
    Burning = 2,
    Burnt = 3,
}

impl From<u8> for CellState {
    fn from(value: u8) -> Self {
        match value {
            0 => CellState::Empty,
            1 => CellState::Vegetation,
            2 => CellState::Burning,
            _ => CellState::Burnt,
        }
    }
}

#[pymethods]
impl FireSimulation {
    #[new]
    fn new(
        width: usize,
        height: usize,
        wind_speed: f64,
        wind_direction: f64,
        humidity: f64,
        temperature: f64,
    ) -> Self {
        let mut grid = vec![vec![CellState::Empty; width]; height];
        let mut rng = rand::thread_rng();
        
        // Initialize with vegetation (higher density for better simulation)
        for row in &mut grid {
            for cell in row {
                if rng.gen::<f64>() < 0.85 {
                    *cell = CellState::Vegetation;
                }
            }
        }

        FireSimulation {
            width,
            height,
            grid,
            wind_speed,
            wind_direction,
            humidity,
            temperature,
            step: 0,
        }
    }
    
    fn ignite(&mut self, x: usize, y: usize) -> PyResult<()> {
        if x >= self.width || y >= self.height {
            return Err(PyValueError::new_err(
                format!("Coordinates ({}, {}) out of bounds", x, y)
            ));
        }
        
        if self.grid[y][x] == CellState::Vegetation {
            self.grid[y][x] = CellState::Burning;
            Ok(())
        } else {
            Err(PyValueError::new_err(
                format!("Cannot ignite cell at ({}, {}) - no vegetation", x, y)
            ))
        }
    }
    
    // This is the performance-critical function - Rust shines here
    fn step(&mut self) -> PyResult<()> {
        let mut new_grid = self.grid.clone();
        
        // Process all cells in parallel - this is why we use Rust!
        let updates: Vec<_> = (0..self.height)
            .into_par_iter()
            .flat_map(|y| {
                (0..self.width).into_par_iter().filter_map(move |x| {
                    self.process_cell_static(x, y).map(|new_state| (x, y, new_state))
                })
            })
            .collect();

        // Apply updates atomically
        for (x, y, new_state) in updates {
            new_grid[y][x] = new_state;
        }

        self.grid = new_grid;
        self.step += 1;
        Ok(())
    }
    
    // Return state as flat array for Python
    fn get_state(&self) -> Vec<u8> {
        self.grid
            .iter()
            .flat_map(|row| row.iter().map(|&cell| cell as u8))
            .collect()
    }
    
    // Return statistics tuple for Python
    fn get_stats(&self) -> (u32, u32, u32, u32, u32) {
        let mut counts = [0u32; 4];
        for row in &self.grid {
            for &cell in row {
                counts[cell as usize] += 1;
            }
        }
        (self.step, counts[0], counts[1], counts[2], counts[3])
    }
    
    // Update weather conditions
    fn set_weather(&mut self, wind_speed: f64, wind_direction: f64, humidity: f64, temperature: f64) {
        self.wind_speed = wind_speed;
        self.wind_direction = wind_direction;
        self.humidity = humidity;
        self.temperature = temperature;
    }
}

impl FireSimulation {
    fn process_cell_static(&self, x: usize, y: usize) -> Option<CellState> {
        let current = self.grid[y][x];
        
        match current {
            CellState::Burning => {
                Some(CellState::Burnt)
            }
            CellState::Vegetation => {
                let fire_probability = self.calculate_fire_probability(x, y);
                let mut rng = rand::thread_rng();
                
                if rng.gen::<f64>() < fire_probability {
                    Some(CellState::Burning)
                } else {
                    None
                }
            }
            _ => None,
        }
    }
    
    fn calculate_fire_probability(&self, x: usize, y: usize) -> f64 {
        let burning_neighbors = self.count_burning_neighbors(x, y);
        if burning_neighbors == 0 {
            return 0.0;
        }

        // Base fire spread rate
        let base_rate = 0.35;
        
        // Environmental effects
        let wind_factor = 1.0 + (self.wind_speed / 120.0);
        let humidity_factor = 1.15 - (self.humidity / 100.0);
        let temp_factor = 0.85 + (self.temperature / 120.0);
        let neighbor_factor = burning_neighbors as f64 * 0.45;

        let probability = base_rate * wind_factor * humidity_factor * temp_factor * neighbor_factor;
        
        let max_prob = if self.wind_speed > 65.0 { 0.7 } else { 0.6 };
        probability.min(max_prob)
    }
    
    fn count_burning_neighbors(&self, x: usize, y: usize) -> u8 {
        let mut count = 0;
        
        for dy in -1i32..=1 {
            for dx in -1i32..=1 {
                if dx == 0 && dy == 0 { continue; }
                
                let nx = (x as i32 + dx) as usize;
                let ny = (y as i32 + dy) as usize;
                
                if nx < self.width && ny < self.height {
                    if self.grid[ny][nx] == CellState::Burning {
                        count += 1;
                    }
                }
            }
        }
        
        count
    }
}

// Batch simulation function for performance testing
#[pyfunction]
fn run_batch_simulation(
    width: usize,
    height: usize,
    steps: u32,
    ignition_points: Vec<(usize, usize)>,
    wind_speed: f64,
    humidity: f64,
    temperature: f64,
) -> PyResult<Vec<Vec<u8>>> {
    let mut sim = FireSimulation::new(width, height, wind_speed, 0.0, humidity, temperature);
    
    // Set ignition points
    for (x, y) in ignition_points {
        sim.ignite(x, y)?;
    }
    
    let mut results = Vec::with_capacity(steps as usize);
    results.push(sim.get_state());
    
    // Run simulation steps
    for _ in 0..steps {
        sim.step()?;
        results.push(sim.get_state());
    }
    
    Ok(results)
}
```

### Python Integration Layer

Now let's see how this integrates with Python (this is what goes in your Python `__init__.py`):

```python
# src/bushfire_sim/__init__.py
"""Bushfire Simulation with Rust acceleration."""

from ._core import FireSimulation, run_batch_simulation
import numpy as np
import time
from typing import List, Tuple, Dict, Optional

class BushfireModel:
    """High-level Python interface wrapping the Rust simulation."""
    
    # Australian fire danger ratings
    DANGER_LEVELS = {
        'low': {'wind': 15, 'humidity': 65, 'temp': 25},
        'moderate': {'wind': 20, 'humidity': 50, 'temp': 30},
        'high': {'wind': 30, 'humidity': 35, 'temp': 35},
        'very_high': {'wind': 40, 'humidity': 25, 'temp': 40},
        'severe': {'wind': 50, 'humidity': 15, 'temp': 45},
        'extreme': {'wind': 65, 'humidity': 8, 'temp': 48},
        'catastrophic': {'wind': 80, 'humidity': 5, 'temp': 50},
    }
    
    def __init__(self, width: int = 100, height: int = 100):
        self.width = width
        self.height = height
        self.sim: Optional[FireSimulation] = None
        self.history: List[np.ndarray] = []
    
    def set_conditions(self, danger_level: str = 'moderate', **overrides) -> Dict[str, float]:
        """Set weather conditions based on Australian fire danger ratings."""
        if danger_level not in self.DANGER_LEVELS:
            available = ", ".join(self.DANGER_LEVELS.keys())
            raise ValueError(f"Unknown danger level '{danger_level}'. Available: {available}")
        
        conditions = self.DANGER_LEVELS[danger_level].copy()
        conditions.update(overrides)
        
        # Create the Rust simulation object
        self.sim = FireSimulation(
            self.width,
            self.height,
            conditions['wind'],
            0.0,  # wind direction
            conditions['humidity'],
            conditions['temp']
        )
        
        return conditions
    
    def ignite(self, locations: List[Tuple[int, int]]) -> None:
        """Start fires at specified locations."""
        if not self.sim:
            raise RuntimeError("Must call set_conditions() first")
        
        for x, y in locations:
            try:
                self.sim.ignite(x, y)
            except ValueError as e:
                print(f"Warning: Could not ignite at ({x}, {y}): {e}")
    
    def simulate_steps(self, steps: int, save_history: bool = True) -> List[np.ndarray]:
        """Run simulation for specified number of steps."""
        if not self.sim:
            raise RuntimeError("Must call set_conditions() first")
        
        results = []
        for _ in range(steps):
            state = self.get_state()
            if save_history:
                self.history.append(state)
            results.append(state)
            
            self.sim.step()
        
        return results
    
    def get_state(self) -> np.ndarray:
        """Get current state as 2D numpy array."""
        if not self.sim:
            return np.zeros((self.height, self.width), dtype=np.uint8)
        
        flat_state = self.sim.get_state()
        return np.array(flat_state, dtype=np.uint8).reshape(self.height, self.width)
    
    def get_stats(self) -> Dict[str, float]:
        """Get simulation statistics."""
        if not self.sim:
            return {'step': 0, 'empty': 0, 'vegetation': 0, 'burning': 0, 'burnt': 0}
        
        step, empty, vegetation, burning, burnt = self.sim.get_stats()
        total = empty + vegetation + burning + burnt
        
        return {
            'step': step,
            'empty': empty,
            'vegetation': vegetation,
            'burning': burning,
            'burnt': burnt,
            'fire_spread_pct': (burnt / total * 100) if total > 0 else 0,
            'active_fire_pct': (burning / total * 100) if total > 0 else 0,
        }
    
    def benchmark_rust_vs_python(self, steps: int = 50) -> Dict[str, float]:
        """Compare Rust vs pure Python performance."""
        # Rust implementation (using our fast batch function)
        start_time = time.time()
        rust_results = run_batch_simulation(
            self.width, self.height, steps,
            [(self.width // 2, self.height // 2)],  # Center ignition
            25.0, 40.0, 35.0  # Moderate conditions
        )
        rust_time = time.time() - start_time
        
        # Pure Python implementation (much slower)
        start_time = time.time()
        python_results = self._python_simulation(steps)
        python_time = time.time() - start_time
        
        return {
            'rust_time': rust_time,
            'python_time': python_time,
            'speedup': python_time / rust_time if rust_time > 0 else float('inf'),
            'rust_steps': len(rust_results),
            'python_steps': len(python_results)
        }
    
    def _python_simulation(self, steps: int) -> List[np.ndarray]:
        """Pure Python simulation for benchmarking."""
        # Initialize grid
        grid = np.random.choice([0, 1], size=(self.height, self.width), p=[0.15, 0.85])
        grid[self.height // 2, self.width // 2] = 2  # Start fire
        
        results = []
        for _ in range(steps):
            results.append(grid.copy())
            new_grid = grid.copy()
            
            # Simple fire spread (much slower than Rust)
            for y in range(1, self.height - 1):
                for x in range(1, self.width - 1):
                    if grid[y, x] == 1:  # Vegetation
                        neighbors = grid[y-1:y+2, x-1:x+2]
                        if np.any(neighbors == 2):  # Has burning neighbor
                            if np.random.random() < 0.3:
                                new_grid[y, x] = 2
                    elif grid[y, x] == 2:  # Burning
                        new_grid[y, x] = 3  # Becomes burnt
            
            grid = new_grid
        
        return results
```

---

## Performance Optimization

Understanding **when and why** Rust provides performance benefits is crucial for effective polyglot programming.

### CPU-Bound vs I/O-Bound Operations

```rust
use pyo3::prelude::*;
use std::thread;
use std::time::{Duration, Instant};

#[pyfunction]
fn cpu_intensive_task(iterations: u64) -> u64 {
    // This benefits massively from Rust's performance
    let mut result = 0u64;
    
    for i in 0..iterations {
        // Simulate complex calculation
        result = result.wrapping_add(i * i % 1000);
        
        // Some branching to prevent compiler optimizations
        if result % 1000 == 0 {
            result = result.wrapping_mul(997);
        }
    }
    
    result
}

#[pyfunction]
fn io_bound_task(delay_ms: u64) -> String {
    // This doesn't benefit much from Rust vs Python
    thread::sleep(Duration::from_millis(delay_ms));
    format!("Completed after {}ms", delay_ms)
}

#[pyfunction]
fn parallel_cpu_task(iterations: u64, num_threads: usize) -> u64 {
    use rayon::prelude::*;
    
    // Split work across threads - this is where Rust really shines
    let chunk_size = iterations / num_threads as u64;
    
    (0..num_threads)
        .into_par_iter()
        .map(|thread_id| {
            let start = thread_id as u64 * chunk_size;
            let end = if thread_id == num_threads - 1 {
                iterations  // Last thread handles remainder
            } else {
                start + chunk_size
            };
            
            let mut thread_result = 0u64;
            for i in start..end {
                thread_result = thread_result.wrapping_add(i * i % 1000);
                if thread_result % 1000 == 0 {
                    thread_result = thread_result.wrapping_mul(997);
                }
            }
            
            thread_result
        })
        .sum()
}

// Memory-intensive operations
#[pyfunction]
fn process_large_array(size: usize, operations: u32) -> f64 {
    // Create large array
    let mut data: Vec<f64> = (0..size).map(|i| i as f64).collect();
    
    // Perform multiple passes over the data
    for _ in 0..operations {
        // This kind of operation benefits from Rust's memory layout
        for i in 0..data.len() {
            data[i] = data[i] * 1.001 + 0.1;
            if data[i] > 1000.0 {
                data[i] = data[i] % 1000.0;
            }
        }
    }
    
    // Return summary statistic
    data.iter().sum::<f64>() / data.len() as f64
}

#[pyfunction]
fn benchmark_operation_types() -> PyResult<PyObject> {
    Python::with_gil(|py| {
        let results = pyo3::types::PyDict::new(py);
        
        // CPU-bound benchmark
        let start = Instant::now();
        let cpu_result = cpu_intensive_task(10_000_000);
        let cpu_time = start.elapsed();
        
        results.set_item("cpu_bound", pyo3::types::PyDict::new(py))?;
        let cpu_dict = results.get_item("cpu_bound")?.unwrap().downcast::<pyo3::types::PyDict>()?;
        cpu_dict.set_item("result", cpu_result)?;
        cpu_dict.set_item("time_seconds", cpu_time.as_secs_f64())?;
        
        // I/O-bound benchmark
        let start = Instant::now();
        let io_result = io_bound_task(100);
        let io_time = start.elapsed();
        
        results.set_item("io_bound", pyo3::types::PyDict::new(py))?;
        let io_dict = results.get_item("io_bound")?.unwrap().downcast::<pyo3::types::PyDict>()?;
        io_dict.set_item("result", io_result)?;
        io_dict.set_item("time_seconds", io_time.as_secs_f64())?;
        
        // Parallel CPU benchmark
        let start = Instant::now();
        let parallel_result = parallel_cpu_task(10_000_000, 4);
        let parallel_time = start.elapsed();
        
        results.set_item("parallel_cpu", pyo3::types::PyDict::new(py))?;
        let parallel_dict = results.get_item("parallel_cpu")?.unwrap().downcast::<pyo3::types::PyDict>()?;
        parallel_dict.set_item("result", parallel_result)?;
        parallel_dict.set_item("time_seconds", parallel_time.as_secs_f64())?;
        parallel_dict.set_item("speedup_vs_sequential", cpu_time.as_secs_f64() / parallel_time.as_secs_f64())?;
        
        // Memory-intensive benchmark
        let start = Instant::now();
        let memory_result = process_large_array(1_000_000, 10);
        let memory_time = start.elapsed();
        
        results.set_item("memory_intensive", pyo3::types::PyDict::new(py))?;
        let memory_dict = results.get_item("memory_intensive")?.unwrap().downcast::<pyo3::types::PyDict>()?;
        memory_dict.set_item("result", memory_result)?;
        memory_dict.set_item("time_seconds", memory_time.as_secs_f64())?;
        
        Ok(results.into())
    })
}
```

### Memory-Efficient Data Structures

```rust
use pyo3::prelude::*;

// Efficient grid representation
#[pyclass]
pub struct CompactGrid {
    width: usize,
    height: usize,
    data: Vec<u8>,  // Flat array for cache efficiency
}

#[pymethods]
impl CompactGrid {
    #[new]
    fn new(width: usize, height: usize, initial_value: u8) -> Self {
        CompactGrid {
            width,
            height,
            data: vec![initial_value; width * height],
        }
    }
    
    fn get(&self, x: usize, y: usize) -> PyResult<u8> {
        if x >= self.width || y >= self.height {
            return Err(PyErr::new::<pyo3::exceptions::PyIndexError, _>(
                format!("Index ({}, {}) out of bounds", x, y)
            ));
        }
        Ok(self.data[y * self.width + x])
    }
    
    fn set(&mut self, x: usize, y: usize, value: u8) -> PyResult<()> {
        if x >= self.width || y >= self.height {
            return Err(PyErr::new::<pyo3::exceptions::PyIndexError, _>(
                format!("Index ({}, {}) out of bounds", x, y)
            ));
        }
        self.data[y * self.width + x] = value;
        Ok(())
    }
    
    // Efficient batch operations
    fn fill_region(&mut self, x1: usize, y1: usize, x2: usize, y2: usize, value: u8) -> PyResult<()> {
        if x2 >= self.width || y2 >= self.height {
            return Err(PyErr::new::<pyo3::exceptions::PyIndexError, _>(
                "Region bounds exceed grid size"
            ));
        }
        
        for y in y1..=y2 {
            for x in x1..=x2 {
                self.data[y * self.width + x] = value;
            }
        }
        Ok(())
    }
    
    fn count_value(&self, value: u8) -> usize {
        // This is much faster in Rust than Python
        self.data.iter().filter(|&&v| v == value).count()
    }
    
    // Return data as Python bytes for zero-copy transfer
    fn get_raw_data(&self) -> &[u8] {
        &self.data
    }
    
    // Parallel operations
    fn parallel_transform(&mut self, multiplier: f64) {
        use rayon::prelude::*;
        
        self.data.par_iter_mut().for_each(|cell| {
            let new_value = (*cell as f64 * multiplier) as u8;
            *cell = new_value.min(255);
        });
    }
}

// Memory pool for reducing allocations
#[pyclass]
pub struct GridPool {
    available_grids: Vec<CompactGrid>,
    grid_width: usize,
    grid_height: usize,
}

#[pymethods]
impl GridPool {
    #[new]
    fn new(grid_width: usize, grid_height: usize, initial_pool_size: usize) -> Self {
        let mut available_grids = Vec::with_capacity(initial_pool_size);
        
        for _ in 0..initial_pool_size {
            available_grids.push(CompactGrid::new(grid_width, grid_height, 0));
        }
        
        GridPool {
            available_grids,
            grid_width,
            grid_height,
        }
    }
    
    fn get_grid(&mut self) -> CompactGrid {
        self.available_grids.pop().unwrap_or_else(|| {
            CompactGrid::new(self.grid_width, self.grid_height, 0)
        })
    }
    
    fn return_grid(&mut self, mut grid: CompactGrid) {
        // Reset grid for reuse
        grid.fill_region(0, 0, grid.width - 1, grid.height - 1, 0).unwrap();
        self.available_grids.push(grid);
    }
    
    fn pool_size(&self) -> usize {
        self.available_grids.len()
    }
}
```

---

## Memory Management and Safety

Understanding Rust's memory model helps you write efficient Python extensions.

### Zero-Copy Data Transfer

```rust
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use numpy::{PyArray1, PyArray2};

#[pyclass]
pub struct DataProcessor {
    buffer: Vec<f64>,
    processed_count: usize,
}

#[pymethods]
impl DataProcessor {
    #[new]
    fn new(capacity: usize) -> Self {
        DataProcessor {
            buffer: Vec::with_capacity(capacity),
            processed_count: 0,
        }
    }
    
    // Zero-copy access to internal buffer
    fn get_buffer_view<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyArray1<f64>>> {
        // This creates a view into our Rust data without copying
        Ok(PyArray1::from_slice_bound(py, &self.buffer))
    }
    
    // Accept numpy array without copying
    fn process_numpy_array(&mut self, array: &Bound<'_, PyArray1<f64>>) -> PyResult<f64> {
        let readonly = array.readonly();
        let slice = readonly.as_slice()?;
        
        // Process the data directly from numpy memory
        let sum: f64 = slice.iter().sum();
        let mean = sum / slice.len() as f64;
        
        // Store results in our buffer
        self.buffer.clear();
        for &value in slice {
            if value > mean {
                self.buffer.push(value);
            }
        }
        
        self.processed_count += 1;
        Ok(mean)
    }
    
    // Return results as numpy array (zero-copy when possible)
    fn get_results<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyArray1<f64>>> {
        Ok(PyArray1::from_slice_bound(py, &self.buffer))
    }
    
    // Working with raw bytes
    fn process_raw_bytes(&mut self, data: &[u8]) -> PyResult<Vec<f64>> {
        // Convert bytes to f64 values efficiently
        if data.len() % 8 != 0 {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Data length must be multiple of 8 for f64 conversion"
            ));
        }
        
        let mut results = Vec::with_capacity(data.len() / 8);
        
        for chunk in data.chunks_exact(8) {
            let bytes: [u8; 8] = chunk.try_into().unwrap();
            let value = f64::from_le_bytes(bytes);
            results.push(value * 2.0);  // Some processing
        }
        
        Ok(results)
    }
}

// Efficient string processing
#[pyfunction]
fn process_text_efficiently(text: &str) -> PyResult<PyObject> {
    Python::with_gil(|py| {
        // Process text without unnecessary copying
        let word_count = text.split_whitespace().count();
        let char_count = text.chars().count();
        let line_count = text.lines().count();
        
        // Find longest word efficiently
        let longest_word = text
            .split_whitespace()
            .max_by_key(|word| word.len())
            .unwrap_or("")
            .to_string();
        
        let result = pyo3::types::PyDict::new_bound(py);
        result.set_item("word_count", word_count)?;
        result.set_item("char_count", char_count)?;
        result.set_item("line_count", line_count)?;
        result.set_item("longest_word", longest_word)?;
        
        Ok(result.into())
    })
}
```

### Safe Concurrency

```rust
use pyo3::prelude::*;
use std::sync::{Arc, Mutex};
use std::thread;

// Thread-safe shared state
#[pyclass]
pub struct SharedCounter {
    inner: Arc<Mutex<u64>>,
}

#[pymethods]
impl SharedCounter {
    #[new]
    fn new() -> Self {
        SharedCounter {
            inner: Arc::new(Mutex::new(0)),
        }
    }
    
    fn increment(&self) -> PyResult<u64> {
        let mut counter = self.inner.lock().unwrap();
        *counter += 1;
        Ok(*counter)
    }
    
    fn get_value(&self) -> PyResult<u64> {
        let counter = self.inner.lock().unwrap();
        Ok(*counter)
    }
    
    fn parallel_increment(&self, num_threads: usize, increments_per_thread: usize) -> PyResult<u64> {
        let mut handles = Vec::new();
        
        for _ in 0..num_threads {
            let counter_clone = Arc::clone(&self.inner);
            
            let handle = thread::spawn(move || {
                for _ in 0..increments_per_thread {
                    let mut counter = counter_clone.lock().unwrap();
                    *counter += 1;
                }
            });
            
            handles.push(handle);
        }
        
        // Wait for all threads
        for handle in handles {
            handle.join().unwrap();
        }
        
        let counter = self.inner.lock().unwrap();
        Ok(*counter)
    }
}

// Safe parallel data processing
#[pyfunction]
fn parallel_process_data(data: Vec<f64>, num_threads: usize) -> PyResult<Vec<f64>> {
    use rayon::prelude::*;
    
    if num_threads > 0 {
        rayon::ThreadPoolBuilder::new()
            .num_threads(num_threads)
            .build()
            .unwrap()
            .install(|| {
                // Parallel processing with specified thread count
                Ok(data
                    .into_par_iter()
                    .map(|x| x * x + 1.0)
                    .collect())
            })
    } else {
        // Sequential processing
        Ok(data.into_iter().map(|x| x * x + 1.0).collect())
    }
}
```

---

## Testing and Debugging

Testing Rust extensions requires strategies for both Rust and Python sides.

### Rust Unit Tests

```rust
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_fire_simulation_creation() {
        let sim = FireSimulation::new(10, 10, 25.0, 0.0, 45.0, 35.0);
        let (step, empty, vegetation, burning, burnt) = sim.get_stats();
        
        assert_eq!(step, 0);
        assert!(vegetation > 50); // Should have mostly vegetation
        assert_eq!(burning, 0);   // No fires initially
        assert_eq!(burnt, 0);     // Nothing burnt initially
    }
    
    #[test]
    fn test_ignition() {
        let mut sim = FireSimulation::new(10, 10, 25.0, 0.0, 45.0, 35.0);
        
        // Should be able to ignite vegetation
        let result = sim.ignite(5, 5);
        assert!(result.is_ok());
        
        let (_, _, _, burning, _) = sim.get_stats();
        assert_eq!(burning, 1);
    }
    
    #[test]
    fn test_fire_spread() {
        let mut sim = FireSimulation::new(5, 5, 80.0, 0.0, 5.0, 50.0); // Extreme conditions
        
        // Fill with vegetation for predictable test
        for y in 0..5 {
            for x in 0..5 {
                sim.grid[y][x] = CellState::Vegetation;
            }
        }
        
        sim.ignite(2, 2).unwrap(); // Center
        
        // Run several steps
        for _ in 0..5 {
            sim.step().unwrap();
        }
        
        let (_, _, _, burning, burnt) = sim.get_stats();
        assert!(burning + burnt > 1); // Fire should have spread
    }
    
    #[test]
    fn test_performance_benchmark() {
        use std::time::Instant;
        
        let start = Instant::now();
        let mut sim = FireSimulation::new(100, 100, 45.0, 0.0, 20.0, 40.0);
        sim.ignite(50, 50).unwrap();
        
        for _ in 0..50 {
            sim.step().unwrap();
        }
        
        let duration = start.elapsed();
        println!("100x100 grid, 50 steps took: {:?}", duration);
        
        // Should complete reasonably quickly
        assert!(duration.as_millis() < 1000); // Less than 1 second
    }
}

// Benchmark tests (require cargo bench)
#[cfg(test)]
mod benchmarks {
    use super::*;
    
    #[bench]
    fn bench_simulation_step(b: &mut test::Bencher) {
        let mut sim = FireSimulation::new(50, 50, 35.0, 0.0, 25.0, 38.0);
        sim.ignite(25, 25).unwrap();
        
        b.iter(|| {
            sim.step().unwrap();
        });
    }
    
    #[bench]
    fn bench_fire_probability_calculation(b: &mut test::Bencher) {
        let sim = FireSimulation::new(50, 50, 35.0, 0.0, 25.0, 38.0);
        
        b.iter(|| {
            sim.calculate_fire_probability(25, 25);
        });
    }
}
```

### Python Integration Tests

```python
# tests/test_integration.py
import pytest
import numpy as np
import time
from bushfire_sim import BushfireModel, FireSimulation, run_batch_simulation

class TestBushfireIntegration:
    
    def test_model_initialization(self):
        """Test that the Python wrapper initializes correctly."""
        model = BushfireModel(50, 50)
        conditions = model.set_conditions('moderate')
        
        assert 'wind' in conditions
        assert 'humidity' in conditions
        assert 'temp' in conditions
        
        # Should be able to get initial state
        state = model.get_state()
        assert state.shape == (50, 50)
        assert state.dtype == np.uint8
    
    def test_fire_ignition_and_spread(self):
        """Test that fires can be ignited and spread."""
        model = BushfireModel(20, 20)
        model.set_conditions('severe')  # High spread conditions
        
        # Ignite fire at center
        model.ignite([(10, 10)])
        
        # Get initial stats
        initial_stats = model.get_stats()
        assert initial_stats['burning'] > 0
        
        # Run simulation
        results = model.simulate_steps(10)
        assert len(results) == 10
        
        # Fire should have spread
        final_stats = model.get_stats()
        assert final_stats['fire_spread_pct'] > 0
    
    def test_different_danger_levels(self):
        """Test that different danger levels produce different spread rates."""
        results = {}
        
        for danger_level in ['moderate', 'high', 'severe', 'extreme']:
            model = BushfireModel(30, 30)
            model.set_conditions(danger_level)
            model.ignite([(15, 15)])
            
            # Run for same number of steps
            model.simulate_steps(15)
            stats = model.get_stats()
            results[danger_level] = stats['fire_spread_pct']
        
        # Higher danger levels should generally spread more
        assert results['moderate'] <= results['high']
        assert results['high'] <= results['severe']
        # (Note: randomness might make this occasionally fail)
    
    def test_performance_comparison(self):
        """Test that Rust is significantly faster than Python."""
        model = BushfireModel(100, 100)
        model.set_conditions('high')
        
        benchmark_results = model.benchmark_rust_vs_python(30)
        
        assert benchmark_results['speedup'] > 5  # At least 5x faster
        assert benchmark_results['rust_time'] < benchmark_results['python_time']
        
        print(f"Rust vs Python speedup: {benchmark_results['speedup']:.1f}x")
    
    def test_batch_simulation_function(self):
        """Test the direct batch simulation function."""
        results = run_batch_simulation(
            width=25, 
            height=25, 
            steps=10,
            ignition_points=[(12, 12)],
            wind_speed=40.0,
            humidity=20.0,
            temperature=40.0
        )
        
        assert len(results) == 11  # Initial state + 10 steps
        assert all(len(step) == 25 * 25 for step in results)
        
        # First step should have at least one fire
        first_step = np.array(results[0]).reshape(25, 25)
        assert np.any(first_step == 2)  # CellState::Burning
    
    def test_error_handling(self):
        """Test that errors are properly handled."""
        model = BushfireModel(10, 10)
        
        # Should raise error if no conditions set
        with pytest.raises(RuntimeError):
            model.simulate_steps(5)
        
        # Set conditions
        model.set_conditions('moderate')
        
        # Should handle out of bounds ignition gracefully
        with pytest.warns():  # Our code prints warnings for failed ignitions
            model.ignite([(15, 15)])  # Out of bounds
    
    def test_memory_usage(self):
        """Test that memory usage is reasonable."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create and run a large simulation
        model = BushfireModel(200, 200)
        model.set_conditions('extreme')
        model.ignite([(100, 100)])
        
        # Run simulation
        for _ in range(50):
            model.simulate_steps(1, save_history=False)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024
        
        print(f"Memory increase: {memory_increase / 1024 / 1024:.1f} MB")

def test_direct_rust_simulation():
    """Test the Rust simulation directly."""
    sim = FireSimulation(20, 20, 35.0, 0.0, 30.0, 35.0)
    
    # Should be able to ignite
    sim.ignite(10, 10)
    
    # Get initial state
    step, empty, vegetation, burning, burnt = sim.get_stats()
    assert step == 0
    assert burning == 1
    
    # Run a step
    sim.step()
    
    # Check that step counter increased
    step, empty, vegetation, burning, burnt = sim.get_stats()
    assert step == 1
    
    # Fire should have either spread or burnt out
    assert burning >= 0  # Could be 0 if fire burnt out
    assert burnt >= 1    # Original fire should be burnt

if __name__ == "__main__":
    pytest.main([__file__])
```

---

## Production Deployment

### Building and Distribution

```toml
# pyproject.toml for production
[build-system]
requires = ["maturin>=1.0,<2.0"]
build-backend = "maturin"

[project]
name = "bushfire-sim"
version = "0.1.0"
description = "High-performance bushfire simulation with Rust acceleration"
authors = [{name = "Your Name", email = "your.email@example.com"}]
dependencies = [
    "numpy>=1.21.0",
    "matplotlib>=3.5.0",
    "click>=8.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=6.0",
    "maturin>=1.0",
    "black",
    "ruff",
    "mypy",
]
web = [
    "fastapi>=0.68.0",
    "uvicorn>=0.15.0",
    "websockets>=10.0",
]

[project.scripts]
bushfire-sim = "bushfire_sim.cli:main"

[tool.maturin]
module-name = "bushfire_sim._core"
python-packages = ["bushfire_sim"]
python-source = "src"

# Release optimizations
[profile.release]
opt-level = 3
lto = true
codegen-units = 1
panic = "abort"
```

### Performance Monitoring

```rust
use pyo3::prelude::*;
use std::time::Instant;
use std::collections::HashMap;

// Performance monitoring utilities
#[pyclass]
pub struct PerformanceMonitor {
    timings: HashMap<String, Vec<f64>>,
    counters: HashMap<String, u64>,
}

#[pymethods]
impl PerformanceMonitor {
    #[new]
    fn new() -> Self {
        PerformanceMonitor {
            timings: HashMap::new(),
            counters: HashMap::new(),
        }
    }
    
    fn start_timer(&self, name: &str) -> PerformanceTimer {
        PerformanceTimer {
            name: name.to_string(),
            start_time: Instant::now(),
        }
    }
    
    fn record_timing(&mut self, name: String, duration_seconds: f64) {
        self.timings.entry(name).or_insert_with(Vec::new).push(duration_seconds);
    }
    
    fn increment_counter(&mut self, name: &str) {
        *self.counters.entry(name.to_string()).or_insert(0) += 1;
    }
    
    fn get_statistics(&self) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            let result = pyo3::types::PyDict::new(py);
            
            // Timing statistics
            let timings_dict = pyo3::types::PyDict::new(py);
            for (name, times) in &self.timings {
                if !times.is_empty() {
                    let stats = pyo3::types::PyDict::new(py);
                    let sum: f64 = times.iter().sum();
                    let count = times.len() as f64;
                    
                    stats.set_item("count", count)?;
                    stats.set_item("total_seconds", sum)?;
                    stats.set_item("average_seconds", sum / count)?;
                    stats.set_item("min_seconds", times.iter().fold(f64::INFINITY, |a, &b| a.min(b)))?;
                    stats.set_item("max_seconds", times.iter().fold(f64::NEG_INFINITY, |a, &b| a.max(b)))?;
                    
                    timings_dict.set_item(name, stats)?;
                }
            }
            result.set_item("timings", timings_dict)?;
            
            // Counter statistics  
            let counters_dict = pyo3::types::PyDict::new(py);
            for (name, count) in &self.counters {
                counters_dict.set_item(name, count)?;
            }
            result.set_item("counters", counters_dict)?;
            
            Ok(result.into())
        })
    }
    
    fn reset(&mut self) {
        self.timings.clear();
        self.counters.clear();
    }
}

#[pyclass]
pub struct PerformanceTimer {
    name: String,
    start_time: Instant,
}

#[pymethods]
impl PerformanceTimer {
    fn stop(&self, monitor: &mut PerformanceMonitor) {
        let duration = self.start_time.elapsed();
        monitor.record_timing(self.name.clone(), duration.as_secs_f64());
    }
    
    fn elapsed_seconds(&self) -> f64 {
        self.start_time.elapsed().as_secs_f64()
    }
}

// Memory usage monitoring
#[pyfunction]
fn get_memory_usage() -> PyResult<PyObject> {
    Python::with_gil(|py| {
        let result = pyo3::types::PyDict::new(py);
        
        // Get basic memory info (platform-specific)
        #[cfg(unix)]
        {
            use std::fs;
            if let Ok(status) = fs::read_to_string("/proc/self/status") {
                for line in status.lines() {
                    if line.starts_with("VmRSS:") {
                        if let Some(kb_str) = line.split_whitespace().nth(1) {
                            if let Ok(kb) = kb_str.parse::<u64>() {
                                result.set_item("rss_bytes", kb * 1024)?;
                            }
                        }
                    } else if line.starts_with("VmSize:") {
                        if let Some(kb_str) = line.split_whitespace().nth(1) {
                            if let Ok(kb) = kb_str.parse::<u64>() {
                                result.set_item("virtual_bytes", kb * 1024)?;
                            }
                        }
                    }
                }
            }
        }
        
        Ok(result.into())
    })
}
```

---

## Building Our Complete Bushfire System

Let's bring together everything into a production-ready system:

```python
# src/bushfire_sim/production.py
"""Production-ready bushfire simulation system."""

import logging
import asyncio
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import numpy as np

from ._core import FireSimulation, PerformanceMonitor

@dataclass
class SimulationConfig:
    """Configuration for a bushfire simulation."""
    width: int = 100
    height: int = 100
    wind_speed: float = 25.0
    wind_direction: float = 0.0
    humidity: float = 45.0
    temperature: float = 32.0
    ignition_points: List[tuple] = None
    max_steps: int = 100
    save_interval: int = 10

class ProductionFireSimulation:
    """Production-ready fire simulation with monitoring and error handling."""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.sim: Optional[FireSimulation] = None
        self.monitor = PerformanceMonitor()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.is_running = False
        self.current_step = 0
        
        # Initialize simulation
        self._initialize_simulation()
    
    def _initialize_simulation(self):
        """Initialize the Rust simulation with error handling."""
        try:
            timer = self.monitor.start_timer("simulation_init")
            self.sim = FireSimulation(
                self.config.width,
                self.config.height,
                self.config.wind_speed,
                self.config.wind_direction,
                self.config.humidity,
                self.config.temperature,
            )
            timer.stop(self.monitor)
            self.logger.info(f"Initialized simulation: {self.config.width}x{self.config.height}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize simulation: {e}")
            raise
    
    def set_ignition_points(self, points: List[tuple]) -> int:
        """Set ignition points and return number successfully ignited."""
        if not self.sim:
            raise RuntimeError("Simulation not initialized")
        
        successful = 0
        for x, y in points:
            try:
                self.sim.ignite(x, y)
                successful += 1
                self.monitor.increment_counter("ignitions_successful")
            except Exception as e:
                self.logger.warning(f"Failed to ignite at ({x}, {y}): {e}")
                self.monitor.increment_counter("ignitions_failed")
        
        self.logger.info(f"Ignited {successful}/{len(points)} points")
        return successful
    
    def run_simulation(self, 
                      steps: Optional[int] = None,
                      progress_callback: Optional[Callable[[int, dict], None]] = None) -> Dict:
        """Run the simulation with monitoring and callbacks."""
        if not self.sim:
            raise RuntimeError("Simulation not initialized")
        
        max_steps = steps or self.config.max_steps
        self.is_running = True
        results = {
            'steps_completed': 0,
            'final_stats': None,
            'performance': None,
            'errors': []
        }
        
        try:
            self.logger.info(f"Starting simulation for {max_steps} steps")
            
            for step in range(max_steps):
                if not self.is_running:
                    self.logger.info("Simulation stopped by user")
                    break
                
                # Run simulation step with timing
                timer = self.monitor.start_timer("simulation_step")
                try:
                    self.sim.step()
                    self.current_step += 1
                    self.monitor.increment_counter("steps_successful")
                except Exception as e:
                    self.logger.error(f"Step {step} failed: {e}")
                    results['errors'].append(f"Step {step}: {e}")
                    self.monitor.increment_counter("steps_failed")
                    break
                finally:
                    timer.stop(self.monitor)
                
                # Progress reporting
                if progress_callback and (step % self.config.save_interval == 0):
                    stats = self._get_current_stats()
                    progress_callback(step, stats)
                
                # Check for completion (no more fires)
                if step > 0:
                    _, _, _, burning, _ = self.sim.get_stats()
                    if burning == 0:
                        self.logger.info(f"Simulation completed - no active fires at step {step}")
                        break
            
            results['steps_completed'] = self.current_step
            results['final_stats'] = self._get_current_stats()
            results['performance'] = self.monitor.get_statistics()
            
            self.logger.info(f"Simulation completed: {self.current_step} steps")
            
        except Exception as e:
            self.logger.error(f"Simulation failed: {e}")
            results['errors'].append(f"Fatal error: {e}")
            raise
        finally:
            self.is_running = False
        
        return results
    
    def _get_current_stats(self) -> Dict:
        """Get current simulation statistics."""
        if not self.sim:
            return {}
        
        step, empty, vegetation, burning, burnt = self.sim.get_stats()
        total = empty + vegetation + burning + burnt
        
        return {
            'step': step,
            'empty': empty,
            'vegetation': vegetation,
            'burning': burning,
            'burnt': burnt,
            'total_cells': total,
            'fire_spread_pct': (burnt / total * 100) if total > 0 else 0,
            'active_fire_pct': (burning / total * 100) if total > 0 else 0,
        }
    
    def get_grid_state(self) -> Optional[np.ndarray]:
        """Get current grid state as numpy array."""
        if not self.sim:
            return None
        
        flat_state = self.sim.get_state()
        return np.array(flat_state, dtype=np.uint8).reshape(self.config.height, self.config.width)
    
    def stop_simulation(self):
        """Stop the running simulation."""
        self.is_running = False
        self.logger.info("Simulation stop requested")
    
    def get_performance_report(self) -> Dict:
        """Get detailed performance report."""
        return self.monitor.get_statistics()
    
    def reset(self):
        """Reset simulation to initial state."""
        self._initialize_simulation()
        self.monitor.reset()
        self.current_step = 0
        self.logger.info("Simulation reset")

# Async wrapper for concurrent simulations
class AsyncFireSimulationManager:
    """Manage multiple concurrent fire simulations."""
    
    def __init__(self, max_concurrent: int = 4):
        self.max_concurrent = max_concurrent
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)
        self.active_simulations: Dict[str, ProductionFireSimulation] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def run_simulation_async(self, 
                                   simulation_id: str,
                                   config: SimulationConfig,
                                   ignition_points: List[tuple],
                                   progress_callback: Optional[Callable] = None) -> Dict:
        """Run a simulation asynchronously."""
        self.logger.info(f"Starting async simulation: {simulation_id}")
        
        # Create simulation
        sim = ProductionFireSimulation(config)
        self.active_simulations[simulation_id] = sim
        
        try:
            # Set ignition points
            sim.set_ignition_points(ignition_points)
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                sim.run_simulation,
                None,
                progress_callback
            )
            
            self.logger.info(f"Completed async simulation: {simulation_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Async simulation {simulation_id} failed: {e}")
            raise
        finally:
            # Clean up
            if simulation_id in self.active_simulations:
                del self.active_simulations[simulation_id]
    
    def get_simulation_status(self, simulation_id: str) -> Optional[Dict]:
        """Get status of running simulation."""
        sim = self.active_simulations.get(simulation_id)
        if sim:
            return {
                'is_running': sim.is_running,
                'current_step': sim.current_step,
                'config': sim.config,
                'stats': sim._get_current_stats()
            }
        return None
    
    def stop_simulation(self, simulation_id: str) -> bool:
        """Stop a specific simulation."""
        sim = self.active_simulations.get(simulation_id)
        if sim:
            sim.stop_simulation()
            return True
        return False
    
    def get_all_active(self) -> List[str]:
        """Get list of active simulation IDs."""
        return list(self.active_simulations.keys())
    
    async def shutdown(self):
        """Shutdown all simulations and cleanup."""
        self.logger.info("Shutting down simulation manager")
        
        # Stop all active simulations
        for sim_id in list(self.active_simulations.keys()):
            self.stop_simulation(sim_id)
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
```

---

## When to Use Rust vs Python

Understanding **when** to reach for Rust is crucial for effective polyglot programming:

### Use Rust When:

1. **CPU-Intensive Computation**
   ```rust
   // Cellular automata, physics simulations, mathematical modeling
   fn intensive_computation(data: &[f64]) -> f64 {
       data.par_iter()           // Parallel processing
           .map(|&x| expensive_calculation(x))
           .sum()
   }
   ```

2. **Memory-Critical Applications**
   ```rust
   // Large datasets, real-time systems, embedded applications
   struct CompactData {
       values: Vec<u8>,    // Minimal memory footprint
       indices: Vec<u16>,  // Specific sized integers
   }
   ```

3. **Parallel Processing Beyond GIL**
   ```rust
   // True parallelism for CPU-bound tasks
   (0..data.len())
       .into_par_iter()
       .map(|i| process_item(&data[i]))
       .collect()
   ```

4. **Safety-Critical Code**
   ```rust
   // Memory safety guaranteed at compile time
   fn safe_buffer_access(buffer: &mut [u8], index: usize) -> Option<&mut u8> {
       buffer.get_mut(index)  // Bounds-checked access
   }
   ```

### Keep Using Python For:

1. **I/O-Bound Operations** - Network requests, file operations, database queries
2. **Prototyping and Experimentation** - Rapid development and iteration
3. **Data Science Workflows** - pandas, scikit-learn, matplotlib ecosystem
4. **Business Logic** - Complex rules, decision trees, workflow management
5. **Integration and Orchestration** - Connecting different systems and services

### The Sweet Spot Pattern:

```python
# Python: High-level orchestration and I/O
def analyze_bushfire_risk(region_data, weather_conditions):
    # Python handles data loading, validation, coordination
    historical_data = load_from_database(region_data.id)
    processed_conditions = validate_weather_data(weather_conditions)
    
    # Rust: Intensive computation
    risk_scores = compute_risk_matrix(
        historical_data.vegetation_map,
        processed_conditions,
        simulation_parameters
    )
    
    # Python: Results processing and presentation
    risk_report = generate_report(risk_scores)
    save_to_database(risk_report)
    send_alerts_if_needed(risk_report)
    
    return risk_report
```

---

## Key Takeaways - Part 3

**PyO3 Integration:**
- Use `#[pyclass]` for stateful objects, `#[pyfunction]` for utilities
- Handle errors properly with custom error types that convert to Python exceptions
- Leverage zero-copy data transfer with numpy integration

**Performance Optimization:**
- Profile first - don't optimize without evidence
- Rust shines for CPU-bound, parallel, and memory-intensive operations
- Use Rayon for parallel processing that bypasses Python's GIL

**Memory Management:**
- Rust's ownership system prevents entire categories of bugs
- Use Arc/Mutex sparingly - prefer message passing when possible
- Design APIs to minimize data copying between Rust and Python

**Production Readiness:**
- Include comprehensive error handling and logging
- Monitor performance with built-in metrics
- Design for testability from both Rust and Python sides
- Plan for concurrent usage patterns

**Sensible Defaults:**
- Use Rust for the performance-critical core, Python for everything else
- Keep the Rust API simple and Pythonic
- Include benchmarking capabilities to demonstrate value
- Design for maintainability - not every optimization is worth the complexity
- Document the performance characteristics clearly

The **key insight** is that successful polyglot programming requires **clear boundaries** between languages. Use each language for what it does best, design clean interfaces between them, and always measure the performance gains to ensure the added complexity is worthwhile.

Rust + Python gives you the best of both worlds: **Python's productivity and ecosystem** with **Rust's performance and safety** exactly where you need it most.
