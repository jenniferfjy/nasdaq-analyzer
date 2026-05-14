import pandas as pd

from config import C


def build_html(
    *,
    prices: pd.DataFrame,
    qqq_dca: pd.DataFrame,
    summary_rows: list[dict],
    win_rates: dict,
    daily_investment: float,
    chart_a: str, chart_b: str, chart_c: str,
    chart_d: str, chart_e: str, chart_f: str,
    chart_g: str, chart_h: str, chart_i: str,
    mc: dict,
) -> str:
    start_yr   = prices.index[0].year
    end_yr     = prices.index[-1].year
    final_qqq  = qqq_dca["port_value"].iloc[-1]
    final_cost = qqq_dca["cum_cost"].iloc[-1]
    mult       = final_qqq / final_cost
    n_years    = len(qqq_dca) / 252
    cagr_val   = ((final_qqq / final_cost) ** (1 / n_years) - 1) * 100
    max_dd_val = qqq_dca["drawdown_pct"].min()

    stat_cards = [
        ("Money Multiplied",  f"{mult:.1f}×",       f"Every $1 invested became ${mult:.1f}",      C["blue"]),
        ("Yearly Growth Rate", f"{cagr_val:.1f}%",   "Average annual return (CAGR)",               C["olive"]),
        ("Worst Drop",         f"{max_dd_val:.1f}%", "Biggest portfolio decline from peak",        C["red"]),
        ("5-Year Win Rate",    f"{win_rates[5]:.1f}%", "Any 5-year stretch that was profitable",   C["clay"]),
    ]
    cards_html = "\n".join(f"""
  <div class="stat-card">
    <div class="stat-value" style="color:{color}">{val}</div>
    <div class="stat-label">{label}</div>
    <div class="stat-sub">{sub}</div>
  </div>""" for label, val, sub, color in stat_cards)

    mc_rows = ""
    for years in mc["years_list"]:
        s = mc["stats"][years]
        mc_rows += (
            f'<tr><td>{years} years</td>'
            f'<td>$<span class="sc" data-base="{s["total_invested"]:.2f}">{s["total_invested"]:,.0f}</span></td>'
            f'<td>$<span class="sc" data-base="{s["p10"]:.2f}">{s["p10"]:,.0f}</span></td>'
            f'<td>$<span class="sc" data-base="{s["p50"]:.2f}">{s["p50"]:,.0f}</span></td>'
            f'<td>$<span class="sc" data-base="{s["p90"]:.2f}">{s["p90"]:,.0f}</span></td>'
            f'<td>{s["pct_profitable"]:.1f}%</td></tr>\n'
        )

    table_rows = ""
    for i, row in enumerate(summary_rows):
        bg    = C["g100"] if i % 2 == 0 else C["paper"]
        cells = "".join(f"<td>{v}</td>" for v in row.values())
        table_rows += f'<tr style="background:{bg}">{cells}</tr>\n'
    table_headers = "".join(f"<th>{k}</th>" for k in summary_rows[0].keys())

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Should You Invest in NASDAQ Every Day?</title>
  <style>
    :root {{
      --ivory:  {C["ivory"]};
      --paper:  {C["paper"]};
      --slate:  {C["slate"]};
      --clay:   {C["clay"]};
      --clay-d: {C["clay_d"]};
      --oat:    {C["oat"]};
      --olive:  {C["olive"]};
      --g100:   {C["g100"]};
      --g200:   {C["g200"]};
      --g300:   {C["g300"]};
      --g500:   {C["g500"]};
      --g700:   {C["g700"]};
      --serif:  ui-serif, Georgia, "Times New Roman", Times, serif;
      --sans:   system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--ivory); color: var(--slate); font-family: var(--serif);
      font-size: 17px; line-height: 1.7; max-width: 1100px; margin: 0 auto; padding: 0 24px 80px;
    }}
    .hero {{ padding: 64px 0 48px; border-bottom: 1px solid var(--g200); margin-bottom: 56px; }}
    .hero-label {{
      font-family: var(--sans); font-size: 12px; font-weight: 600;
      letter-spacing: 0.12em; text-transform: uppercase; color: var(--clay); margin-bottom: 16px;
    }}
    h1 {{ font-size: clamp(2rem, 5vw, 3.2rem); font-weight: 400; line-height: 1.2; color: var(--slate); margin-bottom: 20px; max-width: 700px; }}
    h1 em {{ font-style: italic; color: var(--clay); }}
    .hero-sub {{ font-size: 1.1rem; color: var(--g700); max-width: 620px; margin-bottom: 28px; }}
    .hero-meta {{ font-family: var(--sans); font-size: 13px; color: var(--g500); }}
    .verdict {{
      background: var(--slate); color: #F0EEE6; border-radius: 10px;
      padding: 28px 32px; margin-bottom: 56px; font-size: 1.05rem; line-height: 1.75;
    }}
    .verdict strong {{ color: var(--clay); }}
    section {{ margin-bottom: 64px; }}
    .section-label {{
      font-family: var(--sans); font-size: 11px; font-weight: 700;
      letter-spacing: 0.14em; text-transform: uppercase; color: var(--g500); margin-bottom: 10px;
    }}
    h2 {{ font-size: 1.7rem; font-weight: 400; margin-bottom: 16px; color: var(--slate); }}
    h3 {{ font-size: 1.15rem; font-weight: 600; margin-bottom: 8px; font-family: var(--sans); color: var(--slate); }}
    p {{ color: var(--g700); margin-bottom: 14px; }}
    .steps {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-top: 24px; }}
    .step {{ background: var(--paper); border: 1px solid var(--g200); border-radius: 10px; padding: 20px 22px; }}
    .step-num {{
      font-family: var(--sans); font-size: 11px; font-weight: 700;
      letter-spacing: 0.1em; text-transform: uppercase; color: var(--clay); margin-bottom: 8px;
    }}
    .stat-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-top: 24px; }}
    .stat-card {{ background: var(--paper); border: 1px solid var(--g200); border-radius: 10px; padding: 24px 22px; }}
    .stat-value {{ font-size: 2.4rem; font-weight: 300; line-height: 1; margin-bottom: 8px; }}
    .stat-label {{ font-family: var(--sans); font-weight: 600; font-size: 13px; color: var(--slate); margin-bottom: 4px; }}
    .stat-sub {{ font-family: var(--sans); font-size: 12px; color: var(--g500); }}
    .chart-card {{ background: var(--paper); border: 1px solid var(--g200); border-radius: 10px; padding: 24px; margin-top: 20px; }}
    .chart-caption {{ font-family: var(--sans); font-size: 13px; color: var(--g500); margin-top: 12px; line-height: 1.5; }}
    .chart-caption strong {{ color: var(--slate); }}
    .chart-note {{
      background: var(--g100); border-left: 3px solid var(--clay); border-radius: 0 6px 6px 0;
      padding: 12px 16px; font-family: var(--sans); font-size: 13.5px;
      color: var(--g700); line-height: 1.6; margin-bottom: 16px;
    }}
    .chart-note strong {{ color: var(--slate); }}
    .table-wrap {{ overflow-x: auto; margin-top: 20px; }}
    table {{ width: 100%; border-collapse: collapse; font-family: var(--sans); font-size: 13.5px; }}
    th {{ background: var(--slate); color: var(--ivory); font-weight: 600; text-align: left; padding: 10px 14px; white-space: nowrap; }}
    td {{ padding: 10px 14px; border-bottom: 1px solid var(--g200); color: var(--g700); white-space: nowrap; }}
    tr:last-child td {{ border-bottom: none; }}
    .glossary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; margin-top: 20px; }}
    .gloss-item {{ background: var(--paper); border: 1px solid var(--g200); border-radius: 8px; padding: 16px 18px; }}
    .gloss-term {{ font-family: var(--sans); font-weight: 700; font-size: 13px; color: var(--clay); margin-bottom: 4px; }}
    .gloss-def {{ font-size: 14px; color: var(--g700); line-height: 1.55; }}
    .research-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; margin-top: 20px; }}
    .research-card {{ background: var(--paper); border: 1px solid var(--g200); border-radius: 10px; padding: 22px 22px 18px; }}
    .research-source {{
      font-family: var(--sans); font-size: 11px; font-weight: 700;
      letter-spacing: 0.1em; text-transform: uppercase; color: var(--clay); margin-bottom: 8px;
    }}
    .research-card p {{ font-size: 14px; line-height: 1.6; margin-bottom: 0; }}
    footer {{
      border-top: 1px solid var(--g200); padding-top: 24px; margin-top: 64px;
      font-family: var(--sans); font-size: 12px; color: var(--g500); line-height: 1.6;
    }}

    /* ── Sticky TOC ──────────────────────────────────────────────────────── */
    #toc {{
      position: fixed; left: 8px; top: 50%;
      transform: translateY(-50%); background: var(--paper);
      border: 1px solid var(--g200); border-radius: 10px;
      padding: 12px 10px; font-family: var(--sans); font-size: 10px; line-height: 1.4;
      z-index: 100; width: 118px; max-height: 82vh; overflow-y: auto; display: none;
    }}
    @media (min-width: 1500px) {{ #toc {{ display: block; }} }}
    #toc-title {{
      font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;
      color: var(--clay); font-size: 10px; margin-bottom: 10px;
    }}
    #toc ul {{ list-style: none; }}
    #toc li {{ margin-bottom: 2px; }}
    #toc a {{
      text-decoration: none; color: var(--g500); display: block;
      padding: 3px 6px; border-radius: 4px; transition: background 0.15s, color 0.15s;
    }}
    #toc a:hover, #toc a.toc-active {{ background: var(--g100); color: var(--slate); }}

    /* ── Interactive slider ──────────────────────────────────────────────── */
    .slider-wrap {{
      display: flex; align-items: center; gap: 12px;
      font-family: var(--sans); font-size: 14px; margin: 20px 0 8px;
    }}
    #amount-label {{ font-size: 1.5rem; font-weight: 300; color: var(--clay); min-width: 90px; }}
    input[type=range] {{ accent-color: var(--clay); width: 200px; cursor: pointer; }}
    .slider-bounds {{ color: var(--g500); font-size: 12px; }}
    .slider-note {{ font-family: var(--sans); font-size: 12px; color: var(--g500); font-style: italic; }}

    /* ── Mobile fixes ────────────────────────────────────────────────────── */
    @media (max-width: 720px) {{
      body {{ font-size: 15px; padding: 0 14px 64px; }}
      h1 {{ font-size: 1.75rem; }}
      .hero {{ padding: 40px 0 32px; }}
      .two-col {{ grid-template-columns: 1fr !important; }}
      .steps {{ grid-template-columns: 1fr !important; }}
      .stat-grid {{ grid-template-columns: repeat(2, 1fr) !important; }}
      .glossary {{ grid-template-columns: 1fr !important; }}
      input[type=range] {{ width: 140px; }}
    }}
  </style>
