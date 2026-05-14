# Planned Improvements

## Data & Accuracy
1. **Local data cache** — currently re-fetches from Yahoo Finance on every run (slow, fragile). Cache to Parquet, fetch only missing dates on subsequent runs.
2. **Include dividends** — QQQ pays dividends; ignoring them understates real returns by ~0.5%/yr. yfinance supports this with `actions=True`.
3. **Inflation-adjusted returns** — show real purchasing power alongside nominal returns using CPI data (FRED API).

## Analysis Depth
4. **Recovery time analysis** — for each major drawdown, show how many days it took to recover to breakeven. More actionable than raw drawdown %.
5. **DCA frequency comparison** — daily vs weekly vs monthly. Most brokerages don't support true daily investing; weekly/monthly is more realistic.
6. **Additional benchmarks** — TLT (bonds), GLD (gold), BTC-USD, and cash (inflation-adjusted) alongside QQQ/SPY.
7. **Monte Carlo projections** — use historical return distributions to simulate the next 10/20/30 years with confidence intervals (10th/50th/90th percentile outcomes).
8. **More risk metrics** — Sortino ratio (penalizes only downside volatility), Calmar ratio (CAGR ÷ max drawdown), and rolling VaR.

## Software Engineering
9. **CLI arguments** — `--ticker`, `--start`, `--daily-amount`, `--output` via `argparse` or `typer` instead of editing `config.py`.
10. **Unit tests** — `simulation.py` and `analysis.py` are pure functions, trivial to test with `pytest`.
11. **Error handling** — network failures, missing tickers, yfinance API changes currently crash with no useful message.

## Report / UX
12. **Interactive amount slider** — JavaScript slider in the HTML lets users change the daily investment amount and see results update without re-running Python.
13. **Sticky table of contents** — the report is long; a fixed-position nav would improve usability significantly.
14. **Mobile layout** — the bear/bull two-column grid breaks on small screens.

---

*Roughly ordered by impact-to-effort ratio within each category.*
*Priority quick wins: #1, #2, #9, #10.*
*Most impressive finance addition: #7 (Monte Carlo).*
