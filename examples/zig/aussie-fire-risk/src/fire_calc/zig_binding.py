from __future__ import annotations

import ctypes as ct
import os
import sys
from pathlib import Path
from typing import Optional

import numpy as np


def _default_lib_name() -> str:
    if sys.platform.startswith("linux"):
        return "libfire_calc.so"
    if sys.platform == "darwin":
        return "libfire_calc.dylib"
    return "fire_calc.dll"


def _find_lib_path(explicit: Optional[str] = None) -> Optional[Path]:
    if explicit:
        p = Path(explicit)
        return p if p.exists() else None

    env = os.getenv("FIRE_CALC_LIB_PATH")
    if env:
        p = Path(env)
        if p.exists():
            return p

    # Try zig-out/lib under the Zig subproject
    here = Path(__file__).resolve().parent
    zig_root = here.parent / "fire_calc_zig"
    candidate = zig_root / "zig-out" / "lib" / _default_lib_name()
    if candidate.exists():
        return candidate

    # Try current working directory zig-out/lib
    cwd_candidate = Path.cwd() / "zig-out" / "lib" / _default_lib_name()
    if cwd_candidate.exists():
        return cwd_candidate

    return None


_lib_handle: Optional[ct.CDLL] = None


def load_zig_lib(path: Optional[str] = None) -> ct.CDLL:
    global _lib_handle
    if _lib_handle is not None:
        return _lib_handle

    lib_path = _find_lib_path(path)
    if not lib_path:
        raise FileNotFoundError(
            "Could not find Zig shared library. Set FIRE_CALC_LIB_PATH or build via 'zig build'."
        )

    _lib_handle = ct.CDLL(str(lib_path))

    # Prototype: void calculate_fire_danger_index_out(const double*, const double*, const double*, const double*, const double*, const double*, size_t, double*)
    _lib_handle.calculate_fire_danger_index_out.argtypes = [
        ct.POINTER(ct.c_double),  # drought_factor
        ct.POINTER(ct.c_double),  # ffmc
        ct.POINTER(ct.c_double),  # wind_speed
        ct.POINTER(ct.c_double),  # temperature_c
        ct.POINTER(ct.c_double),  # humidity_frac
        ct.POINTER(ct.c_double),  # elevation_m
        ct.c_size_t,              # size
        ct.POINTER(ct.c_double),  # out
    ]
    _lib_handle.calculate_fire_danger_index_out.restype = None

    return _lib_handle


def _as_c_double_ptr(a: np.ndarray) -> ct.POINTER(ct.c_double):
    if a.dtype != np.float64 or not a.flags.c_contiguous:
        a = np.ascontiguousarray(a, dtype=np.float64)
    return a.ctypes.data_as(ct.POINTER(ct.c_double))


def fdi_zig(
    drought_factor: np.ndarray,
    ffmc: np.ndarray,
    wind_speed: np.ndarray,
    temperature_c: np.ndarray,
    humidity_frac: np.ndarray,
    elevation_m: np.ndarray,
    out: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Compute FDI using the Zig shared library via ctypes.

    Ensure the Zig library is built (`zig build`) before calling.
    """
    n = int(np.asarray(drought_factor).size)
    d = np.asarray(drought_factor, dtype=np.float64, order="C")
    f = np.asarray(ffmc, dtype=np.float64, order="C")
    w = np.asarray(wind_speed, dtype=np.float64, order="C")
    t = np.asarray(temperature_c, dtype=np.float64, order="C")
    h = np.asarray(humidity_frac, dtype=np.float64, order="C")
    e = np.asarray(elevation_m, dtype=np.float64, order="C")

    assert d.shape == f.shape == w.shape == t.shape == h.shape == e.shape, "All arrays must have same shape"

    if out is None:
        out = np.empty_like(d)
    else:
        assert out.shape == d.shape and out.dtype == np.float64

    lib = load_zig_lib()
    lib.calculate_fire_danger_index_out(
        _as_c_double_ptr(d),
        _as_c_double_ptr(f),
        _as_c_double_ptr(w),
        _as_c_double_ptr(t),
        _as_c_double_ptr(h),
        _as_c_double_ptr(e),
        ct.c_size_t(n),
        _as_c_double_ptr(out),
    )
    return out

