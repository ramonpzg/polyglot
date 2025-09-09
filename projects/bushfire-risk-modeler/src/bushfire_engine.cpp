#include "bushfire_engine.hpp"
#include <algorithm>
#include <execution>
#include <numeric>
#include <ranges>
#include <format>
#include <cmath>

namespace bushfire {

// C++20 ranges and modern algorithms
auto BushfireSimulator::get_neighboring_cells(std::size_t x, std::size_t y) const noexcept 
    -> std::vector<std::pair<std::size_t, std::size_t>> {
    
    std::vector<std::pair<std::size_t, std::size_t>> neighbors;
    neighbors.reserve(8); // Maximum 8 neighbors
    
    // Modern range-based approach to generate neighbors
    constexpr std::array<std::pair<int, int>, 8> deltas = {{
        {-1, -1}, {-1, 0}, {-1, 1},
        { 0, -1},          { 0, 1},
        { 1, -1}, { 1, 0}, { 1, 1}
    }};
    
    for (const auto& [dx, dy] : deltas) {
        const auto nx = static_cast<int>(x) + dx;
        const auto ny = static_cast<int>(y) + dy;
        
        if (nx >= 0 && ny >= 0 && nx < static_cast<int>(width_) && ny < static_cast<int>(height_)) {
            neighbors.emplace_back(static_cast<std::size_t>(nx), static_cast<std::size_t>(ny));
        }
    }
    
    return neighbors;
}

void BushfireSimulator::initialize_terrain_from_data(
    std::span<const double> elevations,
    std::span<const double> fuel_loads,
    std::span<const VegetationType> vegetation_types) {
    
    const auto total_cells = width_ * height_;
    if (elevations.size() != total_cells || 
        fuel_loads.size() != total_cells || 
        vegetation_types.size() != total_cells) {
        throw std::invalid_argument("Input data size mismatch with grid dimensions");
    }
    
    // C++20 ranges with zip view (or manual indexing until C++23)
    for (std::size_t i = 0; i < total_cells; ++i) {
        const auto y = i / width_;
        const auto x = i % width_;
        
        auto& cell = grid_[y][x];
        cell.elevation = elevations[i];
        cell.fuel_load = fuel_loads[i];
        cell.vegetation_type = vegetation_types[i];
        cell.fuel_remaining = 1.0;
        
        // Calculate slope from neighboring elevation differences
        const auto neighbors = get_neighboring_cells(x, y);
        if (!neighbors.empty()) {
            const auto elevation_diffs = neighbors 
                | std::views::transform([this, elevation = elevations[i]](const auto& pos) {
                    return std::abs(elevation - grid_[pos.second][pos.first].elevation);
                });
            
            const auto max_diff = std::ranges::max(elevation_diffs);
            cell.slope = std::atan(max_diff / CELL_SIZE_M) * 180.0 / std::numbers::pi;
        }
    }
}

// Template specialization for weather data concept
template<WeatherData W>
constexpr double BushfireSimulator::calculate_fire_danger_index(const W& weather) const noexcept {
    // McArthur Forest Fire Danger Index with drought factor approximation
    const double drought_factor = std::max(1.0, 10.0 - weather.rainfall / 10.0);
    return australian_fire_index::mcarthur_forest_fire_danger_index(
        weather.temperature, weather.humidity, weather.wind_speed, drought_factor);
}

// Explicit instantiation for WeatherCondition
template double BushfireSimulator::calculate_fire_danger_index<WeatherCondition>(const WeatherCondition&) const noexcept;

double BushfireSimulator::calculate_spread_rate(const TerrainCell& cell, const WeatherCondition& weather, 
                                              double wind_effect, double slope_effect) const noexcept {
    // Advanced fire spread model combining multiple factors
    const double base_rate = 0.1; // m/min base spread rate
    
    // Fuel type multiplier
    const double fuel_multiplier = [&cell]() constexpr {
        switch (cell.vegetation_type) {
            case VegetationType::Sparse:  return 0.5;
            case VegetationType::Moderate: return 1.0;
            case VegetationType::Dense:    return 2.0;
            case VegetationType::Extreme:  return 4.0;
        }
        return 1.0;
    }();
    
    // Fuel moisture penalty
    const double fuel_moisture_effect = std::exp(-0.05 * weather.fuel_moisture);
    
    // Combined rate calculation
    return base_rate * fuel_multiplier * fuel_moisture_effect * 
           (1.0 + wind_effect) * (1.0 + slope_effect) * cell.fuel_remaining;
}

constexpr double BushfireSimulator::calculate_wind_effect(const WeatherCondition& weather, double direction_diff) const noexcept {
    // Wind effect based on speed and direction alignment
    const double wind_factor = weather.wind_speed / 10.0; // Normalize
    const double direction_factor = std::cos(direction_diff * std::numbers::pi / 180.0);
    return wind_factor * std::max(0.0, direction_factor);
}

constexpr double BushfireSimulator::calculate_slope_effect(const TerrainCell& from_cell, const TerrainCell& to_cell) const noexcept {
    // Upslope fire spreads faster, downslope slower
    const double elevation_diff = to_cell.elevation - from_cell.elevation;
    const double slope_radians = std::atan(elevation_diff / CELL_SIZE_M);
    return std::tan(slope_radians) * 2.0; // Slope effect coefficient
}

constexpr double BushfireSimulator::calculate_fuel_consumption_rate(const TerrainCell& cell) const noexcept {
    // Rate at which fuel is consumed during burning
    const double base_consumption = 0.02; // 2% per timestep
    const double load_factor = cell.fuel_load / 20.0; // Normalize to typical 20 t/ha
    return base_consumption * (1.0 + load_factor);
}

// The core simulation loop - this is where C++ shines with performance
void BushfireSimulator::simulate_timestep(const WeatherCondition& weather, double dt) {
    if (!weather.is_valid()) {
        throw std::invalid_argument("Invalid weather conditions");
    }
    
    // Create a copy for simultaneous updates (cellular automaton pattern)
    auto new_grid = grid_;
    
    // C++17 parallel execution for performance
    const auto total_cells = width_ * height_;
    std::vector<std::size_t> indices(total_cells);
    std::iota(indices.begin(), indices.end(), 0);
    
    std::for_each(std::execution::par_unseq, indices.begin(), indices.end(), 
        [&, this](std::size_t idx) {
            const auto y = idx / width_;
            const auto x = idx % width_;
            auto& current_cell = new_grid[y][x];
            const auto& original_cell = grid_[y][x];
            
            if (original_cell.is_ignited) {
                // Consume fuel
                const double consumption = calculate_fuel_consumption_rate(original_cell) * dt;
                current_cell.fuel_remaining = std::max(0.0, original_cell.fuel_remaining - consumption);
                
                // If fuel depleted, fire dies out
                if (current_cell.fuel_remaining < 0.01) {
                    current_cell.is_ignited = false;
                    current_cell.burn_intensity = 0.0;
                } else {
                    // Update burn intensity
                    current_cell.burn_intensity = original_cell.fuel_load * 
                        (1.0 - current_cell.fuel_remaining) * 0.1;
                }
                
                // Spread to neighbors
                const auto neighbors = get_neighboring_cells(x, y);
                for (const auto& [nx, ny] : neighbors) {
                    auto& neighbor = new_grid[ny][nx];
                    const auto& orig_neighbor = grid_[ny][nx];
                    
                    if (!orig_neighbor.is_ignited && orig_neighbor.fuel_remaining > 0.01) {
                        // Calculate spread probability
                        const double direction_diff = std::atan2(ny - y, nx - x) * 180.0 / std::numbers::pi - weather.wind_direction;
                        const double wind_effect = calculate_wind_effect(weather, direction_diff);
                        const double slope_effect = calculate_slope_effect(original_cell, orig_neighbor);
                        const double spread_rate = calculate_spread_rate(orig_neighbor, weather, wind_effect, slope_effect);
                        
                        // Probabilistic ignition
                        const double ignition_prob = std::min(1.0, spread_rate * dt * 0.1);
                        std::uniform_real_distribution<double> dist(0.0, 1.0);
                        
                        if (dist(rng_) < ignition_prob) {
                            neighbor.is_ignited = true;
                        }
                    }
                }
            }
        });
    
    grid_ = std::move(new_grid);
}

// High-performance risk surface calculation using modern C++
std::vector<double> BushfireSimulator::calculate_risk_surface(
    const WeatherCondition& weather,
    std::span<const std::pair<std::size_t, std::size_t>> ignition_points) const {
    
    std::vector<double> risk_surface(width_ * height_, 0.0);
    
    // C++20 ranges to process ignition points
    for (const auto& [start_x, start_y] : ignition_points) {
        // Fast distance-based risk calculation
        for (std::size_t y = 0; y < height_; ++y) {
            for (std::size_t x = 0; x < width_; ++x) {
                const double distance = std::sqrt(
                    std::pow(static_cast<double>(x) - static_cast<double>(start_x), 2) +
                    std::pow(static_cast<double>(y) - static_cast<double>(start_y), 2)
                );
                
                const auto& cell = grid_[y][x];
                const double base_risk = calculate_fire_danger_index(weather) / 100.0;
                const double distance_decay = std::exp(-distance / 50.0); // 50-cell effective range
                
                const double fuel_factor = cell.fuel_load / 20.0;
                const double vegetation_factor = [&cell]() constexpr {
                    switch (cell.vegetation_type) {
                        case VegetationType::Sparse:  return 0.3;
                        case VegetationType::Moderate: return 0.6;
                        case VegetationType::Dense:    return 0.9;
                        case VegetationType::Extreme:  return 1.0;
                    }
                    return 0.5;
                }();
                
                const double cell_risk = base_risk * distance_decay * fuel_factor * vegetation_factor;
                risk_surface[y * width_ + x] = std::max(risk_surface[y * width_ + x], cell_risk);
            }
        }
    }
    
    return risk_surface;
}

// Monte Carlo simulation - perfect for parallel C++ execution
std::vector<double> BushfireSimulator::monte_carlo_risk_analysis(
    std::span<const WeatherCondition> weather_scenarios,
    std::span<const std::pair<std::size_t, std::size_t>> potential_ignitions,
    std::size_t num_simulations) const {
    
    std::vector<double> aggregated_risk(width_ * height_, 0.0);
    std::vector<std::size_t> simulation_indices(num_simulations);
    std::iota(simulation_indices.begin(), simulation_indices.end(), 0);
    
    // Thread-local storage for parallel Monte Carlo
    thread_local std::mt19937 local_rng{std::random_device{}()};
    
    std::for_each(std::execution::par_unseq, simulation_indices.begin(), simulation_indices.end(),
        [&](std::size_t sim_idx) {
            // Create local simulator for this thread
            auto local_sim = *this;
            local_sim.rng_.seed(sim_idx);
            
            // Random weather and ignition selection
            std::uniform_int_distribution<std::size_t> weather_dist(0, weather_scenarios.size() - 1);
            std::uniform_int_distribution<std::size_t> ignition_dist(0, potential_ignitions.size() - 1);
            
            const auto& weather = weather_scenarios[weather_dist(local_rng)];
            const auto& ignition = potential_ignitions[ignition_dist(local_rng)];
            
            // Run short simulation
            local_sim.ignite_location(ignition.first, ignition.second);
            
            for (int step = 0; step < 100; ++step) {
                local_sim.simulate_timestep(weather, 0.1);
            }
            
            // Collect results (thread-safe aggregation)
            const auto burned = local_sim.get_burned_areas();
            for (std::size_t i = 0; i < burned.size(); ++i) {
                if (burned[i]) {
                    std::atomic_ref<double>{aggregated_risk[i]} += 1.0 / num_simulations;
                }
            }
        });
    
    return aggregated_risk;
}

// Data extraction using modern C++ ranges and views
std::vector<double> BushfireSimulator::get_burn_intensity_grid() const {
    std::vector<double> intensities;
    intensities.reserve(width_ * height_);
    
    // C++20 ranges approach
    auto intensity_view = grid_ 
        | std::views::join 
        | std::views::transform([](const TerrainCell& cell) { 
            return cell.burn_intensity; 
        });
    
    intensities.assign(intensity_view.begin(), intensity_view.end());
    return intensities;
}

std::vector<bool> BushfireSimulator::get_burned_areas() const {
    std::vector<bool> burned;
    burned.reserve(width_ * height_);
    
    auto burned_view = grid_
        | std::views::join
        | std::views::transform([](const TerrainCell& cell) {
            return cell.fuel_remaining < 0.9; // Consider burned if >10% fuel consumed
        });
    
    burned.assign(burned_view.begin(), burned_view.end());
    return burned;
}

std::vector<double> BushfireSimulator::get_fuel_remaining() const {
    std::vector<double> fuel;
    fuel.reserve(width_ * height_);
    
    auto fuel_view = grid_
        | std::views::join
        | std::views::transform([](const TerrainCell& cell) {
            return cell.fuel_remaining;
        });
    
    fuel.assign(fuel_view.begin(), fuel_view.end());
    return fuel;
}

// Statistics with C++20 constexpr and parallel algorithms
double BushfireSimulator::get_total_burned_area() const noexcept {
    const auto burned_cells = std::transform_reduce(
        std::execution::par_unseq,
        grid_.begin(), grid_.end(),
        0.0,
        std::plus<>{},
        [](const auto& row) {
            return std::transform_reduce(
                row.begin(), row.end(),
                0.0,
                std::plus<>{},
                [](const TerrainCell& cell) {
                    return (cell.fuel_remaining < 0.9) ? (CELL_SIZE_M * CELL_SIZE_M / HECTARE_TO_M2) : 0.0;
                });
        });
    
    return burned_cells;
}

double BushfireSimulator::get_maximum_intensity() const noexcept {
    const auto max_intensity = std::transform_reduce(
        std::execution::par_unseq,
        grid_.begin(), grid_.end(),
        0.0,
        [](double a, double b) { return std::max(a, b); },
        [](const auto& row) {
            return std::transform_reduce(
                row.begin(), row.end(),
                0.0,
                [](double a, double b) { return std::max(a, b); },
                [](const TerrainCell& cell) { return cell.burn_intensity; });
        });
    
    return max_intensity;
}

std::pair<std::size_t, std::size_t> BushfireSimulator::get_fire_perimeter_count() const noexcept {
    std::size_t active_fires = 0;
    std::size_t perimeter_cells = 0;
    
    for (std::size_t y = 0; y < height_; ++y) {
        for (std::size_t x = 0; x < width_; ++x) {
            const auto& cell = grid_[y][x];
            if (cell.is_ignited) {
                ++active_fires;
                
                // Check if this is a perimeter cell
                const auto neighbors = get_neighboring_cells(x, y);
                const bool is_perimeter = std::ranges::any_of(neighbors, [this](const auto& pos) {
                    return !grid_[pos.second][pos.first].is_ignited;
                });
                
                if (is_perimeter) {
                    ++perimeter_cells;
                }
            }
        }
    }
    
    return {active_fires, perimeter_cells};
}

} // namespace bushfire

