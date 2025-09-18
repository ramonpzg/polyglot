# Rust Tutorial Part 1: Foundations and Safety

*Learn Rust by building a bushfire simulation engine - understanding memory safety, ownership, and basic types*

## Table of Contents
1. [Rust: The Memory-Safe Systems Language](#rust-the-memory-safe-systems-language)
2. [Variables and Mutability](#variables-and-mutability)
3. [Data Types](#data-types)
4. [Ownership: Rust's Superpower](#ownership-rusts-superpower)
5. [References and Borrowing](#references-and-borrowing)
6. [Functions](#functions)
7. [Structs: Custom Data Types](#structs-custom-data-types)
8. [Enums: Powerful Pattern Matching](#enums-powerful-pattern-matching)
9. [Building Our First Simulation Components](#building-our-first-simulation-components)

---

## Rust: The Memory-Safe Systems Language

Think of Rust as a **pedantic but brilliant safety inspector** for your code. It prevents you from making memory mistakes (like using freed memory or data races) by checking everything **at compile time** - before your program even runs.

Unlike garbage-collected languages, Rust gives you **direct control over memory** without the safety risks of languages like C++. It's like having a **race car with advanced safety systems** - maximum performance with maximum safety.

```rust
// This is a complete Rust program
fn main() {
    println!("G'day from Rust!");
    
    // Rust prevents common bugs at compile time
    let temperature = 42.5;
    println!("Current temperature: {}°C", temperature);
}
```

**Key Insight**: Rust's **borrow checker** enforces memory safety rules at compile time. No runtime overhead, no crashes from memory errors.

---

## Variables and Mutability

In Rust, variables are **immutable by default** - like writing with a **permanent marker**. You have to explicitly ask for a **pencil with an eraser** (mutable variable).

### Immutable by Default

```rust
fn main() {
    // Immutable variable - can't be changed
    let station_id = "BROKEN_HILL_001";
    let temperature = 35.2;
    
    // This would cause a compile error:
    // temperature = 36.0;  // ❌ Error: cannot assign twice to immutable variable
    
    println!("Station {}: {}°C", station_id, temperature);
}
```

### Explicit Mutability

```rust
fn main() {
    // Mutable variable - can be changed
    let mut current_temp = 25.0;
    let mut readings_count = 0;
    
    // This works because we declared them as `mut`
    current_temp = 28.5;
    readings_count += 1;
    
    println!("Reading #{}: {}°C", readings_count, current_temp);
}
```

### Shadowing: Reusing Names

```rust
fn main() {
    // Original variable
    let temperature = "32.1";  // String
    
    // Shadow the previous variable with a new type
    let temperature: f64 = temperature.parse().expect("Invalid number");
    
    // Shadow again with a calculation
    let temperature = temperature * 1.8 + 32.0;  // Convert to Fahrenheit
    
    println!("Temperature: {}°F", temperature);
}
```

**Mental Model**: Think of `let` as **creating a new variable** that happens to have the same name, not modifying the existing one.

---

## Data Types

Rust is **statically typed** - every variable has a type known at compile time. But Rust can usually **infer** the type, so you don't have to write it explicitly.

### Numbers

```rust
fn main() {
    // Integer types (signed and unsigned, various sizes)
    let wind_speed: u32 = 45;        // Unsigned 32-bit (0 to ~4 billion)
    let temperature_diff: i32 = -5;  // Signed 32-bit (-2 billion to +2 billion)
    
    // Floating point
    let temperature: f64 = 32.7;     // 64-bit float (sensible default)
    let humidity: f32 = 65.2;        // 32-bit float (less precision)
    
    // Type inference usually works
    let rainfall = 12.5;             // Rust infers f64
    let day_count = 7;               // Rust infers i32
    
    // Explicit type annotations when needed
    let station_count: usize = 150;  // usize for array indices/sizes
    
    println!("Wind: {} km/h, Temp: {}°C", wind_speed, temperature);
}
```

### Strings

Rust has **two main string types** - think of them as **different tools for different jobs**:

```rust
fn main() {
    // String literals (&str) - like a "read-only view" of text
    let region: &str = "Queensland";           // Lives in program binary
    let message: &str = "Fire danger: HIGH";   // Can't be modified
    
    // String objects - like a "text editor buffer" 
    let mut station_name = String::new();        // Empty, growable string
    station_name.push_str("Broken Hill");        // Can add text
    station_name.push_str(" Weather Station");   // Keep adding
    
    // Converting between types
    let region_owned: String = region.to_string();     // &str → String
    let station_ref: &str = &station_name;             // String → &str
    
    // String formatting
    let report = format!("Station: {}, Region: {}", station_name, region);
    
    println!("{}", report);
}
```

**Analogy**: `&str` is like a **bookmark pointing to text in a book** (can't change the book). `String` is like a **notepad where you can write and erase**.

### Booleans and Characters

```rust
fn main() {
    // Booleans
    let is_dangerous = true;
    let system_online = false;
    let fire_risk = temperature > 40.0 && humidity < 20.0;
    
    // Characters (Unicode, 4 bytes)
    let fire_emoji = '🔥';
    let degree_symbol = '°';
    let letter = 'A';
    
    println!("Fire risk: {} {}", fire_risk, fire_emoji);
}
```

### Arrays and Tuples

```rust
fn main() {
    // Arrays - fixed size, same type
    let temperatures = [25.1, 28.3, 32.7, 29.9, 31.2];  // [f64; 5]
    let regions: [&str; 5] = ["QLD", "NSW", "VIC", "SA", "WA"];
    
    // Accessing array elements
    let first_temp = temperatures[0];
    let last_region = regions[4];
    
    // Arrays are stack-allocated and very fast
    println!("First temperature: {}°C", first_temp);
    
    // Tuples - fixed size, different types
    let station_info = ("Broken Hill", -31.95, 141.46, 315.0);  // (name, lat, lng, elevation)
    
    // Destructuring tuples
    let (name, latitude, longitude, elevation) = station_info;
    let latitude_only = station_info.1;  // Access by index
    
    println!("Station: {} at ({}, {}) {}m elevation", 
             name, latitude, longitude, elevation);
}
```

---

## Ownership: Rust's Superpower

**Ownership** is Rust's secret sauce for memory safety. Think of it like **having exactly one person responsible for each piece of data** at any time.

### The Three Rules

1. **Each value has exactly one owner**
2. **When the owner goes out of scope, the value is dropped**  
3. **There can only be one owner at a time**

```rust
fn main() {
    // Rule 1: Each value has an owner
    let station_name = String::from("Darwin Weather Station");  // station_name owns the string
    
    // Rule 3: Only one owner at a time
    let new_owner = station_name;  // Ownership MOVES to new_owner
    
    // println!("{}", station_name);  // ❌ Error! station_name no longer owns the data
    println!("{}", new_owner);        // ✅ This works
    
} // Rule 2: new_owner goes out of scope, string memory is automatically freed
```

### Move Semantics

```rust
fn process_station_data(data: String) {  // Takes ownership
    println!("Processing: {}", data);
}  // data is dropped here

fn main() {
    let weather_data = String::from("Temperature: 32°C, Humidity: 45%");
    
    process_station_data(weather_data);  // Ownership moves into function
    
    // println!("{}", weather_data);  // ❌ Error! weather_data is no longer valid
}
```

**Mental Model**: Think of ownership like **passing a physical object**. If you give someone your phone, you no longer have it.

### Copy Types

Some types implement `Copy` - they're **duplicated** instead of moved:

```rust
fn main() {
    // These types implement Copy (they're small and cheap to duplicate)
    let temperature = 32.5;  // f64
    let count = 10;          // i32
    let is_hot = true;       // bool
    
    let temp_copy = temperature;  // Creates a copy, doesn't move
    
    println!("Original: {}, Copy: {}", temperature, temp_copy);  // Both still valid
}
```

### Clone for Expensive Copies

```rust
fn main() {
    let original_data = String::from("Extensive weather readings...");
    
    // Explicitly clone when you need a copy
    let backup_data = original_data.clone();  // Expensive operation, but explicit
    
    println!("Original: {}", original_data);  // Still valid
    println!("Backup: {}", backup_data);      // Also valid
}
```

---

## References and Borrowing

**Borrowing** lets you **use data without taking ownership** - like borrowing a friend's book instead of taking it permanently.

### Immutable References

```rust
fn calculate_fire_risk(temp: &f64, humidity: &f64, wind: &f64) -> &'static str {
    if *temp > 40.0 && *humidity < 20.0 && *wind > 30.0 {
        "EXTREME"
    } else if *temp > 30.0 && *humidity < 40.0 {
        "HIGH"  
    } else {
        "MODERATE"
    }
}

fn main() {
    let temperature = 42.5;
    let humidity = 15.0;
    let wind_speed = 45.0;
    
    // Borrow the values (pass references)
    let risk = calculate_fire_risk(&temperature, &humidity, &wind_speed);
    
    // Original values still accessible
    println!("Conditions: {}°C, {}% humidity, {} km/h wind", 
             temperature, humidity, wind_speed);
    println!("Fire risk: {}", risk);
}
```

### Mutable References

```rust
fn update_temperature(temp: &mut f64, adjustment: f64) {
    *temp += adjustment;  // Dereference with * to modify the value
}

fn main() {
    let mut current_temp = 25.0;
    
    // Borrow mutably
    update_temperature(&mut current_temp, 3.5);
    
    println!("Updated temperature: {}°C", current_temp);  // 28.5°C
}
```

### Borrowing Rules

```rust
fn main() {
    let mut data = String::from("Weather data");
    
    // Rule 1: Either one mutable reference OR any number of immutable references
    
    // This works - multiple immutable references
    let read1 = &data;
    let read2 = &data;
    println!("{} and {}", read1, read2);
    
    // This works - one mutable reference (after immutable ones are done)
    let write = &mut data;
    write.push_str(" - updated");
    println!("{}", write);
    
    // This would NOT work - can't mix mutable and immutable:
    // let read3 = &data;        // Immutable borrow
    // let write2 = &mut data;   // ❌ Error! Can't have both
}
```

**Mental Model**: Think of borrowing like **library rules**:
- Multiple people can **read** the same book simultaneously
- Only **one person** can **write in** the book at a time
- You can't **read** while someone is **writing** (prevents data races)

---

## Functions

Functions in Rust are like **specialized tools** with clear contracts about what they take and return.

### Basic Functions

```rust
// Function that takes ownership
fn process_reading(data: String) -> String {
    format!("Processed: {}", data)
}

// Function that borrows data
fn analyze_reading(data: &String) -> f64 {
    data.len() as f64 * 1.5  // Some analysis calculation
}

// Function with multiple parameters and early return
fn calculate_heat_index(temp_c: f64, humidity: f64) -> Option<f64> {
    if temp_c < 27.0 {
        return None;  // Heat index not applicable for cool temperatures
    }
    
    let temp_f = temp_c * 9.0 / 5.0 + 32.0;
    
    // Simplified heat index calculation
    let hi = -42.379 + 2.04901523 * temp_f + 10.14333127 * humidity;
    Some((hi - 32.0) * 5.0 / 9.0)  // Convert back to Celsius
}

fn main() {
    let reading = String::from("Temperature: 35°C");
    
    // Function that takes ownership
    let processed = process_reading(reading);
    // println!("{}", reading);  // ❌ reading is no longer valid
    
    // Function that borrows
    let analysis = analyze_reading(&processed);
    println!("{}, Analysis: {}", processed, analysis);  // processed still valid
    
    // Function with Option return
    if let Some(heat_index) = calculate_heat_index(35.0, 75.0) {
        println!("Heat index: {:.1}°C", heat_index);
    } else {
        println!("Heat index not applicable");
    }
}
```

### Closures: Inline Functions

```rust
fn main() {
    let temperatures = vec![25.1, 28.3, 32.7, 29.9, 31.2];
    
    // Closure that captures environment
    let threshold = 30.0;
    let hot_days = temperatures.iter()
        .filter(|&temp| *temp > threshold)  // Closure captures 'threshold'
        .count();
    
    println!("Hot days (>{}°C): {}", threshold, hot_days);
    
    // Closure for transformation
    let fahrenheit_temps: Vec<f64> = temperatures.iter()
        .map(|&c| c * 9.0 / 5.0 + 32.0)  // Convert to Fahrenheit
        .collect();
    
    println!("Fahrenheit: {:?}", fahrenheit_temps);
}
```

---

## Structs: Custom Data Types

Structs are like **blueprints** for creating custom data types that group related information together.

### Basic Structs

```rust
// Weather station data structure
struct WeatherStation {
    id: String,
    location: String,
    latitude: f64,
    longitude: f64,
    elevation: f64,
    active: bool,
}

// Current weather reading
struct WeatherReading {
    temperature: f64,
    humidity: f64,
    wind_speed: f64,
    wind_direction: u16,  // Degrees 0-359
    pressure: f64,
    timestamp: u64,       // Unix timestamp
}

fn main() {
    // Create a weather station
    let station = WeatherStation {
        id: String::from("BROKEN_HILL_001"),
        location: String::from("Broken Hill, NSW"),
        latitude: -31.95,
        longitude: 141.46,
        elevation: 315.0,
        active: true,
    };
    
    // Create a weather reading
    let reading = WeatherReading {
        temperature: 32.7,
        humidity: 45.0,
        wind_speed: 25.0,
        wind_direction: 225,  // Southwest
        pressure: 1013.25,
        timestamp: 1640995200,  // Example timestamp
    };
    
    // Access struct fields
    println!("Station: {} ({})", station.id, station.location);
    println!("Reading: {}°C, {}% humidity", reading.temperature, reading.humidity);
}
```

### Methods and Associated Functions

```rust
impl WeatherStation {
    // Associated function (like a constructor)
    fn new(id: String, location: String, lat: f64, lng: f64, elevation: f64) -> WeatherStation {
        WeatherStation {
            id,
            location,
            latitude: lat,
            longitude: lng,
            elevation,
            active: true,
        }
    }
    
    // Method (takes &self)
    fn is_operational(&self) -> bool {
        self.active && self.elevation > 0.0
    }
    
    // Mutable method (takes &mut self)
    fn deactivate(&mut self) {
        self.active = false;
    }
    
    // Method that takes ownership (takes self)
    fn shutdown(self) -> String {
        format!("Station {} ({}) has been shut down", self.id, self.location)
    }
}

impl WeatherReading {
    // Calculate apparent temperature (feels like)
    fn apparent_temperature(&self) -> f64 {
        // Simplified apparent temperature calculation
        let vapor_pressure = (self.humidity / 100.0) * 6.105 * 
            (17.27 * self.temperature / (237.7 + self.temperature)).exp();
        
        self.temperature + 0.33 * vapor_pressure - 0.7 * self.wind_speed - 4.0
    }
    
    // Fire danger assessment
    fn fire_danger_level(&self) -> &'static str {
        let temp = self.temperature;
        let humidity = self.humidity;
        let wind = self.wind_speed;
        
        if temp > 40.0 && humidity < 15.0 && wind > 40.0 {
            "CATASTROPHIC"
        } else if temp > 35.0 && humidity < 20.0 && wind > 30.0 {
            "EXTREME"
        } else if temp > 30.0 && humidity < 30.0 && wind > 20.0 {
            "SEVERE"
        } else if temp > 25.0 && humidity < 40.0 {
            "HIGH"
        } else {
            "MODERATE"
        }
    }
}

fn main() {
    // Use associated function
    let mut station = WeatherStation::new(
        String::from("ALICE_SPRINGS_001"),
        String::from("Alice Springs, NT"),
        -23.70, 
        133.88, 
        545.0
    );
    
    // Use methods
    println!("Station operational: {}", station.is_operational());
    station.deactivate();
    println!("Station operational: {}", station.is_operational());
    
    // Create weather reading
    let reading = WeatherReading {
        temperature: 38.5,
        humidity: 25.0,
        wind_speed: 35.0,
        wind_direction: 180,
        pressure: 1008.2,
        timestamp: 1640995800,
    };
    
    // Use reading methods
    println!("Apparent temperature: {:.1}°C", reading.apparent_temperature());
    println!("Fire danger: {}", reading.fire_danger_level());
}
```

### Tuple Structs and Unit Structs

```rust
// Tuple struct - struct with unnamed fields
struct Coordinates(f64, f64);  // (latitude, longitude)
struct Temperature(f64);       // Wrapper around f64
struct WindReading(f64, u16);  // (speed, direction)

// Unit struct - no fields, useful for markers
struct FireAlert;

fn main() {
    let location = Coordinates(-31.95, 141.46);
    let current_temp = Temperature(32.7);
    let wind = WindReading(25.0, 225);
    
    // Access tuple struct fields by index
    println!("Location: {:.2}, {:.2}", location.0, location.1);
    println!("Temperature: {}°C", current_temp.0);
    println!("Wind: {} km/h from {}°", wind.0, wind.1);
    
    let alert = FireAlert;  // Unit struct instance
}
```

---

## Enums: Powerful Pattern Matching

Enums in Rust are **much more powerful** than in many other languages. They can hold data and represent **multiple possible states** of something.

### Basic Enums

```rust
// Fire danger levels
enum FireDangerLevel {
    Low,
    Moderate,
    High,
    VeryHigh,
    Severe,
    Extreme,
    Catastrophic,
}

// Weather conditions
enum WeatherCondition {
    Clear,
    PartlyCloudy,
    Overcast,
    Rain,
    Storm,
    Fog,
}

fn danger_color(level: &FireDangerLevel) -> &'static str {
    match level {
        FireDangerLevel::Low => "green",
        FireDangerLevel::Moderate => "blue", 
        FireDangerLevel::High => "yellow",
        FireDangerLevel::VeryHigh => "orange",
        FireDangerLevel::Severe => "red",
        FireDangerLevel::Extreme => "deep-red",
        FireDangerLevel::Catastrophic => "maroon",
    }
}

fn main() {
    let current_danger = FireDangerLevel::Severe;
    let condition = WeatherCondition::PartlyCloudy;
    
    println!("Current fire danger: {} ({})", 
             danger_color(&current_danger), 
             std::mem::discriminant(&current_danger) as u8);  // Get variant index
}
```

### Enums with Data

```rust
// Enum variants can hold data
enum SensorReading {
    Temperature(f64),                    // Single value
    Humidity(f64),                      // Single value
    Wind { speed: f64, direction: u16 }, // Named fields (like struct)
    Pressure(f64, String),              // Multiple values
    Error(String),                      // Error message
}

// Result-like enum for operations that might fail
enum MeasurementResult {
    Success(f64),
    CalibrationError,
    SensorOffline,
    InvalidReading(String),
}

fn process_sensor_reading(reading: SensorReading) {
    match reading {
        SensorReading::Temperature(temp) => {
            println!("Temperature: {}°C", temp);
            if temp > 40.0 {
                println!("⚠️ High temperature alert!");
            }
        },
        SensorReading::Humidity(humidity) => {
            println!("Humidity: {}%", humidity);
        },
        SensorReading::Wind { speed, direction } => {
            println!("Wind: {} km/h from {}°", speed, direction);
        },
        SensorReading::Pressure(value, unit) => {
            println!("Pressure: {} {}", value, unit);
        },
        SensorReading::Error(msg) => {
            println!("❌ Sensor error: {}", msg);
        }
    }
}

fn handle_measurement(result: MeasurementResult) -> Option<f64> {
    match result {
        MeasurementResult::Success(value) => {
            println!("✅ Measurement successful: {}", value);
            Some(value)
        },
        MeasurementResult::CalibrationError => {
            println!("❌ Sensor needs calibration");
            None
        },
        MeasurementResult::SensorOffline => {
            println!("❌ Sensor is offline");
            None
        },
        MeasurementResult::InvalidReading(reason) => {
            println!("❌ Invalid reading: {}", reason);
            None
        },
    }
}

fn main() {
    let readings = vec![
        SensorReading::Temperature(32.7),
        SensorReading::Wind { speed: 25.0, direction: 225 },
        SensorReading::Error(String::from("Communication timeout")),
    ];
    
    for reading in readings {
        process_sensor_reading(reading);
    }
    
    let measurement = MeasurementResult::Success(42.3);
    if let Some(value) = handle_measurement(measurement) {
        println!("Got valid measurement: {}", value);
    }
}
```

### Option and Result: Essential Enums

```rust
// Option<T> - represents something that might be None
fn find_station(id: &str, stations: &[WeatherStation]) -> Option<&WeatherStation> {
    stations.iter().find(|station| station.id == id)
}

// Result<T, E> - represents operations that might fail  
fn parse_temperature(input: &str) -> Result<f64, String> {
    match input.parse::<f64>() {
        Ok(temp) if temp > -100.0 && temp < 100.0 => Ok(temp),
        Ok(_) => Err(format!("Temperature {} out of valid range", input)),
        Err(_) => Err(format!("'{}' is not a valid number", input)),
    }
}

fn main() {
    // Working with Option
    let stations = vec![
        WeatherStation::new(
            String::from("SYD_001"), 
            String::from("Sydney"), 
            -33.87, 151.21, 58.0
        )
    ];
    
    match find_station("SYD_001", &stations) {
        Some(station) => println!("Found: {}", station.location),
        None => println!("Station not found"),
    }
    
    // Using if let for cleaner Option handling
    if let Some(station) = find_station("SYD_001", &stations) {
        println!("Station {} is at elevation {}m", station.id, station.elevation);
    }
    
    // Working with Result
    let temp_inputs = vec!["32.5", "invalid", "-150", "42.7"];
    
    for input in temp_inputs {
        match parse_temperature(input) {
            Ok(temp) => println!("Valid temperature: {}°C", temp),
            Err(error) => println!("Error parsing '{}': {}", input, error),
        }
    }
}
```

---

## Building Our First Simulation Components

Let's put everything together by building the foundational types for our bushfire simulation:

```rust
// Cell states in our simulation grid
#[derive(Clone, Copy, Debug, PartialEq)]
enum CellState {
    Empty,
    Vegetation,
    Burning,
    Burnt,
}

// Environmental conditions affecting fire spread
#[derive(Debug)]
struct Environment {
    wind_speed: f64,      // km/h
    wind_direction: f64,  // radians
    humidity: f64,        // percentage
    temperature: f64,     // celsius
}

// A single cell in our simulation grid
#[derive(Debug)]
struct Cell {
    state: CellState,
    fuel_load: f64,       // 0.0 to 1.0
    moisture: f64,        // 0.0 to 1.0
}

// The simulation grid
struct FireGrid {
    width: usize,
    height: usize,
    cells: Vec<Vec<Cell>>,
    environment: Environment,
    step_count: u32,
}

impl Cell {
    fn new(state: CellState) -> Self {
        Cell {
            state,
            fuel_load: 0.75,    // Default fuel load
            moisture: 0.3,      // Default moisture
        }
    }
    
    // Check if this cell can catch fire
    fn can_ignite(&self) -> bool {
        matches!(self.state, CellState::Vegetation) && 
        self.fuel_load > 0.1 && 
        self.moisture < 0.8
    }
    
    // Calculate how likely this cell is to catch fire
    fn ignition_probability(&self, neighbors_burning: u8, env: &Environment) -> f64 {
        if !self.can_ignite() {
            return 0.0;
        }
        
        // Base probability
        let mut prob = 0.1;
        
        // More burning neighbors = higher probability
        prob += neighbors_burning as f64 * 0.2;
        
        // Environmental factors
        prob *= 1.0 + (env.wind_speed / 50.0);           // Wind increases spread
        prob *= 1.0 + (1.0 - env.humidity / 100.0);     // Low humidity increases spread
        prob *= 1.0 + ((env.temperature - 20.0) / 50.0).max(0.0); // High temp increases spread
        
        // Cell-specific factors
        prob *= self.fuel_load;                          // More fuel = easier ignition
        prob *= 1.0 - self.moisture;                     // Less moisture = easier ignition
        
        prob.min(0.95) // Cap at 95%
    }
}

impl Environment {
    fn new(wind_speed: f64, wind_direction: f64, humidity: f64, temperature: f64) -> Self {
        Environment {
            wind_speed,
            wind_direction,
            humidity,
            temperature,
        }
    }
    
    // Australian fire danger rating
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
            "VERY_HIGH"
        } else if temp > 20.0 && humidity < 60.0 {
            "HIGH"
        } else {
            "MODERATE"
        }
    }
}

impl FireGrid {
    fn new(width: usize, height: usize, environment: Environment) -> Self {
        // Initialize grid with vegetation
        let mut cells = Vec::with_capacity(height);
        for _ in 0..height {
            let mut row = Vec::with_capacity(width);
            for _ in 0..width {
                // 80% chance of vegetation, 20% empty
                let state = if rand::random::<f64>() < 0.8 {
                    CellState::Vegetation
                } else {
                    CellState::Empty
                };
                row.push(Cell::new(state));
            }
            cells.push(row);
        }
        
        FireGrid {
            width,
            height,
            cells,
            environment,
            step_count: 0,
        }
    }
    
    // Start a fire at specific coordinates
    fn ignite(&mut self, x: usize, y: usize) -> Result<(), String> {
        if x >= self.width || y >= self.height {
            return Err(format!("Coordinates ({}, {}) out of bounds", x, y));
        }
        
        let cell = &mut self.cells[y][x];
        match cell.state {
            CellState::Vegetation => {
                cell.state = CellState::Burning;
                Ok(())
            },
            CellState::Empty => Err("Cannot ignite empty cell".to_string()),
            CellState::Burning => Err("Cell is already burning".to_string()),
            CellState::Burnt => Err("Cell is already burnt".to_string()),
        }
    }
    
    // Count burning neighbors for a cell
    fn burning_neighbors(&self, x: usize, y: usize) -> u8 {
        let mut count = 0;
        
        // Check all 8 neighbors (including diagonals)
        for dy in -1i32..=1 {
            for dx in -1i32..=1 {
                if dx == 0 && dy == 0 {
                    continue; // Skip the cell itself
                }
                
                let nx = (x as i32 + dx) as usize;
                let ny = (y as i32 + dy) as usize;
                
                // Check bounds and if neighbor is burning
                if nx < self.width && ny < self.height {
                    if matches!(self.cells[ny][nx].state, CellState::Burning) {
                        count += 1;
                    }
                }
            }
        }
        
        count
    }
    
    // Get statistics about current state
    fn statistics(&self) -> (u32, u32, u32, u32, u32) {
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
        
        (self.step_count, empty, vegetation, burning, burnt)
    }
    
    // Print current state (for debugging)
    fn print_state(&self) {
        println!("Step {}: Fire Danger = {}", 
                 self.step_count, 
                 self.environment.fire_danger_level());
        
        for row in &self.cells {
            for cell in row {
                let symbol = match cell.state {
                    CellState::Empty => " ",
                    CellState::Vegetation => "🌿",
                    CellState::Burning => "🔥",
                    CellState::Burnt => "⚫",
                };
                print!("{}", symbol);
            }
            println!();
        }
        println!();
    }
}

// Example usage
fn main() {
    println!("🔥 Bushfire Simulation - Part 1 Foundation");
    
    // Create environment conditions
    let environment = Environment::new(
        45.0,   // 45 km/h wind
        0.0,    // Wind from the west
        20.0,   // 20% humidity
        38.0,   // 38°C temperature
    );
    
    println!("Environmental conditions:");
    println!("  Wind: {} km/h", environment.wind_speed);
    println!("  Humidity: {}%", environment.humidity);
    println!("  Temperature: {}°C", environment.temperature);
    println!("  Fire danger: {}", environment.fire_danger_level());
    
    // Create simulation grid
    let mut grid = FireGrid::new(10, 10, environment);
    
    // Ignite a fire in the center
    match grid.ignite(5, 5) {
        Ok(()) => println!("🔥 Fire started at center (5, 5)"),
        Err(e) => println!("❌ Failed to start fire: {}", e),
    }
    
    // Show initial state
    grid.print_state();
    
    // Show statistics
    let (step, empty, vegetation, burning, burnt) = grid.statistics();
    println!("Statistics:");
    println!("  Step: {}", step);
    println!("  Empty: {}", empty);
    println!("  Vegetation: {}", vegetation);
    println!("  Burning: {}", burning);
    println!("  Burnt: {}", burnt);
}

// We'll need this for random generation
use rand;
```

---

## Key Rust Concepts Summary - Part 1

**Ownership & Borrowing:**
- Each value has exactly one owner
- Borrowing lets you use data without taking ownership  
- `&T` for immutable references, `&mut T` for mutable references
- Compiler prevents data races and memory errors at compile time

**Variables & Mutability:**
- Variables are immutable by default (`let`)
- Use `let mut` for mutable variables
- Shadowing lets you reuse variable names with `let`

**Types:**
- Rust is statically typed but has good type inference
- `&str` vs `String` - borrowed vs owned strings
- Arrays `[T; N]` are fixed-size, Vectors `Vec<T>` are growable

**Functions:**
- Take parameters by value (move), reference (`&T`), or mutable reference (`&mut T`)
- Return types specified after `->`
- Closures capture environment variables

**Structs:**
- Group related data together
- Methods defined in `impl` blocks
- Associated functions (like constructors) don't take `self`

**Enums:**
- Much more powerful than in other languages
- Can hold data in variants
- `Option<T>` and `Result<T, E>` are essential enums
- Pattern matching with `match` is exhaustive

**Sensible Defaults:**
- Use `let` by default, `let mut` only when needed
- Prefer borrowing (`&`) over taking ownership when possible
- Use `match` for exhaustive pattern matching
- Handle `Option` and `Result` explicitly - don't ignore errors
- Use descriptive enum variants and struct field names
- Keep functions small and focused

The **key insight** about Rust is that it moves memory safety checks to **compile time**. The compiler is strict but helpful - it prevents entire categories of bugs that would crash your program at runtime. Once your Rust code compiles, it's very unlikely to have memory safety issues.

In **Part 2**, we'll explore collections, error handling, traits, and concurrency - the tools that make Rust powerful for systems programming.
