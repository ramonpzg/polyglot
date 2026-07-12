// Example of using the library from a Rust binary or integration.

use pixelflow::{analyze_bushfire_risk, MultiSpectralImage, BLUE_MOUNTAINS};

fn main() {
    let width = 1024u32;
    let height = 1024u32;
    let len = (width * height) as usize;
    let red = vec![0.6f32; len];
    let green = vec![0.3f32; len];
    let blue = vec![0.1f32; len];
    let nir = vec![0.5f32; len];
    let img = MultiSpectralImage { width, height, red, green, blue, near_infrared: nir };
    let assess = analyze_bushfire_risk(&img, &BLUE_MOUNTAINS);
    println!("risk={:.3} veg={:.3} fires={} ", assess.risk_level, assess.vegetation_health, assess.fire_pixel_count);
}

