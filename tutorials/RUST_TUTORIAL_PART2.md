# Rust Tutorial Part 2: Collections, Traits, and Concurrency

*Building powerful systems with Rust's advanced features - collections, traits, error handling, and fearless concurrency*

## Table of Contents
1. [Collections: Managing Data](#collections-managing-data)
2. [Error Handling: Embrace the Failure](#error-handling-embrace-the-failure)
3. [Traits: Shared Behavior](#traits-shared-behavior)
4. [Generic Programming](#generic-programming)
5. [Iterators: Processing Data Streams](#iterators-processing-data-streams)
6. [Concurrency: Fearless Parallelism](#concurrency-fearless-parallelism)
7. [Building the Fire Simulation Engine](#building-the-fire-simulation-engine)

---

## Collections: Managing Data

Rust's collections are like **different types of containers** for your data. Each one is optimized for specific use patterns.

### Vec<T>: The Growable Array

```rust
fn main() {
    // Creating vectors
    let mut temperatures = Vec::new();  // Empty vector
    temperatures.push(25.1);
    temperatures.push(28.3);
    temperatures.push(32.7);
    
    // More convenient creation
    let readings = vec![25.1, 28.3, 32.7, 29.9, 31.2];  // vec! macro
    let stations: Vec<String> = Vec::with_capacity(100);  // Pre-allocate space
    
    // Accessing elements
    let first_temp = readings[0];           // Panics if out of bounds
    let maybe_temp = readings.get(10);      // Returns Option<&T>
    
    match maybe_temp {
        Some(temp) => println!("Temperature: {}°C", temp),
        None => println!("No temperature at index 10"),
    }
    
    // Iterating
    for temp in &readings {
        println!("Reading: {}°C", temp);
    }
    
    // Vector operations
    println!("Number of readings: {}", readings.len());
    println!("Is empty: {}", readings.is_empty());
    println!("Contains hot reading: {}", readings.iter().any(|&t| t > 35.0));
}
```

### HashMap<K, V>: Key-Value Storage

```rust
use std::collections::HashMap;

fn main() {
    // Weather data by station ID
    let mut station_data = HashMap::new();
    station_data.insert("BH001".to_string(), 32.7);
    station_data.insert("SYD001".to_string(), 24.1);
    station_data.insert("MELB001".to_string(), 18.9);
    
    // Alternative creation
    let mut fire_danger: HashMap<String, String> = HashMap::from([
        ("Queensland".to_string(), "SEVERE".to_string()),
        ("NSW".to_string(), "HIGH".to_string()),
        ("Victoria".to_string(), "MODERATE".to_string()),
    ]);
    
    // Accessing values
    match station_data.get("BH001") {
        Some(temp) => println!("Broken Hill: {}°C", temp),
        None => println!("Station not found"),
    }
    
    // Update or insert
    station_data.insert("BH001".to_string(), 34.2);  // Updates existing
    fire_danger.entry("SA".to_string()).or_insert("LOW".to_string());  // Insert if not present
    
    // Iterate over key-value pairs
    for (station, temperature) in &station_data {
        println!("{}: {}°C", station, temperature);
    }
    
    // Count readings by temperature range
    let mut temp_ranges = HashMap::new();
    for &temp in station_data.values() {
        let range = if temp < 20.0 { "Cold" }
                   else if temp < 30.0 { "Mild" }
                   else { "Hot" };
        
        *temp_ranges.entry(range).or_insert(0) += 1;
    }
    
    println!("Temperature distribution: {:?}", temp_ranges);
}
```

### HashSet<T>: Unique Values

```rust
use std::collections::HashSet;

fn main() {
    // Track which regions have active fire alerts
    let mut active_alerts = HashSet::new();
    active_alerts.insert("Queensland");
    active_alerts.insert("NSW");
    active_alerts.insert("Queensland");  // Won't add duplicate
    
    println!("Active alerts: {}", active_alerts.len());  // 2
    
    // Check membership
    if active_alerts.contains("Victoria") {
        println!("Victoria has active alerts");
    } else {
        println!("Victoria: no alerts");
    }
    
    // Set operations
    let high_risk_regions: HashSet<&str> = ["Queensland", "NSW", "SA"].into_iter().collect();
    let current_fires: HashSet<&str> = ["Queensland", "WA"].into_iter().collect();
    
    // Intersection - regions with both high risk AND current fires
    let critical_regions: HashSet<_> = high_risk_regions.intersection(&current_fires).collect();
    println!("Critical regions: {:?}", critical_regions);  // {"Queensland"}
    
    // Union - all regions with either high risk OR current fires  
    let all_concern: HashSet<_> = high_risk_regions.union(&current_fires).collect();
    println!("All regions of concern: {:?}", all_concern);
    
    // Difference - high risk regions WITHOUT current fires
    let potential_risk: HashSet<_> = high_risk_regions.difference(&current_fires).collect();
    println!("High risk but no fires: {:?}", potential_risk);  // {"NSW", "SA"}
}
```

### VecDeque<T>: Double-Ended Queue

```rust
use std::collections::VecDeque;

fn main() {
    // Recent temperature readings (sliding window)
    let mut recent_temps = VecDeque::new();
    
    // Add new readings
    recent_temps.push_back(25.1);
    recent_temps.push_back(28.3);
    recent_temps.push_back(32.7);
    
    // Keep only last 5 readings
    while recent_temps.len() > 5 {
        recent_temps.pop_front();  // Remove oldest
    }
    
    // Can add/remove from both ends efficiently
    recent_temps.push_front(24.8);  // Add to beginning
    let latest = recent_temps.pop_back();  // Remove from end
    
    println!("Recent temperatures: {:?}", recent_temps);
    println!("Latest removed: {:?}", latest);
}
```

---

## Error Handling: Embrace the Failure

Rust makes you **explicitly handle errors** rather than hoping they won't happen. It's like having a **careful co-pilot** who makes you acknowledge every potential problem.

### Result<T, E>: Recoverable Errors

```rust
use std::fs::File;
use std::io::{self, Read};
use std::num::ParseFloatError;

// Function that might fail
fn read_temperature_from_file(filename: &str) -> Result<f64, io::Error> {
    let mut file = File::open(filename)?;  // ? propagates errors
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;
    
    // This could also fail, but we'll handle it differently
    match contents.trim().parse::<f64>() {
        Ok(temp) => Ok(temp),
        Err(_) => Err(io::Error::new(io::ErrorKind::InvalidData, "Invalid temperature format")),
    }
}

// Function with multiple error types
fn validate_temperature(temp_str: &str) -> Result<f64, String> {
    let temp = temp_str.parse::<f64>()
        .map_err(|_| format!("'{}' is not a valid number", temp_str))?;
    
    if temp < -100.0 || temp > 100.0 {
        return Err(format!("Temperature {} is out of valid range (-100 to 100)", temp));
    }
    
    Ok(temp)
}

// Weather station that might have sensor failures
#[derive(Debug)]
enum SensorError {
    Disconnected,
    CalibrationNeeded,
    ReadTimeout,
    InvalidReading(String),
}

fn read_sensor() -> Result<f64, SensorError> {
    // Simulate different types of sensor failures
    use rand::Rng;
    let mut rng = rand::thread_rng();
    
    match rng.gen_range(0..10) {
        0 => Err(SensorError::Disconnected),
        1 => Err(SensorError::CalibrationNeeded),
        2 => Err(SensorError::ReadTimeout),
        3 => Err(SensorError::InvalidReading("Sensor returned NaN".to_string())),
        _ => Ok(rng.gen_range(15.0..45.0)),  // Valid temperature
    }
}

fn main() {
    // Handling file reading errors
    match read_temperature_from_file("temperature.txt") {
        Ok(temp) => println!("Temperature from file: {}°C", temp),
        Err(error) => {
            match error.kind() {
                io::ErrorKind::NotFound => println!("Temperature file not found"),
                io::ErrorKind::PermissionDenied => println!("No permission to read file"),
                io::ErrorKind::InvalidData => println!("File contains invalid temperature data"),
                _ => println!("Failed to read temperature: {}", error),
            }
        }
    }
    
    // Validation with custom errors
    let temp_inputs = vec!["32.5", "invalid", "150.0", "25.1"];
    
    for input in temp_inputs {
        match validate_temperature(input) {
            Ok(temp) => println!("✅ Valid temperature: {}°C", temp),
            Err(error) => println!("❌ {}", error),
        }
    }
    
    // Handling sensor errors
    for i in 1..=5 {
        print!("Sensor reading {}: ", i);
        match read_sensor() {
            Ok(temp) => println!("{}°C", temp),
            Err(SensorError::Disconnected) => println!("Sensor disconnected - check cables"),
            Err(SensorError::CalibrationNeeded) => println!("Sensor needs calibration"),
            Err(SensorError::ReadTimeout) => println!("Sensor timeout - retrying..."),
            Err(SensorError::InvalidReading(msg)) => println!("Invalid reading: {}", msg),
        }
    }
}
```

### Option<T>: Handling Absence

```rust
// Weather station registry
struct WeatherStation {
    id: String,
    name: String,
    temperature: Option<f64>,  // Might not have current reading
    last_update: Option<u64>,  // Might never have been updated
}

impl WeatherStation {
    fn new(id: String, name: String) -> Self {
        WeatherStation {
            id,
            name,
            temperature: None,
            last_update: None,
        }
    }
    
    fn update_reading(&mut self, temp: f64) {
        self.temperature = Some(temp);
        self.last_update = Some(current_timestamp());
    }
    
    fn status_report(&self) -> String {
        let temp_str = match self.temperature {
            Some(temp) => format!("{}°C", temp),
            None => "No reading".to_string(),
        };
        
        let update_str = match self.last_update {
            Some(timestamp) => format!("Updated: {}", format_timestamp(timestamp)),
            None => "Never updated".to_string(),
        };
        
        format!("{} ({}): {} - {}", self.id, self.name, temp_str, update_str)
    }
    
    // Chain operations with Option
    fn temperature_in_fahrenheit(&self) -> Option<f64> {
        self.temperature.map(|c| c * 9.0 / 5.0 + 32.0)
    }
    
    // Combine multiple Options
    fn time_since_update(&self) -> Option<u64> {
        self.last_update.map(|timestamp| current_timestamp() - timestamp)
    }
}

// Utility functions
fn current_timestamp() -> u64 {
    use std::time::{SystemTime, UNIX_EPOCH};
    SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs()
}

fn format_timestamp(timestamp: u64) -> String {
    format!("{} seconds ago", current_timestamp() - timestamp)
}

fn main() {
    let mut stations = vec![
        WeatherStation::new("BH001".to_string(), "Broken Hill".to_string()),
        WeatherStation::new("SYD001".to_string(), "Sydney Observatory".to_string()),
        WeatherStation::new("MELB001".to_string(), "Melbourne CBD".to_string()),
    ];
    
    // Update some stations
    stations[0].update_reading(34.2);
    stations[1].update_reading(26.8);
    // Leave Melbourne without reading
    
    // Report status
    for station in &stations {
        println!("{}", station.status_report());
        
        // Use Option chaining
        if let Some(temp_f) = station.temperature_in_fahrenheit() {
            println!("  Temperature in Fahrenheit: {:.1}°F", temp_f);
        }
        
        if let Some(seconds) = station.time_since_update() {
            println!("  Last updated: {} seconds ago", seconds);
        }
    }
    
    // Find stations with temperatures above threshold
    let hot_stations: Vec<_> = stations.iter()
        .filter_map(|station| {
            station.temperature.map(|temp| (station, temp))
        })
        .filter(|(_, temp)| *temp > 30.0)
        .collect();
    
    println!("\nStations with temperature > 30°C:");
    for (station, temp) in hot_stations {
        println!("  {}: {}°C", station.name, temp);
    }
}
```

### Creating Custom Error Types

```rust
use std::fmt;

// Custom error type for our fire simulation
#[derive(Debug)]
enum SimulationError {
    InvalidCoordinates { x: usize, y: usize, max_x: usize, max_y: usize },
    CellNotIgnitable { x: usize, y: usize, reason: String },
    EnvironmentError(String),
    ConfigurationError(String),
}

// Implement Display for user-friendly error messages
impl fmt::Display for SimulationError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            SimulationError::InvalidCoordinates { x, y, max_x, max_y } => {
                write!(f, "Coordinates ({}, {}) are out of bounds (max: {}, {})", x, y, max_x, max_y)
            },
            SimulationError::CellNotIgnitable { x, y, reason } => {
                write!(f, "Cannot ignite cell at ({}, {}): {}", x, y, reason)
            },
            SimulationError::EnvironmentError(msg) => {
                write!(f, "Environment error: {}", msg)
            },
            SimulationError::ConfigurationError(msg) => {
                write!(f, "Configuration error: {}", msg)
            },
        }
    }
}

// Implement std::error::Error trait
impl std::error::Error for SimulationError {}

// Example usage in simulation
struct FireSimulation {
    width: usize,
    height: usize,
    // ... other fields
}

impl FireSimulation {
    fn ignite(&mut self, x: usize, y: usize) -> Result<(), SimulationError> {
        // Validate coordinates
        if x >= self.width || y >= self.height {
            return Err(SimulationError::InvalidCoordinates {
                x, 
                y, 
                max_x: self.width - 1, 
                max_y: self.height - 1,
            });
        }
        
        // Check if cell can be ignited (simplified)
        let can_ignite = true; // Replace with actual logic
        
        if !can_ignite {
            return Err(SimulationError::CellNotIgnitable {
                x,
                y,
                reason: "Cell contains no flammable material".to_string(),
            });
        }
        
        // Actually ignite the cell
        println!("🔥 Fire ignited at ({}, {})", x, y);
        Ok(())
    }
    
    fn validate_environment(&self, temp: f64, humidity: f64) -> Result<(), SimulationError> {
        if temp < -50.0 || temp > 60.0 {
            return Err(SimulationError::EnvironmentError(
                format!("Temperature {} is outside realistic range", temp)
            ));
        }
        
        if humidity < 0.0 || humidity > 100.0 {
            return Err(SimulationError::EnvironmentError(
                format!("Humidity {}% is invalid", humidity)
            ));
        }
        
        Ok(())
    }
}

fn main() {
    let mut sim = FireSimulation { width: 10, height: 10 };
    
    // Test error handling
    match sim.ignite(15, 15) {
        Ok(()) => println!("Fire started successfully"),
        Err(e) => println!("❌ Failed to start fire: {}", e),
    }
    
    match sim.validate_environment(45.0, 120.0) {
        Ok(()) => println!("Environment is valid"),
        Err(e) => println!("❌ Environment validation failed: {}", e),
    }
}
```

---

## Traits: Shared Behavior

Traits are like **contracts** that types can implement. They define **shared behavior** without inheritance - think of them as **interfaces** or **capabilities**.

### Basic Traits

```rust
// Trait for things that can report their fire danger
trait FireDangerAssessment {
    fn fire_danger_level(&self) -> &'static str;
    fn is_dangerous(&self) -> bool {
        // Default implementation
        matches!(self.fire_danger_level(), "HIGH" | "SEVERE" | "EXTREME" | "CATASTROPHIC")
    }
}

// Trait for things that can be displayed as fire simulation cells
trait SimulationDisplay {
    fn display_symbol(&self) -> char;
    fn display_color(&self) -> &'static str;
}

// Our cell state enum
#[derive(Debug, Clone, Copy, PartialEq)]
enum CellState {
    Empty,
    Vegetation,
    Burning,
    Burnt,
}

// Implement traits for CellState
impl SimulationDisplay for CellState {
    fn display_symbol(&self) -> char {
        match self {
            CellState::Empty => ' ',
            CellState::Vegetation => '🌿',
            CellState::Burning => '🔥',
            CellState::Burnt => '⚫',
        }
    }
    
    fn display_color(&self) -> &'static str {
        match self {
            CellState::Empty => "white",
            CellState::Vegetation => "green",
            CellState::Burning => "red",
            CellState::Burnt => "black",
        }
    }
}

// Weather conditions struct
struct WeatherConditions {
    temperature: f64,
    humidity: f64,
    wind_speed: f64,
}

impl FireDangerAssessment for WeatherConditions {
    fn fire_danger_level(&self) -> &'static str {
        let temp = self.temperature;
        let humidity = self.humidity;
        let wind = self.wind_speed;
        
        if temp > 40.0 && humidity < 15.0 && wind > 60.0 {
            "CATASTROPHIC"
        } else if temp > 35.0 && humidity < 20.0 && wind > 40.0 {
            "EXTREME"
        } else if temp > 30.0 && humidity < 25.0 && wind > 30.0 {
            "SEVERE"
        } else if temp > 25.0 && humidity < 40.0 && wind > 20.0 {
            "HIGH"
        } else {
            "MODERATE"
        }
    }
}

// Functions that work with any type implementing the trait
fn print_fire_risk<T: FireDangerAssessment>(item: &T) {
    println!("Fire danger: {} (Dangerous: {})", 
             item.fire_danger_level(), 
             item.is_dangerous());
}

fn display_cell_info<T: SimulationDisplay>(cell: &T) {
    println!("Cell: {} (color: {})", 
             cell.display_symbol(), 
             cell.display_color());
}

fn main() {
    // Create weather conditions
    let mild_weather = WeatherConditions {
        temperature: 22.0,
        humidity: 65.0,
        wind_speed: 10.0,
    };
    
    let dangerous_weather = WeatherConditions {
        temperature: 42.0,
        humidity: 12.0,
        wind_speed: 55.0,
    };
    
    // Use trait methods
    print_fire_risk(&mild_weather);
    print_fire_risk(&dangerous_weather);
    
    // Create cell states
    let cells = vec![
        CellState::Empty,
        CellState::Vegetation,
        CellState::Burning,
        CellState::Burnt,
    ];
    
    for cell in cells {
        display_cell_info(&cell);
    }
}
```

### Derive Traits

```rust
// Many common traits can be automatically derived
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
enum FireDangerLevel {
    Low,
    Moderate,
    High,
    VeryHigh,
    Severe,
    Extreme,
    Catastrophic,
}

#[derive(Debug, Clone, PartialEq)]
struct WeatherReading {
    temperature: f64,
    humidity: f64,
    wind_speed: f64,
    danger_level: FireDangerLevel,
}

fn main() {
    let reading1 = WeatherReading {
        temperature: 35.0,
        humidity: 25.0,
        wind_speed: 30.0,
        danger_level: FireDangerLevel::Severe,
    };
    
    let reading2 = reading1.clone();  // Clone trait
    
    println!("{:?}", reading1);  // Debug trait
    
    if reading1 == reading2 {    // PartialEq trait
        println!("Readings are identical");
    }
    
    // Using derived traits with collections
    use std::collections::HashMap;
    let mut danger_counts = HashMap::new();
    danger_counts.insert(FireDangerLevel::Severe, 5);  // Hash trait for keys
}
```

### Trait Bounds and Where Clauses

```rust
use std::fmt::Display;

// Function with multiple trait bounds
fn log_and_process<T>(item: T) -> String 
where 
    T: Display + FireDangerAssessment + Clone,
{
    let cloned_item = item.clone();
    let danger = cloned_item.fire_danger_level();
    format!("Processing {}: Danger level {}", item, danger)
}

// Implement Display for WeatherConditions
impl Display for WeatherConditions {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}°C, {}% humidity, {} km/h wind", 
               self.temperature, self.humidity, self.wind_speed)
    }
}

impl Clone for WeatherConditions {
    fn clone(&self) -> Self {
        WeatherConditions {
            temperature: self.temperature,
            humidity: self.humidity,
            wind_speed: self.wind_speed,
        }
    }
}

// Trait objects for dynamic dispatch
fn assess_multiple_conditions(conditions: Vec<&dyn FireDangerAssessment>) {
    for (i, condition) in conditions.iter().enumerate() {
        println!("Condition {}: {}", i + 1, condition.fire_danger_level());
    }
}

fn main() {
    let weather = WeatherConditions {
        temperature: 38.0,
        humidity: 20.0,
        wind_speed: 35.0,
    };
    
    // Use function with trait bounds
    let result = log_and_process(weather.clone());
    println!("{}", result);
    
    // Trait objects
    let conditions: Vec<&dyn FireDangerAssessment> = vec![&weather];
    assess_multiple_conditions(conditions);
}
```

---

## Generic Programming

Generics let you write code that works with **multiple types** while maintaining type safety. Think of them as **type templates**.

### Generic Structs and Functions

```rust
// Generic data structure for sensor readings
#[derive(Debug)]
struct SensorReading<T> {
    value: T,
    timestamp: u64,
    sensor_id: String,
}

impl<T> SensorReading<T> {
    fn new(value: T, sensor_id: String) -> Self {
        SensorReading {
            value,
            timestamp: current_timestamp(),
            sensor_id,
        }
    }
    
    fn age_seconds(&self) -> u64 {
        current_timestamp() - self.timestamp
    }
}

// Specialized methods for specific types
impl SensorReading<f64> {
    fn is_temperature_valid(&self) -> bool {
        self.value >= -50.0 && self.value <= 60.0
    }
    
    fn to_fahrenheit(&self) -> SensorReading<f64> {
        SensorReading {
            value: self.value * 9.0 / 5.0 + 32.0,
            timestamp: self.timestamp,
            sensor_id: self.sensor_id.clone(),
        }
    }
}

// Generic function with constraints
fn process_numeric_reading<T>(reading: &SensorReading<T>) -> String
where 
    T: Display + PartialOrd + Copy,
{
    format!("Sensor {}: {} ({}s ago)", 
            reading.sensor_id, 
            reading.value,
            reading.age_seconds())
}

// Generic function for finding extremes
fn find_extreme_readings<T>(readings: &[SensorReading<T>], compare: fn(&T, &T) -> bool) -> Vec<&SensorReading<T>>
where 
    T: Clone,
{
    if readings.is_empty() {
        return Vec::new();
    }
    
    let mut extremes = vec![&readings[0]];
    let mut current_extreme = &readings[0].value;
    
    for reading in readings.iter().skip(1) {
        if compare(&reading.value, current_extreme) {
            extremes.clear();
            extremes.push(reading);
            current_extreme = &reading.value;
        } else if !compare(current_extreme, &reading.value) {
            extremes.push(reading);
        }
    }
    
    extremes
}

use std::fmt::Display;

fn current_timestamp() -> u64 {
    use std::time::{SystemTime, UNIX_EPOCH};
    SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs()
}

fn main() {
    // Temperature readings
    let temp_readings = vec![
        SensorReading::new(32.7, "TEMP_001".to_string()),
        SensorReading::new(45.2, "TEMP_002".to_string()),
        SensorReading::new(28.1, "TEMP_003".to_string()),
        SensorReading::new(45.2, "TEMP_004".to_string()), // Another max
    ];
    
    // Humidity readings
    let humidity_readings = vec![
        SensorReading::new(65, "HUM_001".to_string()),
        SensorReading::new(32, "HUM_002".to_string()),
        SensorReading::new(78, "HUM_003".to_string()),
    ];
    
    // Process readings
    for reading in &temp_readings {
        println!("{}", process_numeric_reading(reading));
        
        if reading.is_temperature_valid() {
            println!("  ✅ Temperature is valid");
        } else {
            println!("  ❌ Temperature out of range");
        }
    }
    
    // Find maximum temperature readings
    let max_temps = find_extreme_readings(&temp_readings, |a, b| *a > *b);
    println!("\nMaximum temperature readings:");
    for reading in max_temps {
        println!("  {}: {}°C", reading.sensor_id, reading.value);
    }
    
    // Find minimum humidity readings
    let min_humidity = find_extreme_readings(&humidity_readings, |a, b| *a < *b);
    println!("\nMinimum humidity readings:");
    for reading in min_humidity {
        println!("  {}: {}%", reading.sensor_id, reading.value);
    }
}
```

### Generic Collections

```rust
use std::collections::HashMap;

// Generic cache for any type of sensor data
#[derive(Debug)]
struct SensorCache<K, V> {
    data: HashMap<K, V>,
    max_age_seconds: u64,
}

impl<K, V> SensorCache<K, V> 
where 
    K: std::hash::Hash + Eq + Clone,
    V: Clone,
{
    fn new(max_age_seconds: u64) -> Self {
        SensorCache {
            data: HashMap::new(),
            max_age_seconds,
        }
    }
    
    fn insert(&mut self, key: K, value: V) {
        self.data.insert(key, value);
    }
    
    fn get(&self, key: &K) -> Option<&V> {
        self.data.get(key)
    }
    
    fn len(&self) -> usize {
        self.data.len()
    }
}

// Specialized cache for timestamped data
#[derive(Debug, Clone)]
struct TimestampedValue<T> {
    value: T,
    timestamp: u64,
}

impl<K, T> SensorCache<K, TimestampedValue<T>>
where
    K: std::hash::Hash + Eq + Clone,
    T: Clone,
{
    fn insert_with_timestamp(&mut self, key: K, value: T) {
        let timestamped = TimestampedValue {
            value,
            timestamp: current_timestamp(),
        };
        self.insert(key, timestamped);
    }
    
    fn get_fresh(&self, key: &K) -> Option<&T> {
        self.get(key).and_then(|timestamped| {
            if current_timestamp() - timestamped.timestamp <= self.max_age_seconds {
                Some(&timestamped.value)
            } else {
                None
            }
        })
    }
    
    fn cleanup_expired(&mut self) {
        let current = current_timestamp();
        let max_age = self.max_age_seconds;
        
        self.data.retain(|_, timestamped| {
            current - timestamped.timestamp <= max_age
        });
    }
}

fn main() {
    // Cache for temperature readings (expire after 300 seconds)
    let mut temp_cache = SensorCache::new(300);
    temp_cache.insert_with_timestamp("station_001".to_string(), 32.7);
    temp_cache.insert_with_timestamp("station_002".to_string(), 28.1);
    
    // Cache for boolean alert states (expire after 60 seconds)  
    let mut alert_cache = SensorCache::new(60);
    alert_cache.insert_with_timestamp("fire_alert_north".to_string(), true);
    alert_cache.insert_with_timestamp("fire_alert_south".to_string(), false);
    
    // Retrieve fresh data
    if let Some(temp) = temp_cache.get_fresh(&"station_001".to_string()) {
        println!("Station 001 temperature: {}°C", temp);
    } else {
        println!("Station 001: no fresh data");
    }
    
    if let Some(alert) = alert_cache.get_fresh(&"fire_alert_north".to_string()) {
        println!("North fire alert: {}", alert);
    }
    
    println!("Temperature cache size: {}", temp_cache.len());
    println!("Alert cache size: {}", alert_cache.len());
}
```

---

## Iterators: Processing Data Streams

Iterators are **lazy data processors** - like having an **assembly line** that only does work when you ask for results.

### Basic Iterator Operations

```rust
fn main() {
    let temperatures = vec![25.1, 28.3, 32.7, 29.9, 31.2, 35.8, 27.4];
    
    // Basic iteration
    for temp in &temperatures {
        println!("Temperature: {}°C", temp);
    }
    
    // Iterator methods (lazy - no work done until collected)
    let hot_temps: Vec<f64> = temperatures
        .iter()                          // Create iterator
        .filter(|&&temp| temp > 30.0)   // Only hot temperatures
        .map(|&temp| temp * 9.0/5.0 + 32.0) // Convert to Fahrenheit
        .collect();                      // Actually do the work
    
    println!("Hot temperatures in Fahrenheit: {:?}", hot_temps);
    
    // Chaining operations
    let stats = temperatures
        .iter()
        .map(|&temp| temp)                     // Convert &f64 to f64
        .fold((0.0, 0.0, f64::INFINITY, f64::NEG_INFINITY), 
              |(sum, count, min, max), temp| {
                  (sum + temp, count + 1.0, min.min(temp), max.max(temp))
              });
    
    let (sum, count, min_temp, max_temp) = stats;
    let average = sum / count;
    
    println!("Temperature statistics:");
    println!("  Average: {:.1}°C", average);
    println!("  Min: {:.1}°C", min_temp);
    println!("  Max: {:.1}°C", max_temp);
    println!("  Range: {:.1}°C", max_temp - min_temp);
}
```

### Custom Iterators

```rust
// Iterator for generating fire spread patterns
struct FireSpreadIterator {
    center_x: usize,
    center_y: usize,
    current_radius: usize,
    max_radius: usize,
    current_angle: f64,
    angle_step: f64,
}

impl FireSpreadIterator {
    fn new(center_x: usize, center_y: usize, max_radius: usize) -> Self {
        FireSpreadIterator {
            center_x,
            center_y,
            current_radius: 1,
            max_radius,
            current_angle: 0.0,
            angle_step: std::f64::consts::PI / 8.0,  // 22.5 degree steps
        }
    }
}

impl Iterator for FireSpreadIterator {
    type Item = (usize, usize);  // (x, y) coordinates
    
    fn next(&mut self) -> Option<Self::Item> {
        if self.current_radius > self.max_radius {
            return None;
        }
        
        // Calculate current position
        let x = self.center_x + (self.current_radius as f64 * self.current_angle.cos()) as usize;
        let y = self.center_y + (self.current_radius as f64 * self.current_angle.sin()) as usize;
        
        // Advance to next angle
        self.current_angle += self.angle_step;
        
        // If we've completed a circle, move to next radius
        if self.current_angle >= 2.0 * std::f64::consts::PI {
            self.current_angle = 0.0;
            self.current_radius += 1;
        }
        
        Some((x, y))
    }
}

// Iterator for weather data windows
struct WeatherWindow<'a> {
    data: &'a [f64],
    window_size: usize,
    current_pos: usize,
}

impl<'a> WeatherWindow<'a> {
    fn new(data: &'a [f64], window_size: usize) -> Self {
        WeatherWindow {
            data,
            window_size,
            current_pos: 0,
        }
    }
}

impl<'a> Iterator for WeatherWindow<'a> {
    type Item = &'a [f64];
    
    fn next(&mut self) -> Option<Self::Item> {
        if self.current_pos + self.window_size > self.data.len() {
            return None;
        }
        
        let window = &self.data[self.current_pos..self.current_pos + self.window_size];
        self.current_pos += 1;
        Some(window)
    }
}

fn main() {
    // Using fire spread iterator
    println!("Fire spread pattern from (10, 10):");
    let fire_spread = FireSpreadIterator::new(10, 10, 3);
    for (i, (x, y)) in fire_spread.enumerate() {
        println!("  Step {}: ({}, {})", i + 1, x, y);
        if i >= 15 { break; } // Limit output
    }
    
    // Using weather window iterator
    let temperatures = vec![20.1, 22.3, 25.7, 28.9, 32.1, 29.8, 26.4, 23.2, 21.0];
    println!("\n3-day moving average temperatures:");
    
    let windows = WeatherWindow::new(&temperatures, 3);
    for (i, window) in windows.enumerate() {
        let average: f64 = window.iter().sum::<f64>() / window.len() as f64;
        println!("  Days {}-{}: {:.1}°C", i + 1, i + 3, average);
    }
    
    // Advanced iterator operations
    let daily_temps = vec![
        vec![22.1, 28.5, 32.7],  // Day 1: min, avg, max
        vec![24.2, 30.1, 35.8],  // Day 2
        vec![26.5, 31.4, 37.2],  // Day 3
    ];
    
    // Find hottest maximum temperature across all days
    let hottest_max = daily_temps
        .iter()
        .map(|day| day[2])          // Get max temp for each day
        .max_by(|a, b| a.partial_cmp(b).unwrap());
    
    if let Some(temp) = hottest_max {
        println!("\nHottest maximum temperature: {}°C", temp);
    }
    
    // Calculate daily temperature ranges
    let daily_ranges: Vec<f64> = daily_temps
        .iter()
        .map(|day| day[2] - day[0])  // max - min
        .collect();
    
    println!("Daily temperature ranges: {:?}", daily_ranges);
}
```

### Parallel Iterators with Rayon

```rust
use rayon::prelude::*;

fn main() {
    // Large dataset of temperature readings
    let temperatures: Vec<f64> = (0..1_000_000)
        .map(|i| 20.0 + (i as f64 * 0.01) % 30.0)  // Generate data
        .collect();
    
    println!("Processing {} temperature readings...", temperatures.len());
    
    // Sequential processing
    let start = std::time::Instant::now();
    let hot_count_sequential = temperatures
        .iter()
        .filter(|&&temp| temp > 35.0)
        .count();
    let sequential_time = start.elapsed();
    
    // Parallel processing
    let start = std::time::Instant::now();
    let hot_count_parallel = temperatures
        .par_iter()                    // Parallel iterator
        .filter(|&&temp| temp > 35.0)
        .count();
    let parallel_time = start.elapsed();
    
    println!("Sequential: {} hot readings in {:?}", hot_count_sequential, sequential_time);
    println!("Parallel: {} hot readings in {:?}", hot_count_parallel, parallel_time);
    
    if sequential_time.as_millis() > 0 {
        let speedup = sequential_time.as_millis() as f64 / parallel_time.as_millis() as f64;
        println!("Speedup: {:.1}x", speedup);
    }
    
    // Complex parallel operations
    let fire_risk_stats = temperatures
        .par_iter()
        .map(|&temp| {
            // Simulate complex fire risk calculation
            let base_risk = if temp > 40.0 { 0.8 } 
                           else if temp > 30.0 { 0.4 }
                           else { 0.1 };
            base_risk * (temp / 50.0)
        })
        .reduce(
            || (0.0, 0.0, 0),                    // Initial: (sum, max, count)
            |(sum1, max1, count1), risk| {
                (sum1 + risk, max1.max(risk), count1 + 1)
            }
        );
    
    let (total_risk, max_risk, count) = fire_risk_stats;
    let avg_risk = total_risk / count as f64;
    
    println!("Fire risk analysis:");
    println!("  Average risk: {:.3}", avg_risk);
    println!("  Maximum risk: {:.3}", max_risk);
    println!("  Total readings: {}", count);
}
```

---

## Concurrency: Fearless Parallelism

Rust's ownership system prevents **data races at compile time**, making concurrent programming much safer. It's like having **traffic laws that are physically impossible to break**.

### Threads and Message Passing

```rust
use std::thread;
use std::sync::mpsc;
use std::time::Duration;
use rand::Rng;

// Simulate a weather station that sends readings
fn weather_station(station_id: String, sender: mpsc::Sender<WeatherReading>) {
    let mut rng = rand::thread_rng();
    
    for reading_num in 1..=10 {
        let reading = WeatherReading {
            station_id: station_id.clone(),
            temperature: 15.0 + rng.gen::<f64>() * 30.0,  // 15-45°C
            humidity: 20.0 + rng.gen::<f64>() * 60.0,     // 20-80%
            timestamp: reading_num,
        };
        
        println!("📡 {}: Sending reading #{}", station_id, reading_num);
        sender.send(reading).unwrap();
        
        // Simulate time between readings
        thread::sleep(Duration::from_millis(100));
    }
    
    println!("📡 {} finished transmitting", station_id);
}

#[derive(Debug, Clone)]
struct WeatherReading {
    station_id: String,
    temperature: f64,
    humidity: f64,
    timestamp: u64,
}

fn main() {
    // Create communication channel
    let (sender, receiver) = mpsc::channel();
    
    // Spawn multiple weather station threads
    let stations = vec!["Brisbane", "Sydney", "Melbourne"];
    let mut handles = Vec::new();
    
    for station in stations {
        let sender_clone = sender.clone();
        let station_name = format!("Station_{}", station);
        
        let handle = thread::spawn(move || {
            weather_station(station_name, sender_clone);
        });
        
        handles.push(handle);
    }
    
    // Drop the original sender so receiver knows when all senders are done
    drop(sender);
    
    // Collect all readings from all stations
    let mut all_readings = Vec::new();
    while let Ok(reading) = receiver.recv() {
        println!("📊 Received: {} - {:.1}°C, {:.1}% humidity", 
                 reading.station_id, reading.temperature, reading.humidity);
        all_readings.push(reading);
    }
    
    // Wait for all threads to complete
    for handle in handles {
        handle.join().unwrap();
    }
    
    // Analyze collected data
    println!("\n📈 Final Analysis:");
    println!("Total readings received: {}", all_readings.len());
    
    let avg_temp: f64 = all_readings.iter()
        .map(|r| r.temperature)
        .sum::<f64>() / all_readings.len() as f64;
    
    println!("Average temperature: {:.1}°C", avg_temp);
}
```

### Shared State with Arc and Mutex

```rust
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;

// Shared fire monitoring system
#[derive(Debug)]
struct FireMonitoringSystem {
    active_fires: u32,
    total_area_burnt: f64,    // hectares
    alert_level: String,
}

impl FireMonitoringSystem {
    fn new() -> Self {
        FireMonitoringSystem {
            active_fires: 0,
            total_area_burnt: 0.0,
            alert_level: "GREEN".to_string(),
        }
    }
    
    fn report_new_fire(&mut self, area: f64) {
        self.active_fires += 1;
        self.total_area_burnt += area;
        
        // Update alert level based on conditions
        self.alert_level = if self.active_fires > 10 || self.total_area_burnt > 10000.0 {
            "RED".to_string()
        } else if self.active_fires > 5 || self.total_area_burnt > 1000.0 {
            "ORANGE".to_string()
        } else if self.active_fires > 0 {
            "YELLOW".to_string()
        } else {
            "GREEN".to_string()
        };
    }
    
    fn extinguish_fire(&mut self, area: f64) {
        if self.active_fires > 0 {
            self.active_fires -= 1;
        }
        // Area burnt doesn't decrease when fire is extinguished
        
        // Recalculate alert level
        self.alert_level = if self.active_fires > 10 || self.total_area_burnt > 10000.0 {
            "RED".to_string()
        } else if self.active_fires > 5 || self.total_area_burnt > 1000.0 {
            "ORANGE".to_string()
        } else if self.active_fires > 0 {
            "YELLOW".to_string()
        } else {
            "GREEN".to_string()
        };
    }
}

fn fire_detection_system(id: u32, monitoring_system: Arc<Mutex<FireMonitoringSystem>>) {
    let mut rng = rand::thread_rng();
    
    for i in 1..=5 {
        // Simulate detecting a fire
        let fire_area = 10.0 + rng.gen::<f64>() * 100.0;  // 10-110 hectares
        
        println!("🔥 Detector {}: Found fire #{} ({:.1} hectares)", id, i, fire_area);
        
        // Report to monitoring system (need to lock the mutex)
        {
            let mut system = monitoring_system.lock().unwrap();
            system.report_new_fire(fire_area);
            println!("📊 System status: {} fires, {:.1} hectares, Alert: {}", 
                     system.active_fires, system.total_area_burnt, system.alert_level);
        } // Lock is released here
        
        thread::sleep(Duration::from_millis(200));
        
        // Sometimes extinguish fires
        if i % 2 == 0 {
            thread::sleep(Duration::from_millis(100));
            println!("🚒 Detector {}: Fire extinguished", id);
            
            let mut system = monitoring_system.lock().unwrap();
            system.extinguish_fire(fire_area);
            println!("📊 System status: {} fires, {:.1} hectares, Alert: {}", 
                     system.active_fires, system.total_area_burnt, system.alert_level);
        }
    }
    
    println!("🔍 Detector {} finished monitoring", id);
}

fn main() {
    // Create shared monitoring system
    let monitoring_system = Arc::new(Mutex::new(FireMonitoringSystem::new()));
    
    // Spawn multiple fire detection threads
    let mut handles = Vec::new();
    
    for detector_id in 1..=3 {
        let system_clone = Arc::clone(&monitoring_system);
        
        let handle = thread::spawn(move || {
            fire_detection_system(detector_id, system_clone);
        });
        
        handles.push(handle);
    }
    
    // Wait for all detectors to finish
    for handle in handles {
        handle.join().unwrap();
    }
    
    // Final system status
    let final_system = monitoring_system.lock().unwrap();
    println!("\n🏁 Final System Status:");
    println!("  Active fires: {}", final_system.active_fires);
    println!("  Total area burnt: {:.1} hectares", final_system.total_area_burnt);
    println!("  Alert level: {}", final_system.alert_level);
}
```

### Async Programming with Tokio

```rust
use tokio::time::{sleep, Duration};
use std::collections::HashMap;

// Async function to fetch weather data (simulated)
async fn fetch_weather_data(station_id: &str) -> Result<WeatherReading, String> {
    println!("🌐 Fetching data from {}...", station_id);
    
    // Simulate network delay
    sleep(Duration::from_millis(200)).await;
    
    // Simulate occasional failures
    if station_id == "unreliable_station" {
        return Err("Connection timeout".to_string());
    }
    
    let reading = WeatherReading {
        station_id: station_id.to_string(),
        temperature: 20.0 + rand::random::<f64>() * 25.0,
        humidity: 30.0 + rand::random::<f64>() * 50.0,
        timestamp: std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs(),
    };
    
    println!("✅ Received data from {}: {:.1}°C", station_id, reading.temperature);
    Ok(reading)
}

// Async function to process multiple stations concurrently
async fn collect_regional_data(station_ids: Vec<&str>) -> HashMap<String, WeatherReading> {
    let mut tasks = Vec::new();
    
    // Start all requests concurrently
    for station_id in station_ids {
        let task = tokio::spawn(async move {
            (station_id.to_string(), fetch_weather_data(station_id).await)
        });
        tasks.push(task);
    }
    
    // Wait for all to complete
    let mut results = HashMap::new();
    for task in tasks {
        let (station_id, result) = task.await.unwrap();
        
        match result {
            Ok(reading) => {
                results.insert(station_id, reading);
            },
            Err(error) => {
                println!("❌ Failed to get data from {}: {}", station_id, error);
            }
        }
    }
    
    results
}

// Async function for real-time monitoring
async fn monitor_weather_stations() {
    let stations = vec![
        "brisbane_central", 
        "sydney_harbor", 
        "melbourne_cbd", 
        "perth_airport",
        "unreliable_station"
    ];
    
    for round in 1..=3 {
        println!("\n🔄 Monitoring round {}", round);
        
        let readings = collect_regional_data(stations.clone()).await;
        
        println!("📊 Round {} results:", round);
        for (station_id, reading) in &readings {
            println!("  {}: {:.1}°C, {:.1}% humidity", 
                     station_id, reading.temperature, reading.humidity);
        }
        
        // Check for extreme conditions
        let extreme_temps: Vec<_> = readings.iter()
            .filter(|(_, reading)| reading.temperature > 40.0)
            .collect();
        
        if !extreme_temps.is_empty() {
            println!("🚨 EXTREME TEMPERATURE ALERT:");
            for (station_id, reading) in extreme_temps {
                println!("  {}: {:.1}°C", station_id, reading.temperature);
            }
        }
        
        // Wait before next round
        if round < 3 {
            println!("⏳ Waiting for next round...");
            sleep(Duration::from_secs(1)).await;
        }
    }
}

#[tokio::main]
async fn main() {
    println!("🌤️ Starting Weather Monitoring System");
    monitor_weather_stations().await;
    println!("✅ Monitoring complete");
}
```

---

## Building the Fire Simulation Engine

Let's put together all the concepts to build a **high-performance fire simulation engine**:

```rust
use rayon::prelude::*;
use std::sync::{Arc, Mutex};
use std::time::Instant;

// Core simulation types (from Part 1, enhanced)
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum CellState {
    Empty,
    Vegetation,
    Burning,
    Burnt,
}

#[derive(Debug, Clone)]
pub struct Environment {
    wind_speed: f64,
    wind_direction: f64,
    humidity: f64,
    temperature: f64,
}

#[derive(Debug, Clone)]
pub struct Cell {
    state: CellState,
    fuel_load: f64,
    moisture: f64,
}

// High-performance simulation engine
pub struct FireSimulationEngine {
    width: usize,
    height: usize,
    cells: Vec<Vec<Cell>>,
    environment: Environment,
    step_count: u32,
    statistics: SimulationStatistics,
}

#[derive(Debug, Clone)]
pub struct SimulationStatistics {
    pub step: u32,
    pub empty_cells: u32,
    pub vegetation_cells: u32,
    pub burning_cells: u32,
    pub burnt_cells: u32,
    pub fire_spread_percentage: f64,
}

impl Cell {
    fn new(state: CellState) -> Self {
        let mut rng = rand::thread_rng();
        Cell {
            state,
            fuel_load: 0.7 + rng.gen::<f64>() * 0.3,  // 0.7 to 1.0
            moisture: 0.2 + rng.gen::<f64>() * 0.4,   // 0.2 to 0.6
        }
    }
    
    fn can_ignite(&self) -> bool {
        matches!(self.state, CellState::Vegetation) && self.fuel_load > 0.1
    }
    
    // Calculate ignition probability with environmental factors
    fn ignition_probability(&self, burning_neighbors: u8, env: &Environment) -> f64 {
        if !self.can_ignite() {
            return 0.0;
        }
        
        // Base probability influenced by multiple factors
        let mut prob = 0.15;
        
        // Neighbor influence (most important factor)
        prob += burning_neighbors as f64 * 0.25;
        
        // Environmental factors
        prob *= 1.0 + (env.wind_speed / 100.0);
        prob *= 1.0 + (1.0 - env.humidity / 100.0);
        prob *= 1.0 + ((env.temperature - 20.0) / 100.0).max(0.0);
        
        // Cell-specific factors
        prob *= self.fuel_load;
        prob *= 1.0 - (self.moisture * 0.5);
        
        prob.min(0.9)  // Cap at 90%
    }
}

impl FireSimulationEngine {
    pub fn new(width: usize, height: usize, environment: Environment) -> Self {
        let mut rng = rand::thread_rng();
        
        // Initialize grid with random vegetation
        let cells: Vec<Vec<Cell>> = (0..height)
            .map(|_| {
                (0..width)
                    .map(|_| {
                        let state = if rng.gen::<f64>() < 0.8 {
                            CellState::Vegetation
                        } else {
                            CellState::Empty
                        };
                        Cell::new(state)
                    })
                    .collect()
            })
            .collect();
        
        let mut engine = FireSimulationEngine {
            width,
            height,
            cells,
            environment,
            step_count: 0,
            statistics: SimulationStatistics {
                step: 0,
                empty_cells: 0,
                vegetation_cells: 0,
                burning_cells: 0,
                burnt_cells: 0,
                fire_spread_percentage: 0.0,
            },
        };
        
        engine.update_statistics();
        engine
    }
    
    pub fn ignite(&mut self, x: usize, y: usize) -> Result<(), String> {
        if x >= self.width || y >= self.height {
            return Err(format!("Coordinates out of bounds: ({}, {})", x, y));
        }
        
        let cell = &mut self.cells[y][x];
        if cell.can_ignite() {
            cell.state = CellState::Burning;
            self.update_statistics();
            Ok(())
        } else {
            Err(format!("Cell at ({}, {}) cannot be ignited", x, y))
        }
    }
    
    // High-performance simulation step using parallel processing
    pub fn step(&mut self) -> Result<(), String> {
        let start_time = Instant::now();
        
        // Process all cells in parallel
        let updates: Vec<_> = (0..self.height)
            .into_par_iter()
            .flat_map(|y| {
                (0..self.width).into_par_iter().filter_map(move |x| {
                    self.process_cell(x, y).map(|new_state| (x, y, new_state))
                })
            })
            .collect();
        
        // Apply all updates atomically
        for (x, y, new_state) in updates {
            self.cells[y][x].state = new_state;
        }
        
        self.step_count += 1;
        self.update_statistics();
        
        let elapsed = start_time.elapsed();
        if elapsed.as_millis() > 100 {  // Log slow steps
            println!("⚠️ Slow simulation step: {:?}", elapsed);
        }
        
        Ok(())
    }
    
    fn process_cell(&self, x: usize, y: usize) -> Option<CellState> {
        let cell = &self.cells[y][x];
        
        match cell.state {
            CellState::Burning => Some(CellState::Burnt),
            CellState::Vegetation => {
                let burning_neighbors = self.count_burning_neighbors(x, y);
                if burning_neighbors > 0 {
                    let prob = cell.ignition_probability(burning_neighbors, &self.environment);
                    if rand::random::<f64>() < prob {
                        Some(CellState::Burning)
                    } else {
                        None
                    }
                } else {
                    None
                }
            },
            _ => None,
        }
    }
    
    fn count_burning_neighbors(&self, x: usize, y: usize) -> u8 {
        let mut count = 0;
        
        for dy in -1i32..=1 {
            for dx in -1i32..=1 {
                if dx == 0 && dy == 0 { continue; }
                
                let nx = (x as i32 + dx) as usize;
                let ny = (y as i32 + dy) as usize;
                
                if nx < self.width && ny < self.height {
                    if matches!(self.cells[ny][nx].state, CellState::Burning) {
                        count += 1;
                    }
                }
            }
        }
        
        count
    }
    
    fn update_statistics(&mut self) {
        let mut empty = 0;
        let mut vegetation = 0;
        let mut burning = 0;
        let mut burnt = 0;
        
        for row in &self.cells {
            for cell in row {
                match cell.state {
                    CellState::Empty => empty += 1,
                    CellState::Vegetation => vegetation += 1,
                    CellState::Burning => burning += 1,
                    CellState::Burnt => burnt += 1,
                }
            }
        }
        
        let total_cells = (self.width * self.height) as f64;
        let fire_spread_percentage = (burnt as f64 / total_cells) * 100.0;
        
        self.statistics = SimulationStatistics {
            step: self.step_count,
            empty_cells: empty,
            vegetation_cells: vegetation,
            burning_cells: burning,
            burnt_cells: burnt,
            fire_spread_percentage,
        };
    }
    
    pub fn get_statistics(&self) -> &SimulationStatistics {
        &self.statistics
    }
    
    pub fn get_grid_state(&self) -> Vec<u8> {
        self.cells
            .iter()
            .flat_map(|row| {
                row.iter().map(|cell| cell.state as u8)
            })
            .collect()
    }
    
    // Run multiple simulation steps
    pub fn run_simulation(&mut self, steps: u32) -> Vec<SimulationStatistics> {
        let mut history = Vec::with_capacity(steps as usize);
        
        for step_num in 1..=steps {
            if let Err(e) = self.step() {
                println!("❌ Simulation error at step {}: {}", step_num, e);
                break;
            }
            
            history.push(self.statistics.clone());
            
            // Stop if no more fires
            if self.statistics.burning_cells == 0 && step_num > 1 {
                println!("🔥 Fire simulation completed - no active fires remaining");
                break;
            }
            
            // Progress reporting for long simulations
            if steps > 10 && step_num % (steps / 10) == 0 {
                let progress = (step_num as f64 / steps as f64) * 100.0;
                println!("📈 Simulation progress: {:.0}% (Step {}/{})", progress, step_num, steps);
            }
        }
        
        history
    }
}

// Utility function for performance testing
pub fn benchmark_simulation(width: usize, height: usize, steps: u32) -> Duration {
    let environment = Environment {
        wind_speed: 25.0,
        wind_direction: 0.0,
        humidity: 35.0,
        temperature: 38.0,
    };
    
    let mut simulation = FireSimulationEngine::new(width, height, environment);
    simulation.ignite(width / 2, height / 2).unwrap();
    
    let start_time = Instant::now();
    simulation.run_simulation(steps);
    start_time.elapsed()
}

fn main() {
    println!("🔥 Advanced Fire Simulation Engine");
    
    // Create realistic Australian bushfire conditions
    let environment = Environment {
        wind_speed: 45.0,     // Strong wind
        wind_direction: 0.0,   // From west
        humidity: 18.0,        // Low humidity
        temperature: 42.0,     // Hot temperature
    };
    
    let mut simulation = FireSimulationEngine::new(50, 50, environment);
    
    // Start multiple fires
    simulation.ignite(10, 10).unwrap();
    simulation.ignite(40, 40).unwrap();
    
    println!("🎯 Fires ignited at (10,10) and (40,40)");
    
    // Run simulation
    let start_time = Instant::now();
    let history = simulation.run_simulation(30);
    let total_time = start_time.elapsed();
    
    // Report results
    let final_stats = simulation.get_statistics();
    println!("\n📊 Final Results:");
    println!("  Simulation time: {:?}", total_time);
    println!("  Total steps: {}", final_stats.step);
    println!("  Fire spread: {:.1}% of area", final_stats.fire_spread_percentage);
    println!("  Cells burnt: {}", final_stats.burnt_cells);
    println!("  Active fires: {}", final_stats.burning_cells);
    
    // Performance benchmark
    println!("\n⚡ Performance Benchmark:");
    let sizes = vec![(25, 25), (50, 50), (100, 100)];
    
    for (width, height) in sizes {
        let bench_time = benchmark_simulation(width, height, 20);
        let cells_per_second = (width * height * 20) as f64 / bench_time.as_secs_f64();
        
        println!("  {}x{} grid: {:?} ({:.0} cells/second)", 
                 width, height, bench_time, cells_per_second);
    }
}

use rand;
```

---

## Key Rust Concepts Summary - Part 2

**Collections:**
- `Vec<T>` for growable arrays, `HashMap<K,V>` for key-value storage
- `HashSet<T>` for unique values, `VecDeque<T>` for double-ended queues
- Choose the right collection for your access patterns

**Error Handling:**
- `Result<T, E>` for recoverable errors, `Option<T>` for absence
- Use `?` operator to propagate errors up the call stack
- Create custom error types with `Display` and `Error` traits

**Traits:**
- Define shared behavior without inheritance
- Implement traits for your types to integrate with Rust ecosystem
- Use trait bounds to constrain generic types
- Derive common traits automatically with `#[derive(...)]`

**Generics:**
- Write code that works with multiple types
- Use constraints (`where T: Trait`) to ensure capabilities
- Generic collections are type-safe and efficient

**Iterators:**
- Lazy processing with method chaining
- Use `map`, `filter`, `fold`, `collect` for data transformation
- Custom iterators implement the `Iterator` trait
- Parallel iterators with Rayon for CPU-intensive tasks

**Concurrency:**
- `thread::spawn` for creating threads
- `mpsc::channel` for message passing between threads
- `Arc<Mutex<T>>` for shared mutable state
- `async/await` with Tokio for asynchronous I/O

**Sensible Defaults:**
- Use iterators instead of loops when possible - they're often faster
- Prefer message passing (`mpsc`) over shared state (`Mutex`) when feasible
- Use `Arc` (atomic reference counting) for sharing data between threads
- Handle all `Result` and `Option` values explicitly - don't ignore them
- Use parallel iterators (Rayon) for CPU-bound work on large datasets
- Create custom error types for better error handling in libraries
- Implement `Display` and `Debug` traits for user-facing types

The **key insight** about advanced Rust is that the **type system guides you toward correct concurrent code**. The compiler prevents data races and ensures memory safety even with complex parallel operations. This makes Rust ideal for high-performance systems programming.

In **Part 3**, we'll integrate with Python using PyO3, optimize performance, and build the complete polyglot application.
