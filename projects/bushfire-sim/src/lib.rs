use pyo3::prelude::*;
use rayon::prelude::*;
use rand::Rng;

/// Cell states in the bushfire simulation
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

/// Bushfire simulation engine using cellular automata
#[pyclass]
pub struct FireSimulation {
    width: usize,
    height: usize,
    grid: Vec<Vec<CellState>>,
    wind_speed: f64,
    wind_direction: f64, // radians
    humidity: f64,
    temperature: f64,
    step: u32,
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
        
        // Initialize with random vegetation (higher density for better spread)
        let mut rng = rand::thread_rng();
        for row in &mut grid {
            for cell in row {
                if rng.gen::<f64>() < 0.85 {  // Higher vegetation density
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

    /// Start a fire at specified coordinates
    fn ignite(&mut self, x: usize, y: usize) -> PyResult<()> {
        if x < self.width && y < self.height {
            if self.grid[y][x] == CellState::Vegetation {
                self.grid[y][x] = CellState::Burning;
            }
        }
        Ok(())
    }

    /// Run one simulation step - this is where Rust shines with performance
    fn step(&mut self) -> PyResult<()> {
        let mut new_grid = self.grid.clone();
        
        // Capture needed values for parallel processing
        let width = self.width;
        let height = self.height;
        let grid = &self.grid;
        let wind_speed = self.wind_speed;
        let humidity = self.humidity;
        let temperature = self.temperature;
        
        // Process all cells in parallel using Rayon
        let updates: Vec<_> = (0..height)
            .into_par_iter()
            .flat_map(|y| {
                (0..width).into_par_iter().filter_map(move |x| {
                    process_cell_static(grid, x, y, width, height, wind_speed, humidity, temperature)
                        .map(|new_state| (x, y, new_state))
                })
            })
            .collect();

        // Apply updates
        for (x, y, new_state) in updates {
            new_grid[y][x] = new_state;
        }

        self.grid = new_grid;
        self.step += 1;
        Ok(())
    }

    /// Get current grid state as flat array for Python
    fn get_state(&self) -> Vec<u8> {
        self.grid
            .iter()
            .flat_map(|row| row.iter().map(|&cell| cell as u8))
            .collect()
    }

    /// Get simulation statistics
    fn get_stats(&self) -> (u32, u32, u32, u32, u32) {
        let mut counts = [0u32; 4];
        for row in &self.grid {
            for &cell in row {
                counts[cell as usize] += 1;
            }
        }
        (self.step, counts[0], counts[1], counts[2], counts[3])
    }

    /// Set weather conditions
    fn set_weather(&mut self, wind_speed: f64, wind_direction: f64, humidity: f64, temperature: f64) {
        self.wind_speed = wind_speed;
        self.wind_direction = wind_direction;
        self.humidity = humidity;
        self.temperature = temperature;
    }
}

/// Static version of process_cell for parallel processing
fn process_cell_static(
    grid: &Vec<Vec<CellState>>, 
    x: usize, 
    y: usize, 
    width: usize, 
    height: usize,
    wind_speed: f64,
    humidity: f64,
    temperature: f64
) -> Option<CellState> {
    let current = grid[y][x];
    
    match current {
        CellState::Burning => {
            // Burning cells become burnt
            Some(CellState::Burnt)
        }
        CellState::Vegetation => {
            // Check if vegetation should catch fire
            let fire_probability = calculate_fire_probability_static(
                grid, x, y, width, height, wind_speed, humidity, temperature
            );
            let mut rng = rand::thread_rng();
            
            if rng.gen::<f64>() < fire_probability {
                Some(CellState::Burning)
            } else {
                None
            }
        }
        _ => None, // Empty and Burnt cells don't change
    }
}

/// Static version of calculate_fire_probability
fn calculate_fire_probability_static(
    grid: &Vec<Vec<CellState>>, 
    x: usize, 
    y: usize, 
    width: usize, 
    height: usize,
    wind_speed: f64,
    humidity: f64,
    temperature: f64
) -> f64 {
    // Count burning neighbors
    let burning_neighbors = count_burning_neighbors_static(grid, x, y, width, height);
    if burning_neighbors == 0 {
        return 0.0;
    }

    // Balanced base rate
    let base_rate = 0.35;
    
    // Moderate wind effect
    let wind_factor = 1.0 + (wind_speed / 120.0);
    
    // Balanced humidity effect
    let humidity_factor = 1.15 - (humidity / 100.0);
    
    // Moderate temperature effect
    let temp_factor = 0.85 + (temperature / 120.0);
    
    // Good neighbor effect
    let neighbor_factor = burning_neighbors as f64 * 0.45;

    let probability = base_rate * wind_factor * humidity_factor * temp_factor * neighbor_factor;
    
    // Balanced caps for controlled but visible spread
    let max_prob = if wind_speed > 65.0 { 0.7 } else { 0.6 };
    probability.min(max_prob)
}

fn count_burning_neighbors_static(
    grid: &Vec<Vec<CellState>>, 
    x: usize, 
    y: usize, 
    width: usize, 
    height: usize
) -> u8 {
    let mut count = 0;
    
    for dy in -1i32..=1 {
        for dx in -1i32..=1 {
            if dx == 0 && dy == 0 {
                continue;
            }
            
            let nx = (x as i32 + dx) as usize;
            let ny = (y as i32 + dy) as usize;
            
            if nx < width && ny < height {
                if grid[ny][nx] == CellState::Burning {
                    count += 1;
                }
            }
        }
    }
    
    count
}

impl FireSimulation {
    /// Process a single cell - core fire spread logic
    fn process_cell(&self, x: usize, y: usize) -> Option<CellState> {
        let current = self.grid[y][x];
        
        match current {
            CellState::Burning => {
                // Burning cells become burnt
                Some(CellState::Burnt)
            }
            CellState::Vegetation => {
                // Check if vegetation should catch fire
                let fire_probability = self.calculate_fire_probability(x, y);
                let mut rng = rand::thread_rng();
                
                if rng.gen::<f64>() < fire_probability {
                    Some(CellState::Burning)
                } else {
                    None
                }
            }
            _ => None, // Empty and Burnt cells don't change
        }
    }

    /// Calculate fire spread probability based on Australian fire behavior
    fn calculate_fire_probability(&self, x: usize, y: usize) -> f64 {
        let mut probability = 0.0;
        
        // Count burning neighbors
        let burning_neighbors = self.count_burning_neighbors(x, y);
        if burning_neighbors == 0 {
            return 0.0;
        }

        // Balanced base rate
        let base_rate = 0.35;
        
        // Moderate wind effect
        let wind_factor = 1.0 + (self.wind_speed / 120.0);
        
        // Balanced humidity effect
        let humidity_factor = 1.15 - (self.humidity / 100.0);
        
        // Moderate temperature effect
        let temp_factor = 0.85 + (self.temperature / 120.0);
        
        // Good neighbor effect
        let neighbor_factor = burning_neighbors as f64 * 0.45;

        probability = base_rate * wind_factor * humidity_factor * temp_factor * neighbor_factor;
        
        // Balanced caps for controlled but visible spread
        let max_prob = if self.wind_speed > 65.0 { 0.7 } else { 0.6 };
        probability.min(max_prob)
    }

    fn count_burning_neighbors(&self, x: usize, y: usize) -> u8 {
        let mut count = 0;
        
        for dy in -1i32..=1 {
            for dx in -1i32..=1 {
                if dx == 0 && dy == 0 {
                    continue;
                }
                
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

/// Run a fast batch simulation - demonstrate Rust's speed advantage
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

/// A Python module implemented in Rust
#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<FireSimulation>()?;
    m.add_function(wrap_pyfunction!(run_batch_simulation, m)?)?;
    Ok(())
}
