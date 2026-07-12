from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=10000)
    ap.add_argument("--outdir", type=str, default=str(Path(__file__).parent))
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(2020)

    rows = args.rows
    # Simplified single-day snapshot for demo
    df_weather = pd.DataFrame(
        {
            "location": ["katoomba"] * rows,
            "date": ["2020-01-15"] * rows,
            "temperature_c": rng.uniform(10, 45, rows),
            "humidity_frac": rng.uniform(0.05, 0.8, rows),
            "wind_speed_ms": rng.uniform(0, 25, rows),
            "ffmc": rng.uniform(60, 95, rows),
            "drought_factor": rng.uniform(0, 10, rows),
        }
    )
    df_elev = pd.DataFrame(
        {
            "location": ["katoomba"] * rows,
            "elevation_m": rng.uniform(100, 1500, rows),
        }
    )

    weather_csv = outdir / "blue_mountains_weather.csv"
    elev_csv = outdir / "elevation_data.csv"
    df_weather.to_csv(weather_csv, index=False)
    df_elev.to_csv(elev_csv, index=False)
    print(f"Wrote {weather_csv} and {elev_csv}")


if __name__ == "__main__":
    main()