</head>
<body>

<nav id="toc">
  <div id="toc-title">Contents</div>
  <ul>
    <li><a href="#s01">01 · Strategy</a></li>
    <li><a href="#s02">02 · Key Numbers</a></li>
    <li><a href="#s03">03 · Portfolio Growth</a></li>
    <li><a href="#s04">04 · DCA vs Lump Sum</a></li>
    <li><a href="#s05">05 · Consistency</a></li>
    <li><a href="#s06">06 · Win Rate</a></li>
    <li><a href="#s07">07 · Post-2020</a></li>
    <li><a href="#s08">08 · Year-by-Year</a></li>
    <li><a href="#s09">09 · Hot Market?</a></li>
    <li><a href="#s10">10 · Full Comparison</a></li>
    <li><a href="#s11">11 · Glossary</a></li>
    <li><a href="#s12">12 · Research</a></li>
    <li><a href="#s13">13 · Frequency</a></li>
    <li><a href="#s14">14 · Crash Recovery</a></li>
    <li><a href="#s15">15 · Monte Carlo</a></li>
  </ul>
</nav>

<header class="hero">
  <div class="hero-label">Investment Analysis · NASDAQ 100</div>
  <h1>Should you invest in the<br><em>NASDAQ every single day?</em></h1>
  <p class="hero-sub">
    We simulated what would have happened if you invested just <strong>${daily_investment:.0f}</strong> every
    trading day into the NASDAQ 100 (QQQ) — starting in {start_yr}. Here's what the data says.
  </p>
  <div class="slider-wrap">
    <span class="slider-bounds">$1</span>
    <input type="range" id="amount-slider" min="1" max="200" value="{daily_investment:.0f}" step="1">
    <span class="slider-bounds">$200</span>
    <span>→ <span id="amount-label">${daily_investment:.0f}/day</span></span>
  </div>
  <p class="slider-note">Drag to explore different daily amounts — key dollar figures update instantly.</p>
  <div class="hero-meta" style="margin-top:12px">Data: {prices.index[0].date()} – {prices.index[-1].date()} &nbsp;·&nbsp; {len(prices):,} trading days &nbsp;·&nbsp; Source: Yahoo Finance</div>