// Utility functions implementation
namespace bushfire::utility {

std::vector<WeatherCondition> generate_australian_weather_scenarios(std::size_t count, unsigned seed) {
    std::mt19937 gen(seed);
    std::vector<WeatherCondition> scenarios;
    scenarios.reserve(count);
    
    // Australian climate patterns
    std::uniform_real_distribution<double> temp_dist(15.0, 45.0);    // Celsius
    std::uniform_real_distribution<double> humidity_dist(20.0, 80.0); // %
    std::uniform_real_distribution<double> wind_dist(5.0, 50.0);     // km/h
    std::uniform_real_distribution<double> direction_dist(0.0, 360.0); // degrees
    std::uniform_real_distribution<double> rain_dist(0.0, 20.0);     // mm
    
    for (std::size_t i = 0; i < count; ++i) {
        const double temp = temp_dist(gen);
        const double humidity = humidity_dist(gen);
        
        // Realistic correlations: hot weather tends to be drier
        const double adjusted_humidity = humidity * (50.0 - temp) / 50.0;
        const double fuel_moisture = std::max(5.0, adjusted_humidity * 0.3);
        
        scenarios.push_back(WeatherCondition{
            .temperature = temp,
            .humidity = std::max(10.0, adjusted_humidity),
            .wind_speed = wind_dist(gen),
            .wind_direction = direction_dist(gen),
            .rainfall = rain_dist(gen),
            .fuel_moisture = fuel_moisture
        });
    }
    
    return scenarios;
}

// Simulated NSW terrain data (Blue Mountains profile)
std::tuple<std::vector<double>, std::vector<double>, std::vector<VegetationType>> 
load_nsw_terrain_data(std::string_view filename) {
    // In a real implementation, this would load from a file
    // For demo purposes, generate realistic Blue Mountains terrain
    
    const std::size_t width = 200, height = 200;
    std::vector<double> elevations, fuel_loads;
    std::vector<VegetationType> vegetation_types;
    
    elevations.reserve(width * height);
    fuel_loads.reserve(width * height);
    vegetation_types.reserve(width * height);
    
    std::mt19937 gen(42);
    std::normal_distribution<double> elevation_dist(800.0, 300.0); // Blue Mountains ~800m average
    std::uniform_real_distribution<double> fuel_dist(5.0, 25.0);   // tonnes/ha
    std::discrete_distribution<int> veg_dist{30, 40, 25, 5}; // Sparse, Moderate, Dense, Extreme
    
    for (std::size_t y = 0; y < height; ++y) {
        for (std::size_t x = 0; x < width; ++x) {
            // Create realistic elevation with ridges and valleys
            const double base_elevation = elevation_dist(gen);
            const double ridge_effect = 100.0 * std::sin(x * 0.02) * std::cos(y * 0.03);
            elevations.push_back(std::max(200.0, base_elevation + ridge_effect));
            
            // Fuel load correlates with elevation and moisture
            const double moisture_effect = 1.0 + 0.3 * std::sin(y * 0.05);
            fuel_loads.push_back(fuel_dist(gen) * moisture_effect);
            
            // Vegetation type based on elevation and position
            const int veg_type = (elevations.back() > 1000.0) ? 
                std::min(3, veg_dist(gen) + 1) : veg_dist(gen);
            vegetation_types.push_back(static_cast<VegetationType>(veg_type));
        }
    }
    
    return {elevations, fuel_loads, vegetation_types};
}

} // namespace bushfire::utility