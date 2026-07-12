"""
Example Python usage of PixelFlow (PyO3 bindings).

Build locally first:
    maturin develop --features python

Then run:
    python examples/python_usage.py
"""

import numpy as np

try:
    import pixelflow  # type: ignore
except Exception as e:
    raise SystemExit("Import failed. Did you run 'maturin develop --features python'?\n" + str(e))


def load_landsat_scene(_path: str, height: int = 512, width: int = 512) -> np.ndarray:
    """Synthetic 4-band scene (R,G,B,NIR) for demo purposes."""
    y, x = np.mgrid[0:height, 0:width].astype(np.float32)
    xf = x / max(1, width)
    yf = y / max(1, height)
    red = np.clip(0.2 + 0.8 * xf, 0.0, 1.0)
    green = np.clip(0.2 + 0.8 * yf, 0.0, 1.0)
    blue = np.clip(0.5 * (1.0 - xf), 0.0, 1.0)
    nir = np.clip(0.6 * (1.0 - yf), 0.0, 1.0)
    # Add a thin vertical hot stripe to simulate fire-like pixels
    red[:, width // 2] = 1.0
    green[:, width // 2] *= 0.3
    return np.stack([red, green, blue, nir], axis=-1).astype(np.float32)


def main():
    landsat = load_landsat_scene("data/landsat_australia.tif")
    red, green, blue, nir = [landsat[:, :, i] for i in range(4)]

    processor = pixelflow.PyMultiSpectralImage(red=red, green=green, blue=blue, nir=nir)

    risk_level = processor.detect_bushfire_risk("blue_mountains")
    print(f"Bushfire risk: {risk_level:.2f}")

    ndvi = processor.calculate_ndvi()
    # ndvi is HxW; scale for preview
    ndvi_img = np.clip(ndvi, 0.0, 1.0) * 255.0
    ndvi_img = ndvi_img.astype(np.uint8)
    try:
        from PIL import Image  # type: ignore
        Image.fromarray(ndvi_img).save("vegetation_health.png")
        print("Saved vegetation_health.png")
    except Exception:
        print("Pillow not installed; skipping image save.")


if __name__ == "__main__":
    main()

