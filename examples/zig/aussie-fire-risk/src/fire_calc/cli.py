from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Optional

import numpy as np
import typer

from .python_impl import fdi_python
from .zig_binding import fdi_zig

app = typer.Typer(add_completion=False)


def _load_sample_data(location: str, date: str, rows: int = 10000):
    # For demo, generate synthetic inputs; could read CSVs in data/ if present
    rng = np.random.default_rng(abs(hash((location, date))) % (2**32))
    n = rows
    d = rng.uniform(0, 10, n)
    f = rng.uniform(60, 95, n)
    w = rng.uniform(0, 25, n)
    t = rng.uniform(10, 45, n)
    h = rng.uniform(0.05, 0.8, n)
    e = rng.uniform(0, 2000, n)
    return d, f, w, t, h, e


@app.command()
def main(
    location: str = typer.Option("katoomba", help="Location name"),
    date: str = typer.Option("2020-01-15", help="Date YYYY-MM-DD"),
    use_zig: bool = typer.Option(False, help="Use Zig for computation"),
    rows: int = typer.Option(100000, min=1, help="Number of grid points"),
):
    """Compute FDI for a given location/date and print summary statistics."""
    # Validate date
    try:
        dt.date.fromisoformat(date)
    except ValueError:
        raise typer.BadParameter("Invalid date format, expected YYYY-MM-DD")

    d, f, w, t, h, e = _load_sample_data(location, date, rows=rows)

    if use_zig:
        out = fdi_zig(d, f, w, t, h, e)
        backend = "zig"
    else:
        out = fdi_python(d, f, w, t, h, e)
        backend = "python"

    print(f"Backend={backend} | N={rows} | location={location} | date={date}")
    print(
        "FDI stats: min={:.3f} median={:.3f} mean={:.3f} max={:.3f}".format(
            float(out.min()), float(np.median(out)), float(out.mean()), float(out.max())
        )
    )


if __name__ == "__main__":
    app()

