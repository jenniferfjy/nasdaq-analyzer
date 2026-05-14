import numpy as np
import pandas as pd

from config import C
from simulation import simulate_dca


def add_rolling_cagr(df: pd.DataFrame) -> pd.DataFrame:
    for years in [1, 3, 5]:
        w         = years * 252
        start_val = df["cum_cost"].shift(w)
        cagr      = ((df["port_value"] / start_val) ** (1 / years) - 1) * 100
        df[f"cagr_{years}y"] = cagr.where(start_val.notna())
    return df


def compute_summary(df: pd.DataFrame, label: str) -> dict:
    final_val  = df["port_value"].iloc[-1]
    final_cost = df["cum_cost"].iloc[-1]
    total_ret  = (final_val - final_cost) / final_cost * 100
    n_years    = len(df) / 252
    cagr       = ((final_val / final_cost) ** (1 / n_years) - 1) * 100
    max_dd     = df["drawdown_pct"].min()
    daily_ret  = df["port_value"].pct_change().dropna()
    sharpe     = daily_ret.mean() / daily_ret.std() * np.sqrt(252)
    return {
        "Strategy":       label,
        "Final Value":    f"${final_val:,.0f}",
        "Total Invested": f"${final_cost:,.0f}",
        "Total Return":   f"{total_ret:.1f}%",
        "CAGR":           f"{cagr:.1f}%",
        "Max Drawdown":   f"{max_dd:.1f}%",
        "Sharpe Ratio":   f"{sharpe:.2f}",
    }


def compute_win_rates(df: pd.DataFrame) -> dict[int, float]:
    rates = {}
    for years in [1, 3, 5]:
        valid = df[f"cagr_{years}y"].dropna()
        rates[years] = (valid > 0).mean() * 100
        print(f"  QQQ DCA win rate ({years}Y window): {rates[years]:.1f}%")
    return rates


def compute_yearly_returns(qqq_prices: pd.Series, dca_df: pd.DataFrame) -> dict:
    annual_price = qqq_prices.resample("YE").last()
    price_ret    = annual_price.pct_change().dropna() * 100

    annual_port  = dca_df["port_value"].resample("YE").last()
    annual_cost  = pd.Series(dca_df["cum_cost"].values, index=dca_df.index).resample("YE").last()
    port_ret     = ((annual_port - annual_cost) / annual_cost * 100).dropna()

    return {
        "price_years":  price_ret.index.year.tolist(),
        "price_vals":   price_ret.values.tolist(),
        "price_colors": [C["olive"] if r >= 0 else C["red"] for r in price_ret.values],
        "port_years":   port_ret.index.year.tolist(),
        "port_vals":    port_ret.values.tolist(),
        "port_colors":  [C["olive"] if r >= 0 else C["red"] for r in port_ret.values],
    }


def compute_dca_frequencies(prices: pd.Series, daily_usd: float) -> dict:
    """Compare daily, weekly, and monthly DCA — same annual spend across all."""
    # Annual equivalent: daily_usd × 252 trading days
    weekly_usd  = daily_usd * 252 / 52
    monthly_usd = daily_usd * 252 / 12

    weekly_prices  = prices.resample("W").first().dropna()
    monthly_prices = prices.resample("MS").first().dropna()

    daily   = simulate_dca(prices,         daily_usd)
    weekly  = simulate_dca(weekly_prices,  weekly_usd)
    monthly = simulate_dca(monthly_prices, monthly_usd)

    return {"daily": daily, "weekly": weekly, "monthly": monthly,
            "daily_usd": daily_usd, "weekly_usd": weekly_usd, "monthly_usd": monthly_usd}


_EVENT_LABELS = {
    2000: "Dot-com Bust",
    2007: "Financial Crisis",
    2020: "COVID Crash",
    2022: "Rate Hike Selloff",
}