</header>

<div class="verdict">
  <strong>Bottom line:</strong> Investing <span id="verdict-daily">${daily_investment:.0f}</span>/day turned
  <strong>$<span class="sc" data-base="{final_cost:.2f}">{final_cost:,.0f}</span></strong> of contributions
  into <strong>$<span class="sc" data-base="{final_qqq:.2f}">{final_qqq:,.0f}</span></strong>
  — a <strong>{mult:.1f}× return</strong> with an average yearly growth of
  <strong>{cagr_val:.1f}%</strong>. There were painful crashes along the way (the worst drop was
  <strong>{max_dd_val:.1f}%</strong>), but if you held through every storm, <strong>any 5-year stretch
  was profitable {win_rates[5]:.0f}% of the time</strong>. The data strongly supports consistent
  daily investing for long-term investors who can stomach short-term swings.
</div>

<section id="s01">
  <div class="section-label">01 · The Strategy</div>
  <h2>What is "Daily DCA"?</h2>
  <p><strong>Dollar-Cost Averaging (DCA)</strong> just means investing a fixed amount of money on a regular
  schedule — regardless of whether the market is up or down that day. You don't try to predict the market.
  You just keep buying.</p>
  <p>Think of it like buying a coffee every morning. Some days it costs $4.50, some days $5.20. Over time,
  you end up paying a fair average price — and you never stress about whether today is the "right" day to buy.</p>
  <div class="steps">
    <div class="step"><div class="step-num">Step 1</div><h3>Pick an amount</h3>
      <p style="font-size:14px">We used $10/day. You could use $5, $25, or whatever fits your budget.</p></div>
    <div class="step"><div class="step-num">Step 2</div><h3>Buy every trading day</h3>
      <p style="font-size:14px">Market up? Buy. Market down? Buy. No decisions needed — that's the point.</p></div>
    <div class="step"><div class="step-num">Step 3</div><h3>Hold long-term</h3>
      <p style="font-size:14px">Don't panic-sell during crashes. Time in the market is what creates returns.</p></div>
    <div class="step"><div class="step-num">Step 4</div><h3>Watch it compound</h3>
      <p style="font-size:14px">Returns generate more returns. The longer you wait, the steeper the curve.</p></div>
  </div>
