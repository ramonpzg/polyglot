"""
Python-friendly interface around the C++ core.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np

try:
    # Import compiled module
    from . import _cpp_core as _core
except Exception:  # pragma: no cover
    _core = None  # Allows import without build for docs/type checking


def _require_core():
    if _core is None:
        raise RuntimeError(
            "_cpp_core extension not built. Install in editable mode or build the wheel."
        )


class MonteCarloEngine:
    def __init__(self, seed: int | None = None):
        _require_core()
        self._impl = _core.MonteCarloEngine(0 if seed is None else int(seed))

    def run_geological_simulation(self, model, num_iterations: int = 1_000_000):
        return self._impl.run_geological_simulation(model, int(num_iterations))

    def calculate_project_npv(self, flows, market):
        return self._impl.calculate_project_npv(flows, market)


class AustralianMiningModel:
    def __init__(self):
        _require_core()
        self._impl = _core.AustralianMiningModel()

    def load_pilbara_data(self, data_file: str):
        return self._impl.load_pilbara_data(data_file)

    def create_geology_model(self):
        return self._impl.create_geology_model()

    def simulate_water_contamination(self, source, years: int):
        return self._impl.simulate_water_contamination(source, int(years))


# Convenience builders for finance inputs
@dataclass
class CashFlow:
    revenue: float
    cost: float


@dataclass
class MarketParameters:
    base_price: float
    price_vol: float
    discount_rate: float


def make_cash_flows(revenues: Sequence[float], costs: Sequence[float]):
    _require_core()
    if len(revenues) != len(costs):
        raise ValueError("revenues and costs must have same length")
    flows = [_core.CashFlow(float(r), float(c)) for r, c in zip(revenues, costs)]
    return flows


def make_market(base_price: float, price_vol: float, discount_rate: float):
    _require_core()
    return _core.MarketParameters(float(base_price), float(price_vol), float(discount_rate))

