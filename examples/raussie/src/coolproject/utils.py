import numpy as np

def synthetic_uluru(h: int = 1024, w: int = 1024, seed: int = 42) -> np.ndarray:
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[-1:1:h*1j, -1:1:w*1j]
    # Base inselberg mound
    z = 200 * np.exp(-((x*1.5)**2 + (y*0.8)**2) * 4.0)
    # Wind erosion ripples
    z += 10 * np.sin((x + y*0.3) * 20) * np.exp(-((x)**2 + (y*0.5)**2) * 3.0)
    # Random micro relief
    z += rng.normal(0, 0.8, size=(h, w)).astype(np.float32)
    return z.astype(np.float32)

def normalize_cellsize(h: int, w: int, meters: float | None = None) -> float:
    # Assume ~30m nominal resolution if unspecified
    return float(30.0 if meters is None else meters)