</section>

<section id="s02">
  <div class="section-label">02 · Key Numbers</div>
  <h2>The results at a glance</h2>
  <p>These numbers are from the QQQ daily DCA simulation covering {start_yr}–{end_yr}.</p>
  <div class="stat-grid">{cards_html}</div>
</section>

<section id="s03">
  <div class="section-label">03 · Portfolio Growth</div>
  <h2>Your money growing — and dipping — over time</h2>
  <p>The top chart shows your portfolio value versus what you actually put in. The gap between the lines is
  your profit. The bottom chart shows how much the portfolio dropped from its peak at any point.</p>
  <div class="chart-card">
    <div class="chart-note"><strong>What to look for:</strong> The blue line (QQQ) growing well above the dotted
    cost line means you're making money. When the bottom chart dips deep — like in 2008 or 2020 — that's when
    many investors panic and sell. Staying invested through those dips is the key.</div>
    {chart_a}
    <div class="chart-caption"><strong>QQQ</strong> = NASDAQ 100 ETF (top 100 non-financial stocks: Apple, Microsoft, Nvidia…) &nbsp;·&nbsp;
    <strong>SPY</strong> = S&P 500 ETF (500 largest US companies) &nbsp;·&nbsp; <strong>Dotted line</strong> = total dollars you put in</div>
  </div>
</section>

<section id="s04">
  <div class="section-label">04 · DCA vs. Lump Sum</div>
  <h2>What if you invested everything at once?</h2>
  <p>A "lump sum" means putting all your money in on day one. Research shows this beats DCA about 2/3 of the
  time in rising markets — but most people don't have a large sum ready on day one, and it's psychologically
  much harder to stomach big drops.</p>
  <div class="chart-card">
    <div class="chart-note"><strong>Solid lines</strong> = daily DCA &nbsp;·&nbsp; <strong>Dashed lines</strong> = lump sum
    (all money invested on {prices.index[0].date()}). The lump sum line starts higher because it owns more shares
    immediately. DCA catches up gradually as you keep buying.</div>
    {chart_b}
    <div class="chart-caption">Both strategies are shown investing the <em>same total amount of money</em> over
    the same period. The difference is <em>when</em> that money enters the market.</div>
  </div>
</section>

<section id="s05">
  <div class="section-label">05 · Consistency Over Time</div>
  <h2>Was it always a good time to be investing?</h2>
  <p>This chart asks: "For any given year, if you had been DCA-ing for the past 1, 3, or 5 years — were you
  winning?" The line above zero means yes.</p>
  <div class="chart-card">
    <div class="chart-note"><strong>Notice:</strong> The 1-year window (yellow) swings wildly — sometimes great,
    sometimes negative. The 5-year window (blue) stays positive almost the entire time.
    <strong>The longer your horizon, the more reliable the returns.</strong></div>
    {chart_c}
    <div class="chart-caption">CAGR = Compound Annual Growth Rate — the yearly return that would produce the same
    total result. Values below 0% mean the portfolio was worth less than what was invested during that window.</div>
  </div>
</section>

