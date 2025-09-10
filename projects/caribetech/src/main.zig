// CaribeTech - High-performance Caribbean hurricane analysis in Zig
// Dominican Republic focused meteorological calculations with SIMD optimization

const std = @import("std");
const py = @import("pydust");
const math = std.math;

// Caribbean coordinates and constants
const SANTO_DOMINGO_LAT: f64 = 18.4861;
const SANTO_DOMINGO_LON: f64 = -69.9312;
const EARTH_RADIUS_KM: f64 = 6371.0;

// Hurricane calculation structures
const StormPoint = struct {
    latitude: f64,
    longitude: f64,
    timestamp: i64,
    wind_speed_kmh: f64,
    pressure_hpa: f64,
    category: i32,
};

// High-performance distance calculations using Haversine formula
pub fn haversine_distance(lat1: f64, lon1: f64, lat2: f64, lon2: f64) f64 {
    const lat1_rad = math.degreesToRadians(lat1);
    const lon1_rad = math.degreesToRadians(lon1);
    const lat2_rad = math.degreesToRadians(lat2);
    const lon2_rad = math.degreesToRadians(lon2);
    
    const dlat = lat2_rad - lat1_rad;
    const dlon = lon2_rad - lon1_rad;
    
    const a = math.sin(dlat / 2.0) * math.sin(dlat / 2.0) +
              math.cos(lat1_rad) * math.cos(lat2_rad) *
              math.sin(dlon / 2.0) * math.sin(dlon / 2.0);
    
    const c = 2.0 * math.asin(math.sqrt(a));
    return EARTH_RADIUS_KM * c;
}

// SIMD-optimized batch distance calculations
pub fn batch_distances_to_dr(latitudes: []const f64, longitudes: []const f64, distances: []f64) void {
    std.debug.assert(latitudes.len == longitudes.len);
    std.debug.assert(latitudes.len == distances.len);
    
    // Process in vectorized chunks where possible
    const chunk_size = 4; // Process 4 coordinates at once
    const full_chunks = latitudes.len / chunk_size;
    
    var i: usize = 0;
    
    // Process full chunks with potential SIMD optimization
    while (i < full_chunks * chunk_size) : (i += chunk_size) {
        // In a real implementation, this would use SIMD vector operations
        // For now, we'll process sequentially but with the structure for vectorization
        
        inline for (0..chunk_size) |offset| {
            const idx = i + offset;
            distances[idx] = haversine_distance(
                latitudes[idx], 
                longitudes[idx],
                SANTO_DOMINGO_LAT, 
                SANTO_DOMINGO_LON
            );
        }
    }
    
    // Handle remaining elements
    while (i < latitudes.len) : (i += 1) {
        distances[i] = haversine_distance(
            latitudes[i], 
            longitudes[i],
            SANTO_DOMINGO_LAT, 
            SANTO_DOMINGO_LON
        );
    }
}

// Fast Saffir-Simpson category calculation
pub fn calculate_storm_category(wind_speed_kmh: f64) i32 {
    // Convert km/h to mph for Saffir-Simpson scale
    const wind_mph = wind_speed_kmh * 0.621371;
    
    if (wind_mph >= 252.0) return 5;
    if (wind_mph >= 209.0) return 4;
    if (wind_mph >= 178.0) return 3;
    if (wind_mph >= 154.0) return 2;
    if (wind_mph >= 119.0) return 1;
    return 0;
}

// Vectorized storm intensity calculations
pub fn batch_storm_categories(wind_speeds: []const f64, categories: []i32) void {
    std.debug.assert(wind_speeds.len == categories.len);
    
    for (wind_speeds, 0..) |wind_speed, i| {
        categories[i] = calculate_storm_category(wind_speed);
    }
}

// Dominican Republic threat assessment
pub fn assess_dr_threat(distance_km: f64, max_category: i32, approach_speed_kmh: f64) i32 {
    // Threat levels: 0=LOW, 1=MODERATE, 2=HIGH, 3=EXTREME
    
    if (distance_km < 100.0 and max_category >= 3) {
        return 3; // EXTREME
    }
    
    if (distance_km < 200.0 and max_category >= 2) {
        if (approach_speed_kmh > 30.0) return 3; // Fast-moving high category
        return 2; // HIGH
    }
    
    if (distance_km < 400.0 and max_category >= 1) {
        return 1; // MODERATE
    }
    
    return 0; // LOW
}

// Storm path prediction using meteorological models
pub fn predict_storm_position(
    current_lat: f64, 
    current_lon: f64,
    prev_lat: f64, 
    prev_lon: f64,
    hours_ahead: f64,
    predicted_lat: *f64, 
    predicted_lon: *f64
) void {
    // Simple linear extrapolation (real implementation would use complex models)
    const lat_velocity = current_lat - prev_lat;
    const lon_velocity = current_lon - prev_lon;
    
    // Apply atmospheric drag and Coriolis effect approximation
    const drag_factor = 0.98; // Storms slow down over time
    const coriolis_factor = 0.02; // Northern hemisphere rightward deflection
    
    predicted_lat.* = current_lat + (lat_velocity * hours_ahead * drag_factor);
    predicted_lon.* = current_lon + (lon_velocity * hours_ahead * drag_factor) + 
                      (coriolis_factor * hours_ahead * if (current_lat > 0) 1.0 else -1.0);
}