def compute_recovery_periods(qqq_prices: pd.Series, min_drawdown: float = -15.0) -> list[dict]:
    """Identify major drawdown events and how long QQQ took to recover."""
    running_max = qqq_prices.cummax()
    dd_pct      = (qqq_prices - running_max) / running_max * 100

    # Dates where a new all-time high was set
    new_ath = running_max > running_max.shift(1, fill_value=0)

    periods = []
    state   = "ok"
    peak_date = trough_date = None
    min_dd_seen = 0.0

    for date, dd in dd_pct.items():
        if state == "ok":
            if dd < min_drawdown:
                state = "drawdown"
                ath_before = new_ath[new_ath & (new_ath.index <= date)]
                peak_date  = ath_before.index[-1] if not ath_before.empty else date
                trough_date = date
                min_dd_seen = dd
        else:  # drawdown
            if dd < min_dd_seen:
                min_dd_seen = dd
                trough_date = date
            elif dd >= 0:
                year  = peak_date.year
                label = _EVENT_LABELS.get(year, f"{year} Crash")
                periods.append({
                    "label":            label,
                    "peak_date":        peak_date,
                    "trough_date":      trough_date,
                    "recovery_date":    date,
                    "max_drawdown_pct": min_dd_seen,
                    "days_to_trough":   (trough_date - peak_date).days,
                    "days_to_recover":  (date - trough_date).days,
                    "total_days":       (date - peak_date).days,
                })
                state = "ok"
                min_dd_seen = 0.0

    # Still in drawdown at end of data
    if state == "drawdown":
        year  = peak_date.year
        label = _EVENT_LABELS.get(year, f"{year} Crash")
        periods.append({
            "label":            label,
            "peak_date":        peak_date,
            "trough_date":      trough_date,
            "recovery_date":    None,
            "max_drawdown_pct": min_dd_seen,
            "days_to_trough":   (trough_date - peak_date).days,
            "days_to_recover":  None,
            "total_days":       None,
        })

    return periods


def run_monte_carlo(
    prices:     pd.Series,
    daily_usd:  float,
    years_list: list[int] = [10, 20, 30],
    n_sims:     int = 1000,
) -> dict:
    """Simulate future DCA returns by sampling from historical daily return distribution."""
    daily_ret = prices.pct_change().dropna()
    mu        = daily_ret.mean()
    sigma     = daily_ret.std()

    max_years = max(years_list)
    n_days    = max_years * 252
    np.random.seed(42)

    sim_ret   = np.random.normal(mu, sigma, (n_sims, n_days))
    price_paths = prices.iloc[-1] * np.cumprod(1 + sim_ret, axis=1)  # (n_sims, n_days)
    daily_shares = daily_usd / price_paths
    cum_shares   = np.cumsum(daily_shares, axis=1)
    port_values  = cum_shares * price_paths                            # (n_sims, n_days)
    cost_basis   = daily_usd * np.arange(1, n_days + 1)

    future_dates = pd.date_range(prices.index[-1] + pd.Timedelta(days=1), periods=n_days, freq="B")

    stats = {}
    for years in years_list:
        idx    = years * 252 - 1
        vals   = port_values[:, idx]
        invest = cost_basis[idx]
        stats[years] = {
            "total_invested":  invest,
            "p10": np.percentile(vals, 10),
            "p25": np.percentile(vals, 25),
            "p50": np.percentile(vals, 50),
            "p75": np.percentile(vals, 75),
            "p90": np.percentile(vals, 90),
            "pct_profitable": (vals > invest).mean() * 100,
        }

    # Percentile paths across all days (for fan chart)
    return {
        "dates":      future_dates,
        "cost_basis": cost_basis,
        "p10":  np.percentile(port_values, 10, axis=0),
        "p25":  np.percentile(port_values, 25, axis=0),
        "p50":  np.percentile(port_values, 50, axis=0),
        "p75":  np.percentile(port_values, 75, axis=0),
        "p90":  np.percentile(port_values, 90, axis=0),
        "stats":      stats,
        "years_list": years_list,
        "daily_usd":  daily_usd,
    }