<section id="s06">
  <div class="section-label">06 · Win Rate</div>
  <h2>How often did you come out ahead?</h2>
  <p>Out of every possible start date in our dataset, what % of rolling windows ended in profit?</p>
  <div class="chart-card">
    <div class="chart-note">A 1-year window is risky — almost 1 in 5 periods lost money. But <strong>no 5-year
    window in the last 22 years ended in a loss.</strong> This is why financial advisors say "invest for the long term."</div>
    {chart_d}
    <div class="chart-caption">Calculated over {len(prices):,} trading days. Each bar shows the percentage of all
    rolling periods of that length where the portfolio finished above the total amount invested.</div>
  </div>
</section>

<section id="s07">
  <div class="section-label">07 · Post-2020 Spotlight</div>
  <h2>The wild ride since 2020</h2>
  <p>The period from 2020 to today compressed several market extremes into just five years: a historic crash,
  a historic recovery, a brutal tech bear market, and an AI-driven surge. If you DCA'd through all of it,
  here's what happened.</p>
  <div class="chart-card">
    <div class="chart-note"><strong>Key moments marked on the chart:</strong> The COVID crash in March 2020 saw
    QQQ drop ~30% in weeks. Investors who kept buying through the crash were rewarded when the market recovered
    to new highs by August 2020. The 2022 bear market (−35% for QQQ) tested conviction again — but those who
    held through it saw their DCA portfolios reach all-time highs in 2023–2025.</div>
    {chart_e}
    <div class="chart-caption">Simulation starts fresh on 2020-01-01 with ${daily_investment:.0f}/day. Annotations mark
    major turning points. The bottom panel shows drawdown — how far the portfolio fell from its peak.</div>
  </div>
</section>

<section id="s08">
  <div class="section-label">08 · Year-by-Year</div>
  <h2>How did each year actually look?</h2>
  <p>The <strong>top chart</strong> shows QQQ's raw price change each calendar year. The <strong>bottom chart</strong>
  shows the DCA investor's total portfolio profit or loss relative to everything they had invested by year-end.
  DCA returns are smoother — averaging in through bad years means you never have your entire pot exposed at the worst moment.</p>
  <div class="chart-card">
    <div class="chart-note"><strong>Red years to remember:</strong> 2008 (Financial Crisis, −42%), 2022 (rate hikes &amp;
    tech selloff, −33%). In both cases, the DCA investor was in far better shape than someone who had invested a lump sum
    at the start of that year, because they had bought shares cheaply throughout the downturn.</div>
    {chart_f}
    <div class="chart-caption">Top: raw annual % price change for QQQ. Bottom: DCA portfolio's total unrealized return
    (portfolio value vs. cumulative cost) at year-end.</div>
  </div>
</section>

