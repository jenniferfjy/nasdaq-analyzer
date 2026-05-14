import pandas as pd
import numpy as np
import pytest
from simulation import simulate_dca
from analysis   import add_rolling_cagr, compute_summary, compute_win_rates, compute_yearly_returns


def make_dca(n_days: int = 2000, daily_usd: float = 10.0) -> pd.DataFrame:
    """Generate a realistic rising price series and run DCA on it."""
    np.random.seed(42)
    dates  = pd.date_range("2010-01-01", periods=n_days, freq="B")
    prices = pd.Series(
        100 * np.exp(np.cumsum(np.random.normal(0.0003, 0.01, n_days))),
        index=dates, name="TEST",
    )
    return simulate_dca(prices, daily_usd)


# ── add_rolling_cagr ──────────────────────────────────────────────────────────

class TestAddRollingCAGR:
    def test_adds_three_columns(self):
        df = add_rolling_cagr(make_dca())
        assert {"cagr_1y", "cagr_3y", "cagr_5y"}.issubset(df.columns)

    def test_short_window_has_nans_at_start(self):
        df = add_rolling_cagr(make_dca())
        # First year of cagr_1y must be NaN (not enough history)
        assert df["cagr_1y"].iloc[:252].isna().all()

    def test_returns_same_dataframe(self):
        dca = make_dca()
        result = add_rolling_cagr(dca)
        assert result is dca  # mutates and returns the same object


# ── compute_summary ───────────────────────────────────────────────────────────

class TestComputeSummary:
    EXPECTED_KEYS = {"Strategy", "Final Value", "Total Invested",
                     "Total Return", "CAGR", "Max Drawdown", "Sharpe Ratio"}

    def test_all_keys_present(self):
        summary = compute_summary(make_dca(), "Test")
        assert self.EXPECTED_KEYS == set(summary.keys())

    def test_strategy_label(self):
        summary = compute_summary(make_dca(), "My Strategy")
        assert summary["Strategy"] == "My Strategy"

    def test_values_are_strings(self):
        summary = compute_summary(make_dca(), "Test")
        for key, val in summary.items():
            assert isinstance(val, str), f"{key} should be a string"

    def test_final_value_formatted_with_dollar(self):
        summary = compute_summary(make_dca(), "Test")
        assert summary["Final Value"].startswith("$")

    def test_cagr_formatted_with_percent(self):
        summary = compute_summary(make_dca(), "Test")
        assert summary["CAGR"].endswith("%")


# ── compute_win_rates ─────────────────────────────────────────────────────────

class TestComputeWinRates:
    def test_returns_three_windows(self):
        dca = add_rolling_cagr(make_dca())
        rates = compute_win_rates(dca)
        assert set(rates.keys()) == {1, 3, 5}

    def test_rates_between_0_and_100(self):
        dca = add_rolling_cagr(make_dca())
        rates = compute_win_rates(dca)
        for window, rate in rates.items():
            assert 0 <= rate <= 100, f"Window {window}Y rate {rate} out of range"

    def test_longer_window_at_least_as_high(self):
        # In a generally rising market, longer windows should win more often
        dca = add_rolling_cagr(make_dca(n_days=3000))
        rates = compute_win_rates(dca)
        assert rates[5] >= rates[1]


# ── compute_yearly_returns ────────────────────────────────────────────────────

class TestComputeYearlyReturns:
    EXPECTED_KEYS = {"price_years", "price_vals", "price_colors",
                     "port_years",  "port_vals",  "port_colors"}

    def test_all_keys_present(self):
        dca    = make_dca()
        prices = pd.Series(
            dca["price"].values, index=dca.index, name="TEST"
        )
        result = compute_yearly_returns(prices, dca)
        assert self.EXPECTED_KEYS == set(result.keys())

    def test_lists_same_length(self):
        dca    = make_dca()
        prices = pd.Series(dca["price"].values, index=dca.index, name="TEST")
        result = compute_yearly_returns(prices, dca)
        assert len(result["price_years"]) == len(result["price_vals"]) == len(result["price_colors"])
        assert len(result["port_years"])  == len(result["port_vals"])  == len(result["port_colors"])

    def test_colors_are_valid_hex(self):
        dca    = make_dca()
        prices = pd.Series(dca["price"].values, index=dca.index, name="TEST")
        result = compute_yearly_returns(prices, dca)
        for color in result["price_colors"] + result["port_colors"]:
            assert color.startswith("#"), f"Color {color!r} is not a hex code"
