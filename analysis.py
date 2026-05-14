import numpy as np
import pandas as pd

from config import C


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
