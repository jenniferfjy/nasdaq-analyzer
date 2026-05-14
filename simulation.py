import numpy as np
import pandas as pd


def simulate_dca(price_series: pd.Series, daily_usd: float) -> pd.DataFrame:
    shares      = daily_usd / price_series
    cum_shares  = shares.cumsum()
    cum_cost    = daily_usd * np.arange(1, len(price_series) + 1)
    port_value  = cum_shares * price_series

    df = pd.DataFrame({
        "price":      price_series.values,
        "cum_cost":   cum_cost,
        "port_value": port_value.values,
    }, index=price_series.index)

    df["total_return_pct"] = (df["port_value"] - df["cum_cost"]) / df["cum_cost"] * 100
    running_max = df["port_value"].cummax()
    df["drawdown_pct"] = (df["port_value"] - running_max) / running_max * 100
    return df


def simulate_lumpsum(price_series: pd.Series, total_usd: float) -> pd.DataFrame:
    shares     = total_usd / price_series.iloc[0]
    port_value = shares * price_series

    df = pd.DataFrame({
        "port_value": port_value.values,
        "cum_cost":   total_usd,
    }, index=price_series.index)

    df["total_return_pct"] = (df["port_value"] - total_usd) / total_usd * 100
    running_max = df["port_value"].cummax()
    df["drawdown_pct"] = (df["port_value"] - running_max) / running_max * 100
    return df
