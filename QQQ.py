"""
NASDAQ (QQQ) Daily DCA Analysis
Fetches historical data, simulates daily dollar-cost averaging,
computes performance metrics, and exports an interactive HTML report.

Usage:
    uv run python QQQ.py
    uv run python QQQ.py --amount 25 --start 2010-01-01
    uv run python QQQ.py --output my_report.html
"""

import argparse
import os
import warnings
warnings.filterwarnings("ignore")

import config
from data       import fetch_prices
from simulation import simulate_dca, simulate_lumpsum
from analysis   import (add_rolling_cagr, compute_summary, compute_win_rates, compute_yearly_returns,
                        compute_dca_frequencies, compute_recovery_periods, run_monte_carlo)
import charts as ch
from report     import build_html


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="NASDAQ Daily DCA Analyzer")
    parser.add_argument("--amount", type=float, default=config.DAILY_INVESTMENT,
                        help=f"Daily investment in USD (default: {config.DAILY_INVESTMENT})")
    parser.add_argument("--start",  default=config.START_DATE,
                        help=f"Start date YYYY-MM-DD (default: {config.START_DATE})")
    parser.add_argument("--end",    default=config.END_DATE,
                        help="End date YYYY-MM-DD (default: today)")
    parser.add_argument("--output", default=config.OUTPUT_FILE,
                        help=f"Output HTML path (default: {config.OUTPUT_FILE})")
    args = parser.parse_args()
    _validate_args(args)
    return args


def _validate_args(args: argparse.Namespace) -> None:
    import sys
    from datetime import datetime

    if args.amount <= 0:
        print(f"Error: --amount must be greater than 0 (got {args.amount})")
        sys.exit(1)

    try:
        start_dt = datetime.strptime(args.start, "%Y-%m-%d")
    except ValueError:
        print(f"Error: --start '{args.start}' is not a valid date. Use YYYY-MM-DD format.")
        sys.exit(1)

    if args.end is not None:
        try:
            end_dt = datetime.strptime(args.end, "%Y-%m-%d")
        except ValueError:
            print(f"Error: --end '{args.end}' is not a valid date. Use YYYY-MM-DD format.")
            sys.exit(1)
        if end_dt <= start_dt:
            print(f"Error: --end ({args.end}) must be after --start ({args.start}).")
            sys.exit(1)

    if start_dt.year < 1993:
        print(f"Error: --start must be 1993-01-01 or later (QQQ launched in March 1999).")
        sys.exit(1)


def main() -> None:
    args = parse_args()

    # ── Fetch ──────────────────────────────────────────────────────────────────
    print("Fetching historical data...")
    prices = fetch_prices(["QQQ", "SPY"], args.start, args.end)

    # ── Simulate ───────────────────────────────────────────────────────────────
    qqq_dca = simulate_dca(prices["QQQ"], args.amount)
    spy_dca = simulate_dca(prices["SPY"], args.amount)
    qqq_ls  = simulate_lumpsum(prices["QQQ"], qqq_dca["cum_cost"].iloc[-1])
    spy_ls  = simulate_lumpsum(prices["SPY"], spy_dca["cum_cost"].iloc[-1])

    prices_2020  = prices[prices.index >= "2020-01-01"]
    qqq_dca_2020 = simulate_dca(prices_2020["QQQ"], args.amount)
    spy_dca_2020 = simulate_dca(prices_2020["SPY"], args.amount)

    # ── Analyse ────────────────────────────────────────────────────────────────
    qqq_dca      = add_rolling_cagr(qqq_dca)
    win_rates    = compute_win_rates(qqq_dca)
    yearly_data  = compute_yearly_returns(prices["QQQ"], qqq_dca)
    summary_rows = [
        compute_summary(qqq_dca, "QQQ DCA"),
        compute_summary(spy_dca, "SPY DCA"),
        compute_summary(qqq_ls,  "QQQ Lump-Sum"),
        compute_summary(spy_ls,  "SPY Lump-Sum"),
    ]
    freq_data        = compute_dca_frequencies(prices["QQQ"], args.amount)
    recovery_periods = compute_recovery_periods(prices["QQQ"])
    mc               = run_monte_carlo(prices["QQQ"], args.amount)

    # ── Charts ─────────────────────────────────────────────────────────────────
    print("Building HTML report...")
    chart_a = ch.to_html(ch.make_growth_chart(qqq_dca, spy_dca),              first=True)
    chart_b = ch.to_html(ch.make_comparison_chart(qqq_dca, qqq_ls, spy_dca, spy_ls))
    chart_c = ch.to_html(ch.make_rolling_cagr_chart(qqq_dca))
    chart_d = ch.to_html(ch.make_winrate_chart(win_rates))
    chart_e = ch.to_html(ch.make_post2020_chart(qqq_dca_2020, spy_dca_2020))
    chart_f = ch.to_html(ch.make_yearly_chart(yearly_data))
    chart_g = ch.to_html(ch.make_frequency_chart(freq_data))
    chart_h = ch.to_html(ch.make_recovery_chart(recovery_periods))
    chart_i = ch.to_html(ch.make_monte_carlo_chart(mc))

    # ── Report ─────────────────────────────────────────────────────────────────
    html = build_html(
        prices=prices, qqq_dca=qqq_dca, summary_rows=summary_rows, win_rates=win_rates,
        daily_investment=args.amount,
        chart_a=chart_a, chart_b=chart_b, chart_c=chart_c,
        chart_d=chart_d, chart_e=chart_e, chart_f=chart_f,
        chart_g=chart_g, chart_h=chart_h, chart_i=chart_i,
        mc=mc,
    )

    output_path = os.path.join(os.path.dirname(__file__), args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(html)
    print(f"\nDone! Report saved to: {output_path}")


if __name__ == "__main__":
    main()
