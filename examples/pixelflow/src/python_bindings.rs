#![cfg(feature = "python")]

use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use numpy::{PyArray2, PyReadonlyArray2};

use crate::image_processing::MultiSpectralImage;
use crate::satellite_analysis::{analyze_bushfire_risk, BLUE_MOUNTAINS, PILBARA};

#[pyclass]
pub struct PyMultiSpectralImage {
    inner: MultiSpectralImage,
}

#[pymethods]
impl PyMultiSpectralImage {
    #[new]
    fn new(
        red: PyReadonlyArray2<f32>,
        green: PyReadonlyArray2<f32>,
        blue: PyReadonlyArray2<f32>,
        nir: PyReadonlyArray2<f32>,
    ) -> PyResult<Self> {
        // Get HxW from the red band; PyReadonlyArray2::dims() returns Dim<[_;2]>,
        // so use shape() for a simple (h, w) extraction and consistent comparisons.
        let shape = red.shape();
        let (h, w) = (shape[0], shape[1]);
        // Basic shape checks
        if green.shape() != shape || blue.shape() != shape || nir.shape() != shape {
            return Err(PyValueError::new_err("All bands must have identical HxW dimensions"));
        }

        let red_vec = red.as_slice()?.to_vec();
        let green_vec = green.as_slice()?.to_vec();
        let blue_vec = blue.as_slice()?.to_vec();
        let nir_vec = nir.as_slice()?.to_vec();

        Ok(Self {
            inner: MultiSpectralImage {
                width: w as u32,
                height: h as u32,
                red: red_vec,
                green: green_vec,
                blue: blue_vec,
                near_infrared: nir_vec,
            },
        })
    }

    fn calculate_ndvi<'py>(&self, py: Python<'py>) -> PyResult<&'py PyArray2<f32>> {
        let ndvi = self.inner.calculate_ndvi();
        let h = self.inner.height as usize;
        let w = self.inner.width as usize;
        // Build a 2D ndarray from the flat vector, then convert to numpy array
        let arr2 = numpy::ndarray::Array2::from_shape_vec((h, w), ndvi)
            .map_err(|e| PyValueError::new_err(format!("failed to build ndarray: {e}")))?;
        Ok(PyArray2::from_owned_array(py, arr2))
    }

    fn detect_bushfire_risk(&self, region: &str) -> PyResult<f32> {
        let region = match region {
            "pilbara" => &PILBARA,
            "blue_mountains" => &BLUE_MOUNTAINS,
            _ => return Err(PyValueError::new_err("Unknown region")),
        };
        let assessment = analyze_bushfire_risk(&self.inner, region);
        Ok(assessment.risk_level)
    }
}

#[pymodule]
fn pixelflow(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyMultiSpectralImage>()?;
    Ok(())
}
