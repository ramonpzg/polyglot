use std::env;

use pixelflow::{analyze_bushfire_risk, MultiSpectralImage, BLUE_MOUNTAINS};

fn synth_image(width: u32, height: u32) -> MultiSpectralImage {
    let len = (width * height) as usize;
    let mut red = vec![0.0f32; len];
    let mut green = vec![0.0f32; len];
    let mut blue = vec![0.0f32; len];
    let mut nir = vec![0.0f32; len];

    // Simple gradients with a "hot" stripe to simulate fire-like pixels
    for y in 0..height as usize {
        for x in 0..width as usize {
            let i = y * (width as usize) + x;
            let xf = x as f32 / (width.max(1) as f32);
            let yf = y as f32 / (height.max(1) as f32);
            red[i] = (0.2 + 0.8 * xf).clamp(0.0, 1.0);
            green[i] = (0.2 + 0.8 * yf).clamp(0.0, 1.0);
            blue[i] = (0.5 * (1.0 - xf)).clamp(0.0, 1.0);
            nir[i] = (0.6 * (1.0 - yf)).clamp(0.0, 1.0);
            if (width > 0) && ((x as u32) > width * 2 / 5) && ((x as u32) < width * 3 / 5) && (y % 16 == 0) {
                red[i] = 1.0;
                green[i] *= 0.4;
            }
        }
    }

    MultiSpectralImage { width, height, red, green, blue, near_infrared: nir }
}

fn main() {
    let mut args = env::args().skip(1);
    let cmd = args.next().unwrap_or_else(|| "help".to_string());
    match cmd.as_str() {
        "process" => {
            let width: u32 = args.next().unwrap_or_else(|| "1024".into()).parse().unwrap_or(1024);
            let height: u32 = args.next().unwrap_or_else(|| "1024".into()).parse().unwrap_or(1024);
            let img = synth_image(width, height);
            let ndvi = img.calculate_ndvi();
            let fires = img.detect_fire_pixels(0.3);
            let assess = analyze_bushfire_risk(&img, &BLUE_MOUNTAINS);
            let fire_count = fires.iter().filter(|&&f| f).count();
            println!(
                "Processed {}x{} pixels | fire_pixels={} | veg_health={:.3} | risk={:.3}",
                width, height, fire_count, assess.vegetation_health, assess.risk_level
            );
            // Suppress unused warning
            if ndvi.len() == 0 { println!("ndvi empty"); }
        }
        _ => {
            eprintln!("Usage: pixelflow-cli process <width> <height>");
        }
    }
}
