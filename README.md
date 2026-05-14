# NASDAQ Daily DCA Analyzer

Simulates investing a fixed dollar amount into the NASDAQ 100 (QQQ) every trading day, computes performance metrics, and exports a beginner-friendly interactive HTML report.

## Quickstart

```bash
uv run python QQQ.py
```

Then open `nasdaq_dca_report.html` in any browser.

## What the report covers

| Section | Content |
|---------|---------|
| Key Numbers | Total return, CAGR, worst drawdown, 5-year win rate |
| Portfolio Growth | Value vs. cost basis over time, drawdown chart |
| DCA vs. Lump Sum | Side-by-side comparison of both strategies |
| Consistency | Rolling 1/3/5-year annualized returns |
| Win Rate | % of rolling windows that were profitable |
| Post-2020 Spotlight | Annotated chart of the COVID crash, 2022 bear market, and AI boom |
| Year-by-Year | Annual QQQ price return and DCA portfolio return per year |
| Hot Market Question | Current bull/bear case with recent analyst data |
| Glossary | Plain-English definitions of every financial term used |

## Configuration

All tunables are in `config.py`:

```python
DAILY_INVESTMENT = 10        # dollars invested each trading day
START_DATE       = "2004-01-01"
END_DATE         = None      # None = today
OUTPUT_FILE      = "nasdaq_dca_report.html"
```

## Project structure

```
trading/
├── QQQ.py          # entry point — run this
├── config.py       # constants and color palette
├── data.py         # fetch_prices() via yfinance
├── simulation.py   # simulate_dca(), simulate_lumpsum()
├── analysis.py     # metrics, rolling CAGR, win rates, yearly returns
├── charts.py       # one Plotly chart builder per section
└── report.py       # build_html() — assembles the full HTML report
```

## Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (install: `curl -LsSf https://astral.sh/uv/install.sh | sh`)

Dependencies are declared in `pyproject.toml` and pinned in `uv.lock`. Running `uv run` handles the virtual environment automatically — no manual activation needed.
