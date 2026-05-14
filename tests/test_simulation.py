import pandas as pd
import numpy as np
import pytest
from simulation import simulate_dca, simulate_lumpsum


def make_prices(values: list[float]) -> pd.Series:
    dates = pd.date_range("2020-01-01", periods=len(values), freq="B")
    return pd.Series(values, index=dates, dtype=float, name="TEST")


# ── simulate_dca ──────────────────────────────────────────────────────────────

class TestSimulateDCA:
    def test_cumulative_cost(self):
        prices = make_prices([100.0] * 5)
        df = simulate_dca(prices, daily_usd=10)
        assert df["cum_cost"].iloc[-1] == pytest.approx(50.0)

    def test_cumulative_cost_increments(self):
        prices = make_prices([100.0] * 4)
        df = simulate_dca(prices, daily_usd=10)
        expected = [10, 20, 30, 40]
        assert list(df["cum_cost"]) == pytest.approx(expected)

    def test_shares_accumulate_correctly(self):
        # $10/day at prices [100, 50, 200] → shares per day [0.1, 0.2, 0.05]
        prices = make_prices([100.0, 50.0, 200.0])
        df = simulate_dca(prices, daily_usd=10)
        expected_cum_shares = [0.1, 0.3, 0.35]
        port_values = [s * p for s, p in zip(expected_cum_shares, [100, 50, 200])]
        assert list(df["port_value"]) == pytest.approx(port_values)

    def test_flat_price_no_drawdown(self):
        prices = make_prices([100.0] * 10)
        df = simulate_dca(prices, daily_usd=10)
        assert (df["drawdown_pct"] == 0).all()

    def test_drawdown_never_positive(self):
        prices = make_prices([100, 120, 80, 90, 110, 95])
        df = simulate_dca(prices, daily_usd=10)
        assert (df["drawdown_pct"] <= 0).all()

    def test_total_return_positive_trend(self):
        # Steadily rising price → always profitable at the end
        prices = make_prices([10 + i for i in range(20)])
        df = simulate_dca(prices, daily_usd=10)
        assert df["total_return_pct"].iloc[-1] > 0

    def test_output_columns(self):
        df = simulate_dca(make_prices([100.0] * 3), daily_usd=10)
        assert {"price", "cum_cost", "port_value", "total_return_pct", "drawdown_pct"}.issubset(df.columns)

    def test_index_matches_input(self):
        prices = make_prices([100.0, 110.0, 90.0])
        df = simulate_dca(prices, daily_usd=10)
        assert list(df.index) == list(prices.index)


# ── simulate_lumpsum ──────────────────────────────────────────────────────────

class TestSimulateLumpsum:
    def test_shares_fixed_after_day_one(self):
        prices = make_prices([100.0, 200.0, 50.0])
        df = simulate_lumpsum(prices, total_usd=100)
        # 1 share bought on day 1 at $100 — portfolio value = 1 * price each day
        assert list(df["port_value"]) == pytest.approx([100.0, 200.0, 50.0])

    def test_cost_is_constant(self):
        prices = make_prices([100.0] * 5)
        df = simulate_lumpsum(prices, total_usd=500)
        assert (df["cum_cost"] == 500).all()

    def test_double_price_gives_100pct_return(self):
        prices = make_prices([100.0, 200.0])
        df = simulate_lumpsum(prices, total_usd=100)
        assert df["total_return_pct"].iloc[-1] == pytest.approx(100.0)

    def test_drawdown_never_positive(self):
        prices = make_prices([100, 80, 120, 60, 110])
        df = simulate_lumpsum(prices, total_usd=1000)
        assert (df["drawdown_pct"] <= 0).all()

    def test_output_columns(self):
        df = simulate_lumpsum(make_prices([100.0] * 3), total_usd=100)
        assert {"port_value", "cum_cost", "total_return_pct", "drawdown_pct"}.issubset(df.columns)
