#pragma once
#include <vector>
#include <random>
#include <cmath>
#include <ranges>
#include <algorithm>
#include <concepts>
#include <span>
#include <array>
#include <string_view>
#include <execution>
#include <numbers>

namespace bushfire {

// C++20 concepts for type safety and better error messages
template<typename T>
concept Numeric = std::integral<T> || std::floating_point<T>;

template<typename T>
concept WeatherData = requires(T t) {
    { t.temperature } -> std::convertible_to<double>;
    { t.humidity } -> std::convertible_to<double>;
    { t.wind_speed } -> std::convertible_to<double>;
};

// Modern aggregate initialization with designated initializers (C++20)
struct WeatherCondition {
    double temperature{20.0};      // Celsius
    double humidity{50.0};         // 0-100%
    double wind_speed{10.0};       // km/h
    double wind_direction{0.0};    // degrees
    double rainfall{0.0};          // mm in last 24h
    double fuel_moisture{10.0};    // 0-100%
    
    // C++20 spaceship operator for easy comparisons
    auto operator<=>(const WeatherCondition&) const = default;
    
    // Validation using concepts
    constexpr bool is_valid() const noexcept {
        return temperature >= -50.0 && temperature <= 60.0 &&
               humidity >= 0.0 && humidity <= 100.0 &&
               wind_speed >= 0.0 && wind_speed <= 200.0;
    }
};

// Strong typing with enum class and underlying type specification
enum class VegetationType : uint8_t {
    Sparse = 0, Moderate = 1, Dense = 2, Extreme = 3
};

enum class FireDangerRating : uint8_t {
    Low = 0, Moderate = 1, High = 2, VeryHigh = 3, Severe = 4, Extreme = 5, Catastrophic = 6
};

struct TerrainCell {
    double elevation{0.0};           // meters
    double slope{0.0};              // degrees
    double aspect{0.0};             // degrees (0=North, 90=East, etc)
    VegetationType vegetation_type{VegetationType::Moderate};
    double fuel_load{10.0};         // tonnes per hectare
    bool is_ignited{false};
    double burn_intensity{0.0};
    double fuel_remaining{1.0};     // fraction 0-1
    
    // C++20 designated initializers make this beautiful:
    // TerrainCell cell{.elevation = 100.0, .slope = 15.0, .vegetation_type = VegetationType::Dense};
};

// C++20 concepts for grid operations
template<typename Grid>
concept TerrainGrid = requires(Grid g) {
    { g.width() } -> std::convertible_to<std::size_t>;
    { g.height() } -> std::convertible_to<std::size_t>;
    { g(0, 0) } -> std::convertible_to<TerrainCell&>;
};

class BushfireSimulator {
private:
    std::vector<std::vector<TerrainCell>> grid_;
    std::size_t width_, height_;
    mutable std::mt19937 rng_;
    
    // C++20 constexpr and consteval for compile-time constants
    static constexpr double HECTARE_TO_M2 = 10000.0;
    static constexpr double CELL_SIZE_M = 30.0;  // 30m x 30m cells
    static consteval double cells_per_hectare() { return HECTARE_TO_M2 / (CELL_SIZE_M * CELL_SIZE_M); }
    
    // Modern C++ physics calculations with concepts
    template<WeatherData W>
    constexpr double calculate_fire_danger_index(const W& weather) const noexcept;
    
    double calculate_spread_rate(const TerrainCell& cell, const WeatherCondition& weather, 
                               double wind_effect, double slope_effect) const noexcept;
    
    constexpr double calculate_wind_effect(const WeatherCondition& weather, double direction_diff) const noexcept;
    constexpr double calculate_slope_effect(const TerrainCell& from_cell, const TerrainCell& to_cell) const noexcept;
    constexpr double calculate_fuel_consumption_rate(const TerrainCell& cell) const noexcept;
    
    // C++20 ranges for elegant data processing
    auto get_neighboring_cells(std::size_t x, std::size_t y) const noexcept 
        -> std::vector<std::pair<std::size_t, std::size_t>>;
    
public:
    BushfireSimulator(std::size_t w, std::size_t h, unsigned int seed = 42)
        : grid_(h, std::vector<TerrainCell>(w)), width_(w), height_(h), rng_(seed) {}
    
    // C++20 span for zero-copy array access
    void initialize_terrain_from_data(std::span<const double> elevations,
                                    std::span<const double> fuel_loads,
                                    std::span<const VegetationType> vegetation_types);
    
