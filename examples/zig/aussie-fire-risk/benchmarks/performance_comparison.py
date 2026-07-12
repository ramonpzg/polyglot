from __future__ import annotations

import time
import numpy as np

from fire_calc.python_impl import fdi_python
from fire_calc.zig_binding import fdi_zig, load_zig_lib


def time_it(fn, *args, repeat=3):
    best = float("inf")
    for _ in range(repeat):
        t0 = time.perf_counter()
        out = fn(*args)
        t1 = time.perf_counter()
        best = min(best, t1 - t0)
    return best, out


def run_sizes(sizes=(1_000, 10_000, 100_000, 1_000_000)):
    rng = np.random.default_rng(7)
    load_zig_lib()  # may raise if not built

    for n in sizes:
        d = rng.uniform(0, 10, n)
        f = rng.uniform(60, 95, n)
        w = rng.uniform(0, 25, n)
        t = rng.uniform(10, 45, n)
        h = rng.uniform(0.05, 0.8, n)
        e = rng.uniform(0, 2000, n)

        t_py, py_out = time_it(fdi_python, d, f, w, t, h, e)
        t_zig, zig_out = time_it(fdi_zig, d, f, w, t, h, e)

        max_abs = float(np.max(np.abs(py_out - zig_out)))
        print(
            f"n={n:>8} | python={t_py*1e3:7.2f} ms | zig={t_zig*1e3:7.2f} ms | diff={max_abs:.3e}"
        )


if __name__ == "__main__":
    run_sizes()

