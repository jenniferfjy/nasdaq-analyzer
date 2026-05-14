import yfinance as yf
import pandas as pd


def fetch_prices(tickers: list[str], start: str, end: str | None = None) -> pd.DataFrame:
    raw = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)
    prices = raw["Close"].dropna()
    print(f"  {len(prices)} trading days loaded ({prices.index[0].date()} → {prices.index[-1].date()})")
    return prices
