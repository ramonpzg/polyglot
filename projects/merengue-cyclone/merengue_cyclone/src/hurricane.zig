const std = @import("std");
const math = std.math;

// Constants for hurricane modeling
const EARTH_RADIUS_KM: f64 = 6371.0;
const CORIOLIS_CONSTANT: f64 = 7.2921e-5;
const SEA_WATER_DENSITY: f64 = 1025.0; // kg/m³

// Structure for hurricane position and metrics
const HurricanePoint = extern struct {
    lat: f64,
    lon: f64,
    pressure: f64, // millibars
    wind_speed: f64, // km/h
    timestamp: i64,
};

// Haversine distance calculation - critical for tracking
export fn haversine_distance(lat1: f64, lon1: f64, lat2: f64, lon2: f64) f64 {
    const lat1_rad = lat1 * math.pi / 180.0;
    const lat2_rad = lat2 * math.pi / 180.0;
    const dlat = (lat2 - lat1) * math.pi / 180.0;
    const dlon = (lon2 - lon1) * math.pi / 180.0;

    const a = math.sin(dlat / 2) * math.sin(dlat / 2) +
        math.cos(lat1_rad) * math.cos(lat2_rad) *
            math.sin(dlon / 2) * math.sin(dlon / 2);
    const c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a));

    return EARTH_RADIUS_KM * c;
}

// Calculate Coriolis parameter at given latitude
export fn coriolis_parameter(latitude: f64) f64 {
    const lat_rad = latitude * math.pi / 180.0;
    return 2 * CORIOLIS_CONSTANT * math.sin(lat_rad);
}

// Estimate hurricane intensity based on sea surface temperature
// Using simplified Emanuel's Maximum Potential Intensity theory
export fn calculate_intensity(sst: f64, environmental_pressure: f64) f64 {
    // SST in Celsius, pressure in millibars
    if (sst < 26.5) return 0.0; // Below threshold for hurricane formation

    const sst_kelvin = sst + 273.15;
    const efficiency = (sst_kelvin - 250.0) / sst_kelvin;
    const pressure_diff = 1013.0 - environmental_pressure;

    // Simplified MPI calculation
    const max_wind = math.sqrt(efficiency * pressure_diff * 100.0) * 3.6; // Convert to km/h
    return @min(max_wind, 300.0); // Cap at Category 5 maximum
}

// Fast batch processing of hurricane track points
export fn process_track_batch(
    points: [*]const HurricanePoint,
    count: usize,
    distances: [*]f64,
    speeds: [*]f64,
) void {
    if (count < 2) return;

    var i: usize = 0;
    while (i < count - 1) : (i += 1) {
        const p1 = points[i];
        const p2 = points[i + 1];

        // Calculate distance between consecutive points
        distances[i] = haversine_distance(p1.lat, p1.lon, p2.lat, p2.lon);

        // Calculate speed (km/h)
        const time_diff = @as(f64, @floatFromInt(p2.timestamp - p1.timestamp)) / 3600.0;
        speeds[i] = if (time_diff > 0) distances[i] / time_diff else 0.0;
    }
}

// Predict next position using simplified beta-advection model
export fn predict_next_position(
    current: HurricanePoint,
    prev: HurricanePoint,
    beta_drift: f64,
) HurricanePoint {
    // Calculate current velocity
    const dlat = current.lat - prev.lat;
    const dlon = current.lon - prev.lon;
    const dt = @as(f64, @floatFromInt(current.timestamp - prev.timestamp)) / 3600.0;

    if (dt <= 0) return current;

    const velocity_lat = dlat / dt;
    const velocity_lon = dlon / dt;

    // Apply beta drift (westward and poleward tendency)
    const coriolis = coriolis_parameter(current.lat);
    const beta_effect = beta_drift * coriolis;

    // Simple forward extrapolation with beta correction
    var next = HurricanePoint{
        .lat = current.lat + velocity_lat - beta_effect * 0.1,
        .lon = current.lon + velocity_lon - beta_effect * 0.2,
        .pressure = current.pressure,
        .wind_speed = current.wind_speed,
        .timestamp = current.timestamp + 3600, // 1 hour forward
    };

    // Apply latitude bounds
    next.lat = @max(-60.0, @min(60.0, next.lat));

    return next;
}

// Calculate storm surge potential (simplified SLOSH-like model)
export fn estimate_storm_surge(
    wind_speed: f64, // km/h
    central_pressure: f64, // millibars
    bathymetry: f64, // average depth in meters
    coastline_angle: f64, // degrees from perpendicular approach
) f64 {
    // Convert wind speed to m/s
    const wind_ms = wind_speed / 3.6;

    // Pressure deficit from normal
    const pressure_deficit = 1013.0 - central_pressure;

    // Wind stress coefficient
    const cd = 0.0025;
    const wind_stress = cd * SEA_WATER_DENSITY * wind_ms * wind_ms;

    // Bathymetry effect (shallower water = higher surge)
    const depth_factor = 50.0 / @max(bathymetry, 10.0);

    // Angle effect (perpendicular approach = maximum surge)
    const angle_rad = coastline_angle * math.pi / 180.0;
    const angle_factor = math.cos(angle_rad);

    // Simplified surge calculation
    const surge = (pressure_deficit * 0.01 +
        wind_stress * 0.0001 * depth_factor) *
        angle_factor;

    return @max(0.0, @min(surge, 10.0)); // Cap at realistic maximum
}

// Batch calculation for performance testing
export fn batch_intensity_calculation(
    sst_values: [*]const f64,
    pressure_values: [*]const f64,
    results: [*]f64,
    count: usize,
) void {
    var i: usize = 0;
    while (i < count) : (i += 1) {
        results[i] = calculate_intensity(sst_values[i], pressure_values[i]);
    }
}

// Calculate Accumulated Cyclone Energy (ACE) for a track
export fn calculate_ace(
    points: [*]const HurricanePoint,
    count: usize,
) f64 {
    var ace: f64 = 0.0;
    var i: usize = 0;

    while (i < count) : (i += 1) {
        const wind_knots = points[i].wind_speed * 0.539957; // Convert km/h to knots
        if (wind_knots >= 35.0) { // Tropical storm threshold
            ace += (wind_knots * wind_knots) / 10000.0;
        }
    }

    return ace;
}

// Performance benchmark function
export fn benchmark_haversine(iterations: u32) f64 {
    var sum: f64 = 0.0;
    var i: u32 = 0;

    // Dominican Republic coordinates
    const santo_domingo_lat = 18.4861;
    const santo_domingo_lon = -69.9312;
    const punta_cana_lat = 18.5601;
    const punta_cana_lon = -68.3725;

    while (i < iterations) : (i += 1) {
        sum += haversine_distance(santo_domingo_lat + @as(f64, @floatFromInt(i)) * 0.001, santo_domingo_lon, punta_cana_lat, punta_cana_lon);
    }

    return sum;
}
