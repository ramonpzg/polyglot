//! PixelFlow core library
//!
//! Provides multispectral image structures and processing routines, with
//! optional bindings for Python (PyO3) and WebAssembly (wasm-bindgen).

pub mod image_processing;
pub mod satellite_analysis;

#[cfg(feature = "python")]
mod python_bindings;

#[cfg(feature = "wasm")]
pub mod wasm_bindings;

pub use image_processing::MultiSpectralImage;
pub use satellite_analysis::{analyze_bushfire_risk, AustralianRegion, BLUE_MOUNTAINS, PILBARA, BushfireRiskAssessment};

