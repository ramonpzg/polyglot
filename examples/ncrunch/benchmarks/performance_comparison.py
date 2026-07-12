import time
from typing import List

import numpy as np

try:
    import numcrunch as nc
except Exception as e:  # pragma: no cover
    print("Failed to import numcrunch:", e)
    raise


def pure_python_monte_carlo(iterations: int = 1_000_000) -> float:
    rng = np.random.default_rng(42)
    # Toy: sample grades uniform [0.45, 0.65]
    grades = rng.uniform(0.45, 0.65, size=iterations)
    lut = np.sqrt(1.0 + grades) / (1.0 + grades * grades * 0.1)
    return float(np.mean(grades * lut))


def benchmark_monte_carlo():
    # Python baseline
    start = time.time()
    _ = pure_python_monte_carlo(iterations=1_000_000)
    py_time = time.time() - start

    # C++23 implementation
    model = nc.AustralianMiningModel()
    model.load_pilbara_data("data/pilbara_geology.csv")
    geo = model.create_geology_model()

    engine = nc.MonteCarloEngine(seed=42)
    start = time.time()
    _ = engine.run_geological_simulation(model=geo, num_iterations=1_000_000)
    cpp_time = time.time() - start

    print(f"Python: {py_time:.2f}s")
    print(f"C++23:  {cpp_time:.2f}s")
    if cpp_time > 0:
        print(f"Speedup: {py_time/cpp_time:.1f}x")


if __name__ == "__main__":
    benchmark_monte_carlo()

