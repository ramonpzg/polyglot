// unused: remove to silence warning
// use std::cmp::min;

#[cfg(feature = "parallel")]
use rayon::prelude::*;

#[derive(Clone, Debug)]
pub struct MultiSpectralImage {
    pub width: u32,
    pub height: u32,
    pub red: Vec<f32>,
    pub green: Vec<f32>,
    pub blue: Vec<f32>,
    pub near_infrared: Vec<f32>,
}

impl MultiSpectralImage {
    #[inline]
    fn len(&self) -> usize { (self.width as usize) * (self.height as usize) }

    #[inline]
    fn to_u8(v: f32) -> u8 {
        let c = if v.is_finite() { v } else { 0.0 };
        (c.clamp(0.0, 1.0) * 255.0) as u8
    }

    #[cfg(feature = "parallel")]
    pub fn calculate_ndvi(&self) -> Vec<f32> {
        self.red
            .par_iter()
            .zip(&self.near_infrared)
            .map(|(red, nir)| {
                let d = *nir + *red;
                if d.abs() > f32::EPSILON { (*nir - *red) / d } else { 0.0 }
            })
            .collect()
    }

    #[cfg(not(feature = "parallel"))]
    pub fn calculate_ndvi(&self) -> Vec<f32> {
        self.red
            .iter()
            .zip(&self.near_infrared)
            .map(|(red, nir)| {
                let d = *nir + *red;
                if d.abs() > f32::EPSILON { (*nir - *red) / d } else { 0.0 }
            })
            .collect()
    }

    #[cfg(feature = "parallel")]
    pub fn detect_fire_pixels(&self, ndvi_threshold: f32) -> Vec<bool> {
        let ndvi = self.calculate_ndvi();
        ndvi
            .par_iter()
            .zip(&self.red)
            .zip(&self.green)
            .map(|((ndvi_val, red), green)| *ndvi_val < ndvi_threshold && *red > *green * 1.5)
            .collect()
    }

    #[cfg(not(feature = "parallel"))]
    pub fn detect_fire_pixels(&self, ndvi_threshold: f32) -> Vec<bool> {
        let ndvi = self.calculate_ndvi();
        ndvi
            .iter()
            .zip(&self.red)
            .zip(&self.green)
            .map(|((ndvi_val, red), green)| *ndvi_val < ndvi_threshold && *red > *green * 1.5)
            .collect()
    }

    #[cfg(feature = "parallel")]
    pub fn apply_false_color(&self) -> Vec<u8> {
        let mut output = vec![0u8; self.len() * 3];
        output
            .par_chunks_exact_mut(3)
            .enumerate()
            .for_each(|(i, px)| {
                px[0] = Self::to_u8(self.near_infrared[i]); // R = NIR
                px[1] = Self::to_u8(self.red[i]);           // G = Red
                px[2] = Self::to_u8(self.green[i]);         // B = Green
            });
        output
    }

    #[cfg(not(feature = "parallel"))]
    pub fn apply_false_color(&self) -> Vec<u8> {
        let mut output = vec![0u8; self.len() * 3];
        for i in 0..self.len() {
            let o = i * 3;
            output[o] = Self::to_u8(self.near_infrared[i]);
            output[o + 1] = Self::to_u8(self.red[i]);
            output[o + 2] = Self::to_u8(self.green[i]);
        }
        output
    }
}
