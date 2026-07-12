# Aussie Fire Risk Calculator

Practical Python + Zig project that computes a simplified McArthur-style Fire Danger Index (FDI) across large grids, comparing three paths: pure Python (NumPy), pure Zig, and Python calling Zig via ctypes.

Highlights:
- Real Australian context (Blue Mountains, NSW) for sample data.
- Benchmarks: performance, memory, and accuracy across implementations.
- Clear teaching points on when and how to go polyglot.

Note: This project uses a pedagogical variant of the McArthur Fire Danger Index with clearly documented formulas for determinism and cross-language matching. It is not a drop-in replacement for operational systems.

## Black Summer context

The 2019–2020 Black Summer fires in Australia burned millions of hectares and are estimated to have affected more than a billion animals. Agencies such as the NSW RFS and CSIRO rely on modeling to anticipate risk. This project demonstrates how performance matters when computing risk across millions of grid cells and dates.

References for further reading (non-exhaustive):
- CSIRO bushfire research portal and publications
- McArthur, A. G. Fire Danger Meters (Forest/Grassland) and subsequent updates

## Project structure

```
aussie-fire-risk/
├── pyproject.toml          # uv configuration and console script
├── README.md
├── src/
│   ├── fire_calc/
│   │   ├── __init__.py
│   │   ├── python_impl.py  # Pure Python implementation (NumPy)
│   │   ├── zig_binding.py  # ctypes loader and adapter for Zig lib
│   │   ├── benchmark.py    # Quick benchmarks from Python
│   │   └── cli.py          # fire-calc CLI
│   └── fire_calc_zig/
│       ├── src/
│       │   └── fire_calc.zig
│       └── build.zig
├── data/
│   ├── blue_mountains_weather.csv  # small sample (generated)
│   ├── elevation_data.csv          # small sample (generated)
│   └── generate_data.py            # generator for large synthetic datasets
├── benchmarks/
│   └── performance_comparison.py
├── tests/
│   └── test_implementations.py
└── .github/
    └── workflows/
        └── ci.yml
```

## Mathematical background (simplified and deterministic)

We implement a consistent, cross-language formula inspired by McArthur-style indices:

FDI = 2 * exp((D - FFMC)/50) * (1 + W/10) * T_factor

Where:
- D (Drought Factor) is provided as input (itself can require iterative modeling). For testing, we generate plausible values.
- FFMC (Fine Fuel Moisture Content) is provided as input. In real models it is computed with logarithmic transforms; here, we assume it is supplied to keep Python/Zig parity focused on the FDI core.
- W is 10 m wind speed (m/s) with optional pressure adjustment baked into the dataset.
- T_factor = (T/30) * (1 - 0.5 * RH) * (1 + 0.1 * (elev/2000)) with RH as a fraction (0..1).

The same numeric path is implemented in both Python and Zig for exact reproducibility. All inputs are float64 and results are float64.

## Build and run

Prereqs: Python 3.10+, NumPy; Zig 0.11+ recommended.

Using uv:
- Install deps: `uv sync`
- Generate data: `uv run python data/generate_data.py --rows 10000`
- Build Zig lib: `cd src/fire_calc_zig && zig build -Doptimize=ReleaseFast && cd -`
- Run CLI (Python + Zig):
  - `uv run fire-calc --location katoomba --date 2020-01-15 --use-zig`
  - Or Python only: `uv run fire-calc --location katoomba --date 2020-01-15`

Quick benchmark:
- `uv run python -m fire_calc.benchmark --sizes 10000 100000 1000000`

## Cross-platform

The Zig build installs a shared library into `zig-out/lib` with the correct extension:
- Linux: `libfire_calc.so`
- macOS: `libfire_calc.dylib`
- Windows: `fire_calc.dll`

The Python loader attempts to find the library automatically; override with `FIRE_CALC_LIB_PATH` if needed.

## CI

The included GitHub Actions workflow runs tests and (optionally) builds the Zig library on Linux. Extend for macOS/Windows as needed.

## Disclaimer

This code focuses on pedagogy and benchmarking. Use official, validated models for operational decision-making.