    constexpr void ignite_location(std::size_t x, std::size_t y) noexcept {
        if (x < width_ && y < height_) {
            grid_[y][x].is_ignited = true;
        }
    }
    
    // The heavy computational work - parallel execution with C++17 execution policies
    void simulate_timestep(const WeatherCondition& weather, double dt = 0.1);
    
    // C++20 ranges and views for elegant data transformation
    [[nodiscard]] std::vector<double> calculate_risk_surface(
        const WeatherCondition& weather,
        std::span<const std::pair<std::size_t, std::size_t>> ignition_points) const;
    
    // High-performance monte carlo with parallel algorithms
    [[nodiscard]] std::vector<double> monte_carlo_risk_analysis(
        std::span<const WeatherCondition> weather_scenarios,
        std::span<const std::pair<std::size_t, std::size_t>> potential_ignitions,
        std::size_t num_simulations) const;
    
    // Data extraction using modern C++ ranges and views
    [[nodiscard]] std::vector<double> get_burn_intensity_grid() const;
    [[nodiscard]] std::vector<bool> get_burned_areas() const;
    [[nodiscard]] std::vector<double> get_fuel_remaining() const;
    
    // Statistics with C++20 constexpr improvements
    [[nodiscard]] double get_total_burned_area() const noexcept;  // hectares
    [[nodiscard]] double get_maximum_intensity() const noexcept;
    [[nodiscard]] std::pair<std::size_t, std::size_t> get_fire_perimeter_count() const noexcept;
    
    // C++20 constexpr accessors
    constexpr std::size_t width() const noexcept { return width_; }
    constexpr std::size_t height() const noexcept { return height_; }
    
    // Modern iteration support
    auto cells() const noexcept {
        return grid_ | std::views::join;
    }
    
    // C++23 multidimensional subscript operator
    TerrainCell& operator[](std::size_t x, std::size_t y) noexcept { return grid_[y][x]; }
    const TerrainCell& operator[](std::size_t x, std::size_t y) const noexcept { return grid_[y][x]; }
};

// Australian-specific fire danger rating calculations with modern C++
namespace australian_fire_index {
    
    // C++20 constexpr and mathematical constants
    constexpr double mcarthur_forest_fire_danger_index(double temp, double humidity, 
                                                      double wind_speed, double drought_factor) noexcept {
        using std::numbers::e;
        return 2.0 * std::exp(-0.45 + 0.987 * std::log(drought_factor) 
                             - 0.0345 * humidity + 0.0338 * temp + 0.0234 * wind_speed);
    }
    
    constexpr double grassland_fire_danger_index(double temp, double humidity, double wind_speed, 
                                                double fuel_load, double fuel_moisture) noexcept {
        return 3.35 * fuel_load * std::exp(-0.0231 * fuel_moisture) 
               * (0.054 + 0.209 * wind_speed) * std::exp(0.0365 * temp - 0.0345 * humidity);
    }
    
    // C++20 constexpr string_view lookup
    constexpr std::string_view danger_rating_category(double fdi) noexcept {
        using namespace std::string_view_literals;
        
        if (fdi < 5) return "Low"sv;
        if (fdi < 12) return "Moderate"sv;
        if (fdi < 25) return "High"sv;
        if (fdi < 50) return "Very High"sv;
        if (fdi < 75) return "Severe"sv;
        if (fdi < 100) return "Extreme"sv;
        return "Catastrophic"sv;
    }
    
    constexpr FireDangerRating fdi_to_rating(double fdi) noexcept {
        if (fdi < 5) return FireDangerRating::Low;
        if (fdi < 12) return FireDangerRating::Moderate;
        if (fdi < 25) return FireDangerRating::High;
        if (fdi < 50) return FireDangerRating::VeryHigh;
        if (fdi < 75) return FireDangerRating::Severe;
        if (fdi < 100) return FireDangerRating::Extreme;
        return FireDangerRating::Catastrophic;
    }
}

// C++20 utility functions with ranges
namespace utility {
    // Generate Australian weather patterns
    std::vector<WeatherCondition> generate_australian_weather_scenarios(std::size_t count, unsigned seed = 42);
    
    // Load real Australian terrain data (Blue Mountains, etc.)
    std::tuple<std::vector<double>, std::vector<double>, std::vector<VegetationType>> 
    load_nsw_terrain_data(std::string_view filename);
}

}