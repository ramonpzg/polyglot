#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <pybind11/operators.h>
#include "bushfire_engine.hpp"

namespace py = pybind11;

PYBIND11_MODULE(_core, m) {
    m.doc() = "High-performance bushfire risk modeling engine - C++ core with Python interface";
    
    // Expose modern C++ enums with automatic string conversion
    py::enum_<bushfire::VegetationType>(m, "VegetationType")
        .value("Sparse", bushfire::VegetationType::Sparse)
        .value("Moderate", bushfire::VegetationType::Moderate)
        .value("Dense", bushfire::VegetationType::Dense)
        .value("Extreme", bushfire::VegetationType::Extreme)
        .export_values();
    
    py::enum_<bushfire::FireDangerRating>(m, "FireDangerRating")
        .value("Low", bushfire::FireDangerRating::Low)
        .value("Moderate", bushfire::FireDangerRating::Moderate)
        .value("High", bushfire::FireDangerRating::High)
        .value("VeryHigh", bushfire::FireDangerRating::VeryHigh)
        .value("Severe", bushfire::FireDangerRating::Severe)
        .value("Extreme", bushfire::FireDangerRating::Extreme)
        .value("Catastrophic", bushfire::FireDangerRating::Catastrophic)
        .export_values();
    
    // WeatherCondition with C++20 designated initializers support
    py::class_<bushfire::WeatherCondition>(m, "WeatherCondition")
        .def(py::init<>())
        .def(py::init<double, double, double, double, double, double>(),
             py::arg("temperature") = 20.0,
             py::arg("humidity") = 50.0,
             py::arg("wind_speed") = 10.0,
             py::arg("wind_direction") = 0.0,
             py::arg("rainfall") = 0.0,
             py::arg("fuel_moisture") = 10.0)
        .def_readwrite("temperature", &bushfire::WeatherCondition::temperature)
        .def_readwrite("humidity", &bushfire::WeatherCondition::humidity)
        .def_readwrite("wind_speed", &bushfire::WeatherCondition::wind_speed)
        .def_readwrite("wind_direction", &bushfire::WeatherCondition::wind_direction)
        .def_readwrite("rainfall", &bushfire::WeatherCondition::rainfall)
        .def_readwrite("fuel_moisture", &bushfire::WeatherCondition::fuel_moisture)
        .def("is_valid", &bushfire::WeatherCondition::is_valid)
        .def(py::self == py::self)  // C++20 spaceship operator support
        .def("__repr__", [](const bushfire::WeatherCondition& w) {
            return py::str("WeatherCondition(temp={:.1f}°C, humidity={:.1f}%, wind={:.1f}km/h)")
                .format(w.temperature, w.humidity, w.wind_speed);
        });
    
    // TerrainCell with modern C++ features exposed
    py::class_<bushfire::TerrainCell>(m, "TerrainCell")
        .def(py::init<>())
        .def_readwrite("elevation", &bushfire::TerrainCell::elevation)
        .def_readwrite("slope", &bushfire::TerrainCell::slope)
        .def_readwrite("aspect", &bushfire::TerrainCell::aspect)
        .def_readwrite("vegetation_type", &bushfire::TerrainCell::vegetation_type)
        .def_readwrite("fuel_load", &bushfire::TerrainCell::fuel_load)
        .def_readwrite("is_ignited", &bushfire::TerrainCell::is_ignited)
        .def_readwrite("burn_intensity", &bushfire::TerrainCell::burn_intensity)
        .def_readwrite("fuel_remaining", &bushfire::TerrainCell::fuel_remaining)
        .def("__repr__", [](const bushfire::TerrainCell& c) {
            return py::str("TerrainCell(elev={:.0f}m, fuel={:.1f}t/ha, ignited={})")
                .format(c.elevation, c.fuel_load, c.is_ignited);
        });
    
    // Main BushfireSimulator class - the performance powerhouse
    py::class_<bushfire::BushfireSimulator>(m, "BushfireSimulator")
        .def(py::init<std::size_t, std::size_t, unsigned int>(),
             py::arg("width"), py::arg("height"), py::arg("seed") = 42,
             "Create a new bushfire simulator with specified grid dimensions")
        
        // Terrain initialization with NumPy array support
        .def("initialize_terrain_from_data", 
             [](bushfire::BushfireSimulator& sim,
                py::array_t<double> elevations,
                py::array_t<double> fuel_loads,
                py::array_t<bushfire::VegetationType> vegetation_types) {
                 
                 auto elev_buf = elevations.request();
                 auto fuel_buf = fuel_loads.request();
                 auto veg_buf = vegetation_types.request();
                 
                 if (elev_buf.size != fuel_buf.size || fuel_buf.size != veg_buf.size) {
                     throw std::runtime_error("Array size mismatch");
                 }
                 
                 // Convert to spans for modern C++ interface
                 std::span<const double> elev_span(static_cast<double*>(elev_buf.ptr), elev_buf.size);
                 std::span<const double> fuel_span(static_cast<double*>(fuel_buf.ptr), fuel_buf.size);
                 std::span<const bushfire::VegetationType> veg_span(
                     static_cast<bushfire::VegetationType*>(veg_buf.ptr), veg_buf.size);
                 
                 sim.initialize_terrain_from_data(elev_span, fuel_span, veg_span);
             },
             py::arg("elevations"), py::arg("fuel_loads"), py::arg("vegetation_types"),
             "Initialize terrain from NumPy arrays - zero-copy with C++20 spans")
        
        .def("ignite_location", &bushfire::BushfireSimulator::ignite_location,
             py::arg("x"), py::arg("y"),
             "Start a fire at the specified grid location")
        
        // The performance-critical simulation step
        .def("simulate_timestep", &bushfire::BushfireSimulator::simulate_timestep,
             py::arg("weather"), py::arg("dt") = 0.1,
             "Advance simulation by one timestep - this is where C++ shows its speed")
        
        // High-performance risk analysis functions
        .def("calculate_risk_surface",
             [](const bushfire::BushfireSimulator& sim,
                const bushfire::WeatherCondition& weather,
                py::array_t<std::size_t> ignition_points) -> py::array_t<double> {
                 
                 auto buf = ignition_points.request();
                 if (buf.ndim != 2 || buf.shape[1] != 2) {
                     throw std::runtime_error("Ignition points must be Nx2 array");
                 }
                 
                 std::vector<std::pair<std::size_t, std::size_t>> points;
                 points.reserve(buf.shape[0]);
                 
                 auto ptr = static_cast<std::size_t*>(buf.ptr);
                 for (py::ssize_t i = 0; i < buf.shape[0]; ++i) {
                     points.emplace_back(ptr[i*2], ptr[i*2 + 1]);
                 }
                 
                 auto result = sim.calculate_risk_surface(weather, points);
                 
                 // Return as NumPy array
                 return py::array_t<double>(
                     {sim.height(), sim.width()},
                     {sizeof(double) * sim.width(), sizeof(double)},
                     result.data(),
                     py::cast(sim)
                 );
             },
             py::arg("weather"), py::arg("ignition_points"),
             "Calculate risk surface for given weather and ignition points - returns NumPy array")
        
        // Monte Carlo simulation - parallel C++ at its finest
        .def("monte_carlo_risk_analysis",
             [](const bushfire::BushfireSimulator& sim,
                std::vector<bushfire::WeatherCondition> weather_scenarios,
                py::array_t<std::size_t> potential_ignitions,
                std::size_t num_simulations) -> py::array_t<double> {
                 
                 auto buf = potential_ignitions.request();
                 std::vector<std::pair<std::size_t, std::size_t>> ignitions;
                 ignitions.reserve(buf.shape[0]);
                 
                 auto ptr = static_cast<std::size_t*>(buf.ptr);
                 for (py::ssize_t i = 0; i < buf.shape[0]; ++i) {
                     ignitions.emplace_back(ptr[i*2], ptr[i*2 + 1]);
                 }
                 
                 auto result = sim.monte_carlo_risk_analysis(weather_scenarios, ignitions, num_simulations);
                 
                 return py::array_t<double>(
                     {sim.height(), sim.width()},
                     {sizeof(double) * sim.width(), sizeof(double)},
                     result.data(),
                     py::cast(sim)
                 );
             },
             py::arg("weather_scenarios"), py::arg("potential_ignitions"), py::arg("num_simulations"),
             "Run Monte Carlo risk analysis - massively parallel C++ computation")
        
        // Data extraction functions returning NumPy arrays
        .def("get_burn_intensity_grid", [](const bushfire::BushfireSimulator& sim) {
            auto result = sim.get_burn_intensity_grid();
            return py::array_t<double>(
                {sim.height(), sim.width()},
                {sizeof(double) * sim.width(), sizeof(double)},
                result.data(),
                py::cast(sim)
            );
        }, "Get current burn intensity as NumPy array")
        
        .def("get_burned_areas", [](const bushfire::BushfireSimulator& sim) {
            auto result = sim.get_burned_areas();
            return py::array_t<bool>(
                {sim.height(), sim.width()},
                {sizeof(bool) * sim.width(), sizeof(bool)},
                result.data(),
                py::cast(sim)
            );
        }, "Get burned areas as boolean NumPy array")
        
        .def("get_fuel_remaining", [](const bushfire::BushfireSimulator& sim) {
            auto result = sim.get_fuel_remaining();
            return py::array_t<double>(
                {sim.height(), sim.width()},
                {sizeof(double) * sim.width(), sizeof(double)},
                result.data(),
                py::cast(sim)
            );
        }, "Get remaining fuel as NumPy array")
        
        // Statistics and properties
        .def("get_total_burned_area", &bushfire::BushfireSimulator::get_total_burned_area,
             "Get total burned area in hectares")
        .def("get_maximum_intensity", &bushfire::BushfireSimulator::get_maximum_intensity,
             "Get maximum burn intensity")
        .def("get_fire_perimeter_count", &bushfire::BushfireSimulator::get_fire_perimeter_count,
             "Get (active_fires, perimeter_cells) counts")
        
        .def_property_readonly("width", &bushfire::BushfireSimulator::width)
        .def_property_readonly("height", &bushfire::BushfireSimulator::height)
        
        .def("__repr__", [](const bushfire::BushfireSimulator& sim) {
            return py::str("BushfireSimulator({}x{} grid, {:.1f} ha burned)")
                .format(sim.width(), sim.height(), sim.get_total_burned_area());
        });
    
    // Australian Fire Index functions - constexpr C++ functions exposed
    auto fire_index = m.def_submodule("fire_index", "Australian fire danger index calculations");
    
    fire_index.def("mcarthur_forest_fire_danger_index", 
        &bushfire::australian_fire_index::mcarthur_forest_fire_danger_index,
        py::arg("temperature"), py::arg("humidity"), py::arg("wind_speed"), py::arg("drought_factor"),
        "Calculate McArthur Forest Fire Danger Index");
    
    fire_index.def("grassland_fire_danger_index",
        &bushfire::australian_fire_index::grassland_fire_danger_index,
        py::arg("temperature"), py::arg("humidity"), py::arg("wind_speed"), 
        py::arg("fuel_load"), py::arg("fuel_moisture"),
        "Calculate Grassland Fire Danger Index");
    
    fire_index.def("danger_rating_category",
        &bushfire::australian_fire_index::danger_rating_category,
        py::arg("fdi"),
        "Convert FDI to danger rating category string");
    
    fire_index.def("fdi_to_rating",
        &bushfire::australian_fire_index::fdi_to_rating,
        py::arg("fdi"),
        "Convert FDI to FireDangerRating enum");
    
    // Utility functions
    auto utils = m.def_submodule("utility", "Utility functions for Australian bushfire modeling");
    
    utils.def("generate_australian_weather_scenarios",
        &bushfire::utility::generate_australian_weather_scenarios,
        py::arg("count"), py::arg("seed") = 42,
        "Generate realistic Australian weather scenarios");
    
    utils.def("load_nsw_terrain_data",
        [](const std::string& filename) {
            auto [elevations, fuel_loads, vegetation_types] = 
                bushfire::utility::load_nsw_terrain_data(filename);
            
            return py::make_tuple(
                py::array_t<double>(elevations.size(), elevations.data()),
                py::array_t<double>(fuel_loads.size(), fuel_loads.data()),
                py::array_t<bushfire::VegetationType>(vegetation_types.size(), vegetation_types.data())
            );
        },
        py::arg("filename"),
        "Load NSW terrain data, returns (elevations, fuel_loads, vegetation_types) as NumPy arrays");
    
    // Version and performance info
    m.attr("__version__") = "1.0.0";
    m.attr("__cpp_standard__") = __cplusplus;
    
    #ifdef __cpp_concepts
    m.attr("__has_concepts__") = true;
    #else
    m.attr("__has_concepts__") = false;
    #endif
    
    #ifdef __cpp_ranges
    m.attr("__has_ranges__") = true;
    #else
    m.attr("__has_ranges__") = false;
    #endif
}
