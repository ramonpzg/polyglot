use hillshade_core::{radians, GpuContext, Params};
use numpy::{PyArray3, PyArrayMethods, PyReadonlyArray2};
use once_cell::sync::OnceCell;
use pyo3::prelude::*;

static GPU: OnceCell<GpuContext> = OnceCell::new();

fn get_ctx() -> anyhow::Result<&'static GpuContext> {
    GPU.get_or_try_init(|| pollster::block_on(GpuContext::new()))
}

#[pyclass]
struct HillshadeSession {}

#[pymethods]
impl HillshadeSession {
    #[new]
    fn new() -> PyResult<Self> {
        get_ctx().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        Ok(Self {})
    }

    fn render(
        &self,
        py: Python<'_>,
        dem: PyReadonlyArray2<'_, f32>,
        cellsize: f32,
        azimuth_deg: f32,
        altitude_deg: f32,
    ) -> PyResult<Py<PyArray3<u8>>> {
        hillshade_impl(py, dem, cellsize, azimuth_deg, altitude_deg)
    }
}

#[pyfunction]
fn hillshade(
    py: Python<'_>,
    dem: PyReadonlyArray2<'_, f32>,
    cellsize: f32,
    azimuth_deg: f32,
    altitude_deg: f32,
) -> PyResult<Py<PyArray3<u8>>> {
    hillshade_impl(py, dem, cellsize, azimuth_deg, altitude_deg)
}

fn hillshade_impl(
    py: Python<'_>,
    dem: PyReadonlyArray2<'_, f32>,
    cellsize: f32,
    azimuth_deg: f32,
    altitude_deg: f32,
) -> PyResult<Py<PyArray3<u8>>> {
    let dem = dem.as_array();
    let (h, w) = dem.dim();
    let data: Vec<f32> = dem.to_owned().into_raw_vec();

    let az = radians(azimuth_deg);
    let zenith = radians(90.0 - altitude_deg.max(0.1));

    let ctx = get_ctx().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

    let rgba = py
        .allow_threads(|| {
            let params = Params {
                dims: [w as u32, h as u32],
                cell: cellsize,
                _pad0: 0.0,
                azimuth: az,
                zenith,
                _pad1: [0.0, 0.0],
            };
            ctx.run(&data, w as u32, h as u32, params)
        })
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

    // Allocate a contiguous numpy array and copy results in
    let out = PyArray3::<u8>::zeros_bound(py, [h, w, 4], false);
    unsafe {
        out.as_slice_mut()?.copy_from_slice(&rgba);
    }

    // Return owned Py<PyArray3<u8>> so we don't fight lifetimes
    Ok(out.unbind())
}

#[pymodule]
fn _hillshade(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<HillshadeSession>()?;
    m.add_function(wrap_pyfunction!(hillshade, m)?)?;
    Ok(())
}
