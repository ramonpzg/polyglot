from __future__ import annotations

import numpy as np


def temperature_factor(temperature_c: np.ndarray, humidity_frac: np.ndarray, elevation_m: np.ndarray) -> np.ndarray:
    """Deterministic temperature factor used by both Python and Zig impls.

    T_factor = (T/30) * (1 - 0.5 * RH) * (1 + 0.1 * (elev/2000))
    Where RH is expressed as 0..1 fraction.
    """
    t = np.asarray(temperature_c, dtype=np.float64)
    rh = np.asarray(humidity_frac, dtype=np.float64)
    elev = np.asarray(elevation_m, dtype=np.float64)
    return (t / 30.0) * (1.0 - 0.5 * rh) * (1.0 + 0.1 * (elev / 2000.0))


def fdi_python(
    drought_factor: np.ndarray,
    ffmc: np.ndarray,
    wind_speed: np.ndarray,
    temperature_c: np.ndarray,
    humidity_frac: np.ndarray,
    elevation_m: np.ndarray,
) -> np.ndarray:
    """Pure-NumPy implementation of the simplified FDI.

    FDI = 2 * exp((D - FFMC)/50) * (1 + W/10) * T_factor
    """
    d = np.asarray(drought_factor, dtype=np.float64)
    f = np.asarray(ffmc, dtype=np.float64)
    w = np.asarray(wind_speed, dtype=np.float64)
    t = np.asarray(temperature_c, dtype=np.float64)
    rh = np.asarray(humidity_frac, dtype=np.float64)
    elev = np.asarray(elevation_m, dtype=np.float64)

    assert d.shape == f.shape == w.shape == t.shape == rh.shape == elev.shape, "All arrays must have same shape"

    tf = temperature_factor(t, rh, elev)
    core = np.exp((d - f) / 50.0)
    wind_term = 1.0 + (w / 10.0)
    return 2.0 * core * wind_term * tf


if __name__ == "__main__":
    n = 10
    rng = np.random.default_rng(42)
    d = rng.uniform(0, 10, n)
    f = rng.uniform(60, 95, n)
    w = rng.uniform(0, 25, n)
    t = rng.uniform(10, 45, n)
    rh = rng.uniform(0.05, 0.8, n)
    elev = rng.uniform(100, 1500, n)
    out = fdi_python(d, f, w, t, rh, elev)
    print("FDI sample:", out[:5])

