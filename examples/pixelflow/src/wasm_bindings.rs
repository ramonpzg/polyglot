#![cfg(feature = "wasm")]

use wasm_bindgen::prelude::*;

use crate::image_processing::MultiSpectralImage;

#[wasm_bindgen]
pub struct WasmImageProcessor {
    image: MultiSpectralImage,
}

#[wasm_bindgen]
impl WasmImageProcessor {
    #[wasm_bindgen(constructor)]
    pub fn new(width: u32, height: u32) -> WasmImageProcessor {
        let len = (width * height) as usize;
        WasmImageProcessor {
            image: MultiSpectralImage {
                width,
                height,
                red: vec![0.0; len],
                green: vec![0.0; len],
                blue: vec![0.0; len],
                near_infrared: vec![0.0; len],
            },
        }
    }

    #[wasm_bindgen]
    pub fn load_band_data(&mut self, band: &str, data: &[f32]) {
        let target = match band {
            "red" => &mut self.image.red,
            "green" => &mut self.image.green,
            "blue" => &mut self.image.blue,
            "nir" => &mut self.image.near_infrared,
            _ => return,
        };
        if target.len() == data.len() {
            target.copy_from_slice(data);
        }
    }

    #[wasm_bindgen]
    pub fn process_false_color(&self) -> Vec<u8> {
        self.image.apply_false_color()
    }

    #[wasm_bindgen]
    pub fn detect_fires(&self) -> Vec<u8> {
        self.image
            .detect_fire_pixels(0.3)
            .into_iter()
            .map(|fire| if fire { 255 } else { 0 })
            .collect()
    }
}

