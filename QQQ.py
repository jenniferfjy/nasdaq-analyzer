"""
NASDAQ (QQQ) Daily DCA Analysis
Fetches historical data, simulates daily dollar-cost averaging,
computes performance metrics, and exports an interactive HTML report.

Usage:
    uv run python QQQ.py
"""

import os
import warnings
warnings.filterwarnings("ignore")

from config     import DAILY_INVESTMENT, START_DATE, END_DATE, OUTPUT_FILE
from data       import fetch_prices
from simulation import simulate_dca, simulate_lumpsum
from analysis   import add_rolling_cagr, compute_summary, compute_win_rates, compute_yearly_returns
import charts as ch
from report     import build_html


def main() -> None:
    # ── Fetch ──────────────────────────────────────────────────────────────────
    print("Fetching historical data...")
    prices = fetch_prices(["QQQ", "SPY"], START_DATE, END_DATE)

    # ── Simulate ───────────────────────────────────────────────────────────────
    qqq_dca = simulate_dca(prices["QQQ"], DAILY_INVESTMENT)
    spy_dca = simulate_dca(prices["SPY"], DAILY_INVESTMENT)
    qqq_ls  = simulate_lumpsum(prices["QQQ"], qqq_dca["cum_cost"].iloc[-1])
    spy_ls  = simulate_lumpsum(prices["SPY"], spy_dca["cum_cost"].iloc[-1])

    prices_2020  = prices[prices.index >= "2020-01-01"]
    qqq_dca_2020 = simulate_dca(prices_2020["QQQ"], DAILY_INVESTMENT)
    spy_dca_2020 = simulate_dca(prices_2020["SPY"], DAILY_INVESTMENT)

    # ── Analyse ────────────────────────────────────────────────────────────────
    qqq_dca     = add_rolling_cagr(qqq_dca)
    win_rates   = compute_win_rates(qqq_dca)
    yearly_data = compute_yearly_returns(prices["QQQ"], qqq_dca)
    summary_rows = [
        compute_summary(qqq_dca, "QQQ DCA"),
        compute_summary(spy_dca, "SPY DCA"),
        compute_summary(qqq_ls,  "QQQ Lump-Sum"),
        compute_summary(spy_ls,  "SPY Lump-Sum"),
    ]

    # ── Charts ─────────────────────────────────────────────────────────────────
    print("Building HTML report...")
    chart_a = ch.to_html(ch.make_growth_chart(qqq_dca, spy_dca),              first=True)
    chart_b = ch.to_html(ch.make_comparison_chart(qqq_dca, qqq_ls, spy_dca, spy_ls))
    chart_c = ch.to_html(ch.make_rolling_cagr_chart(qqq_dca))
    chart_d = ch.to_html(ch.make_winrate_chart(win_rates))
    chart_e = ch.to_html(ch.make_post2020_chart(qqq_dca_2020, spy_dca_2020))
    chart_f = ch.to_html(ch.make_yearly_chart(yearly_data))

    # ── Report ─────────────────────────────────────────────────────────────────
    html = build_html(
        prices=prices, qqq_dca=qqq_dca, summary_rows=summary_rows, win_rates=win_rates,
        chart_a=chart_a, chart_b=chart_b, chart_c=chart_c,
        chart_d=chart_d, chart_e=chart_e, chart_f=chart_f,
    )

    output_path = os.path.join(os.path.dirname(__file__), OUTPUT_FILE)
    with open(output_path, "w") as f:
        f.write(html)
    print(f"\nDone! Report saved to: {output_path}")


if __name__ == "__main__":
    main()
