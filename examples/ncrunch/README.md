# NumCrunch

High-performance scientific computing with C++23 and Python, focused on Monte Carlo simulations for Australian mining risk assessment.

- C++23 core with std::expected, ranges, mdspan, constexpr LUTs
- pybind11 Python bindings via scikit-build-core
- Monte Carlo for geology, environment, and finance
- Target: 100x+ speedup vs pure Python for tight loops

## Install

Prereqs: Python 3.8+, CMake 3.25+, GCC 13+/Clang 16+/MSVC 2022, `pybind11`, `scikit-build-core`.

```
uv pip install numcrunch
# or
pip install numcrunch
```

From source:

```
uv sync
uv run python -m pip install -e . --verbose
```

## Usage

```
import numcrunch as nc
import pandas as pd

model = nc.AustralianMiningModel()
model.load_pilbara_data("data/pilbara_geology.csv")
geo = model.create_geology_model()

engine = nc.MonteCarloEngine(seed=42)
results = engine.run_geological_simulation(model=geo, num_iterations=1_000_000)

# Finance
from numcrunch.mining import make_cash_flows, make_market
npv_dist = engine.calculate_project_npv(
    flows=make_cash_flows([100, 120, 150], [80, 90, 95]),
    market=make_market(base_price=100.0, price_vol=0.2, discount_rate=0.08)
)
```

## Benchmarks

See `benchmarks/performance_comparison.py`. Example output target for 1M iterations:

- Python: ~45s
- C++23: ~0.4s
- Speedup: ~112x

## Layout

```
numcrunch/
├── pyproject.toml
├── CMakeLists.txt
├── src/
│   ├── numcrunch/
│   │   ├── __init__.py
│   │   ├── mining.py
│   │   └── _cpp_core.pyi
│   └── cpp/
│       ├── mining_core.cpp
│       ├── monte_carlo.hpp
│       ├── risk_models.hpp
│       └── python_bindings.cpp
├── data/
│   ├── pilbara_geology.csv
│   ├── commodity_prices.csv
│   └── equipment_reliability.csv
├── benchmarks/
│   ├── performance_comparison.py
│   └── memory_profiling.py
└── examples/
    ├── pilbara_risk_assessment.py
    └── environmental_impact.py
```

## Notes

- `std::mdspan` requires up-to-date standard library. GCC 13+/Clang 16+ recommended.
- If `mdspan` is unavailable, consider adding a fallback or `std::experimental::mdspan`.
- Data files here are toy samples for demos.