<section id="s09">
  <div class="section-label">09 · The Hot Market Question</div>
  <h2>"The market looks expensive — should I wait?"</h2>
  <p>This is the most common hesitation among new investors. The market has had a strong run, valuations are elevated,
  and it feels like a bad time to start. Here's the honest picture from both sides — and what the data actually says.</p>

  <div class="two-col" style="display:grid; grid-template-columns:1fr 1fr; gap:20px; margin:24px 0;">
    <div style="background:var(--paper); border:1px solid var(--g200); border-top:3px solid {C["red"]}; border-radius:10px; padding:22px;">
      <div class="section-label" style="color:{C["red"]}">Bear Case — Reasons to be cautious</div>
      <ul style="font-family:var(--sans); font-size:14px; color:var(--g700); line-height:1.8; padding-left:18px; margin-top:12px;">
        <li><strong>Stretched valuations:</strong> QQQ's P/E ratio sits around 34×, above its 5-year average of 30×. High P/E entry points historically lead to lower 10-year returns.</li>
        <li><strong>Concentration risk:</strong> The top 5 holdings (Apple, Microsoft, Nvidia, Amazon, Meta) make up ~40% of QQQ. A stumble from any one of them hits the whole index hard.</li>
        <li><strong>52-week range tension:</strong> As of early 2026, QQQ sat just 2% below its all-time high with a 35% gap between its yearly high and low — elevated volatility and uncertainty.</li>
        <li><strong>Macro headwinds:</strong> Tariff uncertainty, stubborn inflation, and geopolitical tensions could weigh on tech earnings and compress multiples.</li>
        <li><strong>"Approaching bubble territory":</strong> Multiple analysts have flagged parallels to late 1990s valuations, though earnings quality today is far stronger than in the dot-com era.</li>
      </ul>
    </div>
    <div style="background:var(--paper); border:1px solid var(--g200); border-top:3px solid {C["olive"]}; border-radius:10px; padding:22px;">
      <div class="section-label" style="color:{C["olive"]}">Bull Case — Reasons to keep investing</div>
      <ul style="font-family:var(--sans); font-size:14px; color:var(--g700); line-height:1.8; padding-left:18px; margin-top:12px;">
        <li><strong>AI infrastructure supercycle:</strong> Analysts project $5–8 trillion in cumulative AI infrastructure spending through 2030. Nvidia, Microsoft, and Amazon — all top QQQ holdings — are direct beneficiaries.</li>
        <li><strong>Earnings are real:</strong> Unlike the dot-com era, today's NASDAQ leaders have enormous, growing profits. Apple, Microsoft, and Nvidia collectively earn hundreds of billions per year.</li>
        <li><strong>Technical breakout signal:</strong> QQQ's 10-day moving average crossed above its 50-day moving average in April 2026 — a bullish signal that has historically preceded further gains.</li>
        <li><strong>Rate cut tailwinds:</strong> Potential Fed rate cuts in 2026 would lower borrowing costs and boost the present value of future tech earnings, supporting high P/E stocks.</li>
        <li><strong>Wall Street consensus:</strong> The majority of analysts covering QQQ have a positive 12-month outlook, with price targets implying 10–15% upside from current levels.</li>
      </ul>
    </div>
  </div>

  <h3 style="margin-top:8px">What the historical data actually says about buying at peaks</h3>
  <div class="chart-note" style="margin-top:12px">
    <strong>Buying at all-time highs has historically been fine.</strong> Research by Bank of America found that buying
    the S&P 500 only on days when it hit a new all-time high still produced average 12-month returns of +7.5% —
    nearly identical to buying on any random day. Markets spend roughly <strong>1 in every 3 trading days</strong>
    at or near all-time highs during bull markets. Waiting for a "safer" entry often means missing most of the gains.
  </div>

  <h3 style="margin-top:24px">So what should you actually do?</h3>
  <p>DCA sidesteps the timing question entirely — you're not betting on whether today is cheap or expensive,
  you're committing to buying through all conditions. But if valuations genuinely concern you, here are
  evidence-based adjustments:</p>
  <div class="steps" style="margin-top:16px">
    <div class="step"><div class="step-num">Option 1</div><h3>Keep DCA-ing</h3>
      <p style="font-size:14px">If your horizon is 5+ years, current valuation is unlikely to matter. History shows 100% of 5-year windows were profitable.</p></div>
    <div class="step"><div class="step-num">Option 2</div><h3>Diversify</h3>
      <p style="font-size:14px">Add some SPY (broader S&P 500) or international ETFs alongside QQQ to reduce concentration in tech megacaps.</p></div>
    <div class="step"><div class="step-num">Option 3</div><h3>Reduce but don't stop</h3>
      <p style="font-size:14px">If you're nervous, invest half your usual amount now and hold the rest in a high-yield savings account. Add it gradually over 6–12 months.</p></div>
    <div class="step"><div class="step-num">Option 4</div><h3>Never try to time it</h3>
      <p style="font-size:14px">Schwab's research: even investors with "perfect bad luck" (always buying at yearly peaks) still massively outperformed those who waited in cash.</p></div>
  </div>
  <p style="margin-top:24px; font-family:var(--sans); font-size:13px; color:var(--g500);">
    Sources:
    <a href="https://www.benzinga.com/analyst-ratings/analyst-color/25/04/44894251/sp-500-approaching-bubble-territory-us-stocks-remain-historically-overvalued-despite-recent-correction-says-market-researcher" style="color:var(--clay)">Benzinga — S&P Approaching Bubble Territory</a> ·
    <a href="https://www.barchart.com/story/news/1448517/the-qqq-chart-hints-at-2-extremes-either-a-dot-com-bubble-burst-or-a-technical-breakout-ahead" style="color:var(--clay)">Barchart — QQQ: Bubble Burst or Breakout?</a> ·
    <a href="https://tickeron.com/blogs/qqq-outlook-2026-an-ai-informed-view-of-the-nasdaq-100-etf-s-future-11624/" style="color:var(--clay)">Tickeron — QQQ Outlook 2026</a> ·
    <a href="https://www.fool.com/investing/2026/04/16/where-qqq-be-12-months-wall-street-analyst-answer/" style="color:var(--clay)">Motley Fool — Where Will QQQ Be in 12 Months?</a>
  </p>
</section>

<section id="s10">
  <div class="section-label">10 · Full Comparison</div>
  <h2>All four strategies, side by side</h2>
  <p>Comparing QQQ vs. SPY, and DCA vs. lump sum, over the full {start_yr}–{end_yr} period.</p>
  <div class="table-wrap">
    <table>
      <thead><tr>{table_headers}</tr></thead>
      <tbody>{table_rows}</tbody>
    </table>
  </div>
