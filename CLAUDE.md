# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Run

```bash
uv run python QQQ.py          # fetch data, run analysis, write nasdaq_dca_report.html
```

No build step, no tests, no linter configured. Dependencies are managed by `uv` (`pyproject.toml` + `uv.lock`); the `.venv` is created automatically on first `uv run`.

## Architecture

The pipeline runs in one direction: **fetch → simulate → analyse → chart → report**.

`QQQ.py` is the thin orchestrator — it calls one function from each module in order and passes results forward. No module imports from another module (except `config.py`, which everything imports).

| Module | Responsibility |
|--------|---------------|
| `config.py` | Single source of truth for `DAILY_INVESTMENT`, `START_DATE`, `END_DATE`, `OUTPUT_FILE`, and the CSS color palette `C` |
| `data.py` | `fetch_prices(tickers, start, end)` — downloads OHLCV via yfinance, returns a `DataFrame` of closing prices |
| `simulation.py` | `simulate_dca()` and `simulate_lumpsum()` — both return a `DataFrame` with `cum_cost`, `port_value`, `total_return_pct`, `drawdown_pct` columns |
| `analysis.py` | `add_rolling_cagr()` mutates the DCA DataFrame in place (adds `cagr_1y/3y/5y`); `compute_summary()`, `compute_win_rates()`, `compute_yearly_returns()` produce dicts consumed by `report.py` |
| `charts.py` | One `make_*()` function per chart section, all returning `go.Figure`. Shared `PLOT_LAYOUT` dict and `_style_axes()` keep visual style consistent. `to_html()` wraps `fig.to_html()` with CDN-include logic (only the first chart embeds Plotly.js) |
| `report.py` | `build_html(**kwargs)` — receives all computed data and pre-rendered chart HTML strings, returns the full HTML document as a string. CSS lives here. |

## Key conventions

- All colors reference `C["key"]` from `config.py` — never hardcode hex values elsewhere.
- The first chart passed to `to_html()` must use `first=True` so Plotly.js is included via CDN once; all subsequent charts pass `first=False`.
- `simulate_lumpsum` uses the total invested by the DCA strategy as its `total_usd`, ensuring fair apples-to-apples comparison.
- The post-2020 simulation is a fresh `simulate_dca` call on a date-sliced price series — it does not share state with the full-history DCA DataFrames.
