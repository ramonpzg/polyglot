use crate::image_processing::MultiSpectralImage;

#[derive(Clone, Copy, Debug)]
pub struct AustralianRegion {
    pub name: &'static str,
    pub bounds: (f64, f64, f64, f64), // (min_lat, min_lon, max_lat, max_lon)
}

pub const PILBARA: AustralianRegion = AustralianRegion {
    name: "Pilbara Mining Region",
    bounds: (-24.0, 115.0, -20.0, 121.0),
};

pub const BLUE_MOUNTAINS: AustralianRegion = AustralianRegion {
    name: "Blue Mountains Fire Zone",
    bounds: (-34.0, 150.0, -33.0, 151.0),
};

#[derive(Debug, Clone)]
pub struct BushfireRiskAssessment {
    pub region: &'static str,
    pub vegetation_health: f32,
    pub fire_pixel_count: usize,
    pub risk_level: f32,
}

fn calculate_risk_level(vegetation_health: f32, fire_ratio: f32) -> f32 {
    // Heuristic: low vegetation health + many hot/red pixels => higher risk
    // Weighted blend with simple bounds.
    let veg_component = (1.0 - vegetation_health).clamp(0.0, 1.0) * 0.7;
    let fire_component = fire_ratio.clamp(0.0, 1.0) * 0.3;
    (veg_component + fire_component).clamp(0.0, 1.0)
}

pub fn analyze_bushfire_risk(
    image: &MultiSpectralImage,
    region: &AustralianRegion,
) -> BushfireRiskAssessment {
    let ndvi = image.calculate_ndvi();
    let fire_pixels = image.detect_fire_pixels(0.3);

    let vegetation_health = if ndvi.is_empty() {
        0.0
    } else {
        let sum_pos: f32 = ndvi.iter().map(|v| v.max(0.0)).sum();
        sum_pos / (ndvi.len() as f32)
    };

    let fire_pixel_count = fire_pixels.iter().filter(|&&x| x).count();
    let total = (image.width as usize) * (image.height as usize);
    let fire_ratio = if total > 0 { fire_pixel_count as f32 / total as f32 } else { 0.0 };

    BushfireRiskAssessment {
        region: region.name,
        vegetation_health,
        fire_pixel_count,
        risk_level: calculate_risk_level(vegetation_health, fire_ratio),
    }
}