</section>

<section id="s11">
  <div class="section-label">11 · Plain-English Glossary</div>
  <h2>What do these terms mean?</h2>
  <div class="glossary">
    <div class="gloss-item"><div class="gloss-term">DCA — Dollar-Cost Averaging</div>
      <div class="gloss-def">Investing a fixed dollar amount on a regular schedule, no matter what the market is doing. Reduces the risk of investing everything at a market peak.</div></div>
    <div class="gloss-item"><div class="gloss-term">QQQ</div>
      <div class="gloss-def">An ETF that tracks the NASDAQ 100 — the 100 largest non-financial companies on the NASDAQ exchange. Heavily weighted toward tech (Apple, Microsoft, Nvidia, Amazon).</div></div>
    <div class="gloss-item"><div class="gloss-term">CAGR — Compound Annual Growth Rate</div>
      <div class="gloss-def">The steady yearly return that would produce the same total result. If you turned $1,000 into $2,000 in 7 years, your CAGR is about 10%/year.</div></div>
    <div class="gloss-item"><div class="gloss-term">Drawdown</div>
      <div class="gloss-def">How far your portfolio has fallen from its highest point. A −40% drawdown means the portfolio is worth 40% less than at its peak. Drawdowns are temporary if you hold on.</div></div>
    <div class="gloss-item"><div class="gloss-term">Sharpe Ratio</div>
      <div class="gloss-def">A measure of return per unit of risk. A higher number means you're getting more reward for each unit of volatility you endure. Above 1.0 is generally considered good.</div></div>
    <div class="gloss-item"><div class="gloss-term">Lump Sum Investing</div>
      <div class="gloss-def">Investing all your money at once rather than spreading it over time. Historically beats DCA in bull markets, but harder psychologically and riskier if you pick a bad entry point.</div></div>
  </div>
</section>

<section id="s12">
  <div class="section-label">12 · Supporting Research</div>
  <h2>What the experts say</h2>
  <p>Our findings align with decades of academic and industry research on long-term equity investing.</p>
  <div class="research-grid">
    <div class="research-card"><div class="research-source">Vanguard Research · 2012</div>
      <h3>"Invest now or temporarily hold your cash?"</h3>
      <p>Vanguard found that lump-sum investing outperforms DCA about two-thirds of the time. However, for investors who don't have a large sum available upfront, DCA is the practical and psychologically safer approach — it gets money into the market consistently.</p></div>
    <div class="research-card"><div class="research-source">Charles Schwab · 2012 Study</div>
      <h3>Time in the market beats timing the market</h3>
      <p>Schwab's landmark study showed that even an investor with perfect bad luck — always buying at the yearly market peak — still came out well ahead of someone who stayed in cash waiting for the "right" moment.</p></div>
    <div class="research-card"><div class="research-source">JP Morgan Asset Management</div>
      <h3>Missing the best days is catastrophic</h3>
      <p>JP Morgan's research shows that if you missed just the 10 best trading days in a 20-year S&P 500 period, your return was cut roughly in half. DCA keeps you fully invested, preventing you from sitting on the sidelines.</p></div>
    <div class="research-card"><div class="research-source">Warren Buffett · Berkshire Hathaway Letters</div>
      <h3>"For most investors, a low-cost index fund is the best choice"</h3>
      <p>Buffett has repeatedly advised average investors to buy and hold a low-cost S&P 500 index fund consistently. He even bet $1 million that an index fund would outperform hedge funds over 10 years. He won.</p></div>
    <div class="research-card"><div class="research-source">Dalbar QAIB Study · Annual</div>
      <h3>Behavior is the biggest risk</h3>
      <p>Dalbar's annual study consistently finds that average investors earn far less than the funds they invest in — because they buy high and sell low. Automating DCA removes emotion from the equation entirely.</p></div>
    <div class="research-card"><div class="research-source">Fama &amp; French · Academic Research</div>
      <h3>Long-term equity premium is real</h3>
      <p>Nobel laureate Eugene Fama's research confirms that equities have historically delivered a meaningful premium over safer assets over long periods. Patient, diversified equity investing has been rewarded — but the key word is <em>patient</em>.</p></div>
  </div>
</section>

<section id="s13">
  <div class="section-label">13 · DCA Frequency</div>
  <h2>Does it matter how often you invest?</h2>
  <p>What if instead of investing daily, you invested weekly or monthly — but kept the same <em>annual</em> spend?
  The amounts are scaled so each strategy puts in the same total dollars per year: ${daily_investment:.0f}/day
  becomes ${daily_investment * 252 / 52:.2f}/week or ${daily_investment * 252 / 12:.2f}/month.</p>
  <div class="chart-card">
    <div class="chart-note"><strong>Key finding:</strong> Daily DCA often edges out weekly and monthly over long
    horizons because it buys into more price dips, but the differences are usually small.
    The <em>consistency</em> of any schedule matters far more than its frequency.</div>
    {chart_g}
    <div class="chart-caption">All three strategies invest the same total amount annually.
    Final bar chart shows the ending portfolio value for each frequency.</div>
  </div>
