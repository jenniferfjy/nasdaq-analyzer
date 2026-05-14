from pathlib import Path

import pandas as pd
import yfinance as yf

CACHE_DIR = Path(__file__).parent / "cache"


def fetch_prices(tickers: list[str], start: str, end: str | None = None) -> pd.DataFrame:
    CACHE_DIR.mkdir(exist_ok=True)
    series = {ticker: _load_ticker(ticker, start, end) for ticker in tickers}
    prices  = pd.DataFrame(series).dropna()
    if prices.empty:
        raise ValueError(
            f"No price data returned for {tickers} between {start} and {end or 'today'}. "
            "Check that the tickers are valid and the date range contains trading days."
        )
    print(f"  {len(prices)} trading days loaded ({prices.index[0].date()} → {prices.index[-1].date()})")
    return prices


def _load_ticker(ticker: str, start: str, end: str | None) -> pd.Series:
    cache_file = CACHE_DIR / f"{ticker}.parquet"
    end_ts     = pd.Timestamp.now().normalize() if end is None else pd.Timestamp(end)
    start_ts   = pd.Timestamp(start)

    if cache_file.exists():
        try:
            cached = pd.read_parquet(cache_file).squeeze()
        except Exception:
            print(f"  Cache for {ticker} is corrupted — re-downloading...")
            cache_file.unlink()
            return _load_ticker(ticker, start, end)

        last_date = cached.index[-1]
        if last_date < end_ts - pd.Timedelta(days=1):
            print(f"  Updating {ticker} cache ({last_date.date()} → today)...")
            fresh = _download(ticker, start=last_date + pd.Timedelta(days=1), end=end)
            if not fresh.empty:
                cached = pd.concat([cached, fresh])
                cached = cached[~cached.index.duplicated(keep="last")]
                cached.to_frame("Close").to_parquet(cache_file)
        return cached[cached.index >= start_ts]

    print(f"  Fetching {ticker} (first run — downloading full history)...")
    data = _download(ticker, start=start, end=end)
    if data.empty:
        raise ValueError(
            f"Ticker '{ticker}' returned no data. It may be invalid or delisted. "
            "Check the symbol at finance.yahoo.com."
        )
    data.to_frame("Close").to_parquet(cache_file)
    return data


def _download(ticker: str, start: str | pd.Timestamp, end: str | None) -> pd.Series:
    try:
        raw = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
    except Exception as e:
        raise ConnectionError(
            f"Failed to download data for '{ticker}'. "
            f"Check your internet connection and try again.\n  Details: {e}"
        ) from e

    close = raw["Close"]
    if hasattr(close, "columns"):   # MultiIndex guard
        close = close.iloc[:, 0]
    return close.rename(ticker)
