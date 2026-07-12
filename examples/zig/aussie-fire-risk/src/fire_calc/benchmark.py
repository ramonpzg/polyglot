from __future__ import annotations

import argparse
import time

import numpy as np

from .python_impl import fdi_python
from .zig_binding import fdi_zig, load_zig_lib


def bench(size: int, use_zig: bool) -> dict[str, float]:
    rng = np.random.default_rng(123)
    d = rng.uniform(0, 10, size)
    f = rng.uniform(60, 95, size)
    w = rng.uniform(0, 25, size)
    t = rng.uniform(10, 45, size)
    h = rng.uniform(0.05, 0.8, size)
    e = rng.uniform(0, 2000, size)

    # Warmup
    fdi_python(d, f, w, t, h, e)
    if use_zig:
        load_zig_lib()
        fdi_zig(d, f, w, t, h, e)

    t0 = time.perf_counter()
    py_out = fdi_python(d, f, w, t, h, e)
    t1 = time.perf_counter()
    py_ms = (t1 - t0) * 1000

    zig_ms = None
    if use_zig:
        t2 = time.perf_counter()
        zig_out = fdi_zig(d, f, w, t, h, e)
        t3 = time.perf_counter()
        zig_ms = (t3 - t2) * 1000
        # Correctness check
        max_abs = float(np.max(np.abs(py_out - zig_out)))
        return {"python_ms": py_ms, "zig_ms": zig_ms, "diff_max": max_abs}

    return {"python_ms": py_ms}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", nargs="*", type=int, default=[10_000, 100_000, 1_000_000])
    ap.add_argument("--use-zig", action="store_true", help="Include Zig in benchmarks (requires built lib)")
    args = ap.parse_args()

    print("Benchmarking sizes:", args.sizes)
    for n in args.sizes:
        try:
            res = bench(n, use_zig=args.use_zig)
        except Exception as e:
            print(f"size={n}: ERROR: {e}")
            continue
        if "zig_ms" in res:
            print(f"size={n:>8}: python={res['python_ms']:.2f} ms, zig={res['zig_ms']:.2f} ms, max_diff={res['diff_max']:.3e}")
        else:
            print(f"size={n:>8}: python={res['python_ms']:.2f} ms")


if __name__ == "__main__":
    main()