</section>

<section id="s14">
  <div class="section-label">14 · Crash &amp; Recovery</div>
  <h2>How long did it take to recover from each crash?</h2>
  <p>Every major drawdown ended with a recovery — eventually. This chart shows how long each crash took
  to reach its worst point (red bar) and how many more days it took to climb back to the previous high (green bar).</p>
  <div class="chart-card">
    <div class="chart-note"><strong>The dot-com crash was the worst:</strong> QQQ fell 83% and took over a decade
    to fully recover. More recent crashes — 2020, 2022 — recovered within 1–2 years. Diversifying into SPY reduces
    the depth and duration of these drawdowns.</div>
    {chart_h}
    <div class="chart-caption">Red segment = calendar days from peak to trough. Green segment = days from trough
    back to a new all-time high. Crashes that have not yet recovered show "Ongoing".</div>
  </div>
</section>

<section id="s15">
  <div class="section-label">15 · Monte Carlo Simulation</div>
  <h2>What could the future look like?</h2>
  <p>We ran 1,000 simulations of the next {max(mc["years_list"])} years by randomly sampling from QQQ's
  historical daily return distribution. Each simulation is a possible future — not a prediction, but a range
  of plausible outcomes based on past volatility and average returns.</p>
  <div class="chart-card">
    <div class="chart-note"><strong>How to read this:</strong> The dark blue band is where most outcomes land
    (25th–75th percentile). The lighter band captures 80% of all outcomes. The median line is the "middle" scenario.
    The dotted line is your total investment — outcomes above it are profitable.</div>
    {chart_i}
    <div class="chart-caption">Based on historical return distribution (mean and standard deviation of daily returns).
    This is not a forecast — actual results will differ. 1,000 simulations, ${daily_investment:.0f}/day.</div>
  </div>
  <div class="table-wrap" style="margin-top:24px">
    <table>
      <thead><tr>
        <th>Horizon</th><th>Total Invested</th>
        <th>Pessimistic (10th %ile)</th><th>Median (50th %ile)</th>
        <th>Optimistic (90th %ile)</th><th>Probability of Profit</th>
      </tr></thead>
      <tbody>{mc_rows}</tbody>
    </table>
  </div>
</section>

<footer>
  <p><strong>Disclaimer:</strong> This analysis is for educational purposes only and does not constitute financial advice.
  Past performance does not guarantee future results. All simulations assume no taxes or transaction fees.
  Prices are <em>total-return adjusted</em> via Yahoo Finance (dividends and splits are factored into the price series).
  Generated {prices.index[-1].date()}.</p>
</footer>


<script>
(function () {{
  // ── Slider ──────────────────────────────────────────────────────────────
  const BASE   = {daily_investment:.4f};
  const slider = document.getElementById('amount-slider');
  const label  = document.getElementById('amount-label');
  const vDaily = document.getElementById('verdict-daily');

  function fmt(n) {{
    return '$' + Math.round(n).toLocaleString('en-US');
  }}

  slider.addEventListener('input', function () {{
    const amt   = parseFloat(this.value);
    const ratio = amt / BASE;
    label.textContent = '$' + amt.toFixed(0) + '/day';
    if (vDaily) vDaily.textContent = '$' + amt.toFixed(0);
    document.querySelectorAll('.sc').forEach(function (el) {{
      el.textContent = Math.round(parseFloat(el.dataset.base) * ratio).toLocaleString('en-US');
    }});
  }});

  // ── TOC active section ──────────────────────────────────────────────────
  const sections = Array.from(document.querySelectorAll('section[id]'));
  const tocLinks = Array.from(document.querySelectorAll('#toc a'));

  if ('IntersectionObserver' in window) {{
    const obs = new IntersectionObserver(function (entries) {{
      entries.forEach(function (e) {{
        if (e.isIntersecting) {{
          tocLinks.forEach(function (l) {{ l.classList.remove('toc-active'); }});
          const a = document.querySelector('#toc a[href="#' + e.target.id + '"]');
          if (a) a.classList.add('toc-active');
        }}
      }});
    }}, {{ rootMargin: '0px 0px -60% 0px', threshold: 0 }});
    sections.forEach(function (s) {{ obs.observe(s); }});
  }}
}})();
</script>

</body>
</html>"""
