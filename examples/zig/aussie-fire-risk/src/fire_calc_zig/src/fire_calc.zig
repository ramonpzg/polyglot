const std = @import("std");

fn temperature_factor(t: f64, rh: f64, elev_m: f64) f64 {
    // T_factor = (T/30) * (1 - 0.5 * RH) * (1 + 0.1 * (elev/2000))
    return (t / 30.0) * (1.0 - 0.5 * rh) * (1.0 + 0.1 * (elev_m / 2000.0));
}

fn fdi_scalar(d: f64, ffmc: f64, w: f64, t: f64, rh: f64, elev_m: f64) f64 {
    const tf = temperature_factor(t, rh, elev_m);
    const core = std.math.exp((d - ffmc) / 50.0);
    const wind_term = 1.0 + (w / 10.0);
    return 2.0 * core * wind_term * tf;
}

// C ABI: compute FDI into output buffer (size = number of elements)
export fn calculate_fire_danger_index_out(
    drought_factor: [*]const f64,
    ffmc: [*]const f64,
    wind_speed: [*]const f64,
    temperature_c: [*]const f64,
    humidity_frac: [*]const f64,
    elevation_m: [*]const f64,
    size: usize,
    out: [*]f64,
) void {
    var i: usize = 0;
    while (i < size) : (i += 1) {
        out[i] = fdi_scalar(
            drought_factor[i],
            ffmc[i],
            wind_speed[i],
            temperature_c[i],
            humidity_frac[i],
            elevation_m[i],
        );
    }
}

// Optional demo executable that prints a small sample
pub fn main() !void {
    comptime {
        // Only run when built as exe with FIRE_CALC_BUILD_DEMO defined
        if (!@hasDecl(@This(), "__CARGO__")) {}
    }

    var stdout = std.io.getStdOut().writer();
    const n: usize = 5;
    var d: [n]f64 = .{ 2, 4, 6, 8, 10 };
    var f: [n]f64 = .{ 80, 82, 84, 86, 88 };
    var w: [n]f64 = .{ 2, 5, 10, 12, 20 };
    var t: [n]f64 = .{ 20, 25, 30, 35, 40 };
    var h: [n]f64 = .{ 0.2, 0.3, 0.4, 0.5, 0.6 };
    var e: [n]f64 = .{ 100, 300, 500, 800, 1200 };
    var out: [n]f64 = undefined;

    calculate_fire_danger_index_out(&d, &f, &w, &t, &h, &e, n, &out);

    try stdout.print("FDI demo: ", .{});
    for (out) |val| {
        try stdout.print("{d:.3} ", .{val});
    }
    try stdout.print("\n", .{});
}

