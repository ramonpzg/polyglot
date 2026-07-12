from __future__ import annotations

import numpy as np

from fire_calc.python_impl import fdi_python
from fire_calc.zig_binding import fdi_zig, load_zig_lib


def test_python_vs_zig_small():
    rng = np.random.default_rng(1234)
    n = 1000
    d = rng.uniform(0, 10, n)
    f = rng.uniform(60, 95, n)
    w = rng.uniform(0, 25, n)
    t = rng.uniform(10, 45, n)
    h = rng.uniform(0.05, 0.8, n)
    e = rng.uniform(0, 2000, n)

    py_out = fdi_python(d, f, w, t, h, e)
    try:
        load_zig_lib()
    except FileNotFoundError:
        # Allow running tests without Zig present
        return
    zig_out = fdi_zig(d, f, w, t, h, e)

    max_abs = float(np.max(np.abs(py_out - zig_out)))
    assert max_abs < 1e-12