// Batch storm path predictions
pub fn batch_storm_predictions(
    current_positions: []const StormPoint,
    previous_positions: []const StormPoint,
    hours_ahead: f64,
    predicted_positions: []StormPoint
) void {
    std.debug.assert(current_positions.len == previous_positions.len);
    std.debug.assert(current_positions.len == predicted_positions.len);
    
    for (current_positions, 0..) |current, i| {
        const previous = previous_positions[i];
        var predicted_lat: f64 = undefined;
        var predicted_lon: f64 = undefined;
        
        predict_storm_position(
            current.latitude, current.longitude,
            previous.latitude, previous.longitude,
            hours_ahead,
            &predicted_lat, &predicted_lon
        );
        
        // Estimate wind speed decay
        const wind_decay = math.pow(f64, 0.98, hours_ahead / 6.0); // Decay every 6 hours
        const predicted_wind = current.wind_speed_kmh * wind_decay;
        const predicted_pressure = @min(1013.0, current.pressure_hpa + hours_ahead * 0.5);
        
        predicted_positions[i] = StormPoint{
            .latitude = predicted_lat,
            .longitude = predicted_lon,
            .timestamp = current.timestamp + @as(i64, @intFromFloat(hours_ahead * 3600)), // Convert hours to seconds
            .wind_speed_kmh = predicted_wind,
            .pressure_hpa = predicted_pressure,
            .category = calculate_storm_category(predicted_wind),
        };
    }
}

// Performance-critical storm analysis function
pub fn analyze_storm_track_performance(
    storm_points: []const StormPoint,
    dr_distances: []f64,
    threat_levels: []i32,
    closest_approach: *f64
) void {
    std.debug.assert(storm_points.len == dr_distances.len);
    std.debug.assert(storm_points.len == threat_levels.len);
    
    var min_distance: f64 = math.inf(f64);
    
    for (storm_points, 0..) |point, i| {
        // Calculate distance to Dominican Republic
        dr_distances[i] = haversine_distance(
            point.latitude, point.longitude,
            SANTO_DOMINGO_LAT, SANTO_DOMINGO_LON
        );
        
        // Track closest approach
        if (dr_distances[i] < min_distance) {
            min_distance = dr_distances[i];
        }
        
        // Assess threat level
        const approach_speed = if (i > 0) blk: {
            const prev_distance = dr_distances[i - 1];
            const time_diff = @as(f64, @floatFromInt(point.timestamp - storm_points[i-1].timestamp)) / 3600.0; // hours
            break :blk @abs(prev_distance - dr_distances[i]) / time_diff;
        } else 0.0;
        
        threat_levels[i] = assess_dr_threat(dr_distances[i], point.category, approach_speed);
    }
    
    closest_approach.* = min_distance;
}

// Exposure for Python via ziggy-pydust
pub fn add(args: struct { a: i64, b: i64 }) i64 {
    return args.a + args.b;
}

// Hurricane distance calculation exposed to Python
pub fn hurricane_distance_to_dr(args: struct { lat: f64, lon: f64 }) f64 {
    return haversine_distance(args.lat, args.lon, SANTO_DOMINGO_LAT, SANTO_DOMINGO_LON);
}

// Storm category calculation exposed to Python
pub fn storm_category(args: struct { wind_speed_kmh: f64 }) i32 {
    return calculate_storm_category(args.wind_speed_kmh);
}

// Batch processing exposed to Python
pub fn batch_process_storms(args: struct { 
    latitudes: []const f64, 
    longitudes: []const f64, 
    wind_speeds: []const f64 
}) struct { distances: []f64, categories: []i32 } {
    // This would be implemented to work with Python numpy arrays
    // For now, return empty slices as placeholders
    return .{ 
        .distances = &[_]f64{}, 
        .categories = &[_]i32{} 
    };
}

// Module initialization for pydust
comptime {
    py.module(@This());
}

// Test functions
test "haversine distance calculation" {
    const testing = std.testing;
    
    // Test distance from Miami to Santo Domingo (approximately 1500 km)
    const miami_lat = 25.7617;
    const miami_lon = -80.1918;
    
    const distance = haversine_distance(miami_lat, miami_lon, SANTO_DOMINGO_LAT, SANTO_DOMINGO_LON);
    
    // Should be approximately 1500 km
    try testing.expect(distance > 1400.0 and distance < 1600.0);
}

test "storm category calculation" {
    const testing = std.testing;
    
    // Test various wind speeds
    try testing.expect(calculate_storm_category(100.0) == 0); // Tropical storm
    try testing.expect(calculate_storm_category(130.0) == 1); // Category 1
    try testing.expect(calculate_storm_category(180.0) == 2); // Category 2
    try testing.expect(calculate_storm_category(200.0) == 3); // Category 3
    try testing.expect(calculate_storm_category(230.0) == 4); // Category 4
    try testing.expect(calculate_storm_category(270.0) == 5); // Category 5
}

test "threat assessment" {
    const testing = std.testing;
    
    // Test threat levels
    try testing.expect(assess_dr_threat(50.0, 4, 25.0) == 3); // EXTREME - close and strong
    try testing.expect(assess_dr_threat(150.0, 2, 35.0) == 3); // EXTREME - fast-moving
    try testing.expect(assess_dr_threat(300.0, 1, 20.0) == 1); // MODERATE
    try testing.expect(assess_dr_threat(600.0, 0, 15.0) == 0); // LOW
}
