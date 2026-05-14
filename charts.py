import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import C

PLOT_LAYOUT = dict(
    template="plotly_white",
    paper_bgcolor=C["paper"],
    plot_bgcolor=C["ivory"],
    font=dict(family="Georgia, 'Times New Roman', serif", color=C["slate"], size=12),
    legend=dict(orientation="h", y=-0.15, font=dict(size=11)),
    hovermode="x unified",
    margin=dict(t=40, b=60, l=60, r=20),
)

_AXIS_STYLE = dict(
    showgrid=True, gridcolor=C["g200"], gridwidth=1,
    zeroline=False, linecolor=C["g300"],
)


def _style_axes(fig: go.Figure, rows: int | None = None) -> None:
    if rows:
        for r in range(1, rows + 1):
            fig.update_xaxes(**_AXIS_STYLE, row=r, col=1)
            fig.update_yaxes(**_AXIS_STYLE, row=r, col=1)
    else:
        fig.update_xaxes(**_AXIS_STYLE)
        fig.update_yaxes(**_AXIS_STYLE)


def to_html(fig: go.Figure, first: bool = False) -> str:
    return fig.to_html(full_html=False, include_plotlyjs="cdn" if first else False)


def make_growth_chart(qqq_dca: pd.DataFrame, spy_dca: pd.DataFrame) -> go.Figure:
    fig = make_subplots(rows=2, cols=1,
        subplot_titles=("Your Money Growing Over Time", "How Deep Did the Portfolio Dip? (Drawdown)"),
        vertical_spacing=0.14, row_heights=[0.65, 0.35])

    fig.add_trace(go.Scatter(x=qqq_dca.index, y=qqq_dca["port_value"],
        name="QQQ Portfolio Value", line=dict(color=C["blue"], width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=spy_dca.index, y=spy_dca["port_value"],
        name="SPY Portfolio Value", line=dict(color=C["olive"], width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=qqq_dca.index, y=qqq_dca["cum_cost"],
        name="Total Invested (Cost)", line=dict(color=C["g500"], width=1.5, dash="dot")), row=1, col=1)
    fig.add_trace(go.Scatter(x=qqq_dca.index, y=qqq_dca["drawdown_pct"],
        name="QQQ Drawdown", fill="tozeroy",
        line=dict(color=C["red"], width=1.5),
        fillcolor="rgba(192,57,43,0.12)"), row=2, col=1)

    fig.update_layout(height=640, **PLOT_LAYOUT)
    fig.update_yaxes(tickprefix="$", row=1, col=1)
    fig.update_yaxes(ticksuffix="%", row=2, col=1)
    _style_axes(fig, rows=2)
    return fig


def make_comparison_chart(
    qqq_dca: pd.DataFrame, qqq_ls: pd.DataFrame,
    spy_dca: pd.DataFrame, spy_ls: pd.DataFrame,
) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=qqq_dca.index, y=qqq_dca["port_value"],
        name="QQQ — Daily DCA", line=dict(color=C["blue"], width=2)))
    fig.add_trace(go.Scatter(x=qqq_ls.index, y=qqq_ls["port_value"],
        name="QQQ — Lump Sum", line=dict(color=C["blue"], width=1.5, dash="dash")))
    fig.add_trace(go.Scatter(x=spy_dca.index, y=spy_dca["port_value"],
        name="SPY — Daily DCA", line=dict(color=C["olive"], width=2)))
    fig.add_trace(go.Scatter(x=spy_ls.index, y=spy_ls["port_value"],
        name="SPY — Lump Sum", line=dict(color=C["olive"], width=1.5, dash="dash")))

    fig.update_layout(height=380, yaxis=dict(tickprefix="$"), **PLOT_LAYOUT)
    _style_axes(fig)
    return fig


def make_rolling_cagr_chart(qqq_dca: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=qqq_dca.index, y=qqq_dca["cagr_1y"],
        name="1-Year Window", line=dict(color=C["amber"], width=1.5)))
    fig.add_trace(go.Scatter(x=qqq_dca.index, y=qqq_dca["cagr_3y"],
        name="3-Year Window", line=dict(color=C["clay"], width=2)))
    fig.add_trace(go.Scatter(x=qqq_dca.index, y=qqq_dca["cagr_5y"],
        name="5-Year Window", line=dict(color=C["blue"], width=2.5)))
    fig.add_hline(y=0, line=dict(color=C["red"], width=1, dash="dot"))

    fig.update_layout(height=360, yaxis=dict(ticksuffix="%"), **PLOT_LAYOUT)
    _style_axes(fig)
    return fig


def make_winrate_chart(win_rates: dict[int, float]) -> go.Figure:
    fig = go.Figure(go.Bar(
        x=["1 Year", "3 Years", "5 Years"],
        y=[win_rates[1], win_rates[3], win_rates[5]],
        text=[f"{win_rates[k]:.1f}%" for k in [1, 3, 5]],
        textposition="outside",
        marker_color=[C["amber"], C["clay"], C["blue"]],
        marker_line_width=0,
    ))
    fig.update_layout(height=320,
        yaxis=dict(range=[0, 108], ticksuffix="%", title="% of periods profitable"),
        xaxis=dict(title="Rolling window length"),
        **PLOT_LAYOUT)
    _style_axes(fig)
    return fig


_POST2020_EVENTS = [
    ("2020-03-23", "COVID crash bottom", "above"),
    ("2021-11-19", "Post-COVID peak",    "below"),
    ("2022-10-13", "Bear market bottom", "above"),
    ("2023-01-01", "AI boom begins",     "below"),
    ("2025-01-01", "2025 rally",         "above"),
]


def make_post2020_chart(qqq_dca_2020: pd.DataFrame, spy_dca_2020: pd.DataFrame) -> go.Figure:
    fig = make_subplots(rows=2, cols=1,
        subplot_titles=("Post-2020 DCA: Portfolio vs. Cost Basis", "Drawdown Since 2020"),
        vertical_spacing=0.14, row_heights=[0.65, 0.35])

    fig.add_trace(go.Scatter(x=qqq_dca_2020.index, y=qqq_dca_2020["port_value"],
        name="QQQ Portfolio", line=dict(color=C["blue"], width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=spy_dca_2020.index, y=spy_dca_2020["port_value"],
        name="SPY Portfolio", line=dict(color=C["olive"], width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=qqq_dca_2020.index, y=qqq_dca_2020["cum_cost"],
        name="Cost Basis", line=dict(color=C["g500"], width=1.5, dash="dot")), row=1, col=1)

    for date_str, label, pos in _POST2020_EVENTS:
        try:
            dt      = pd.Timestamp(date_str)
            idx     = qqq_dca_2020.index.searchsorted(dt)
            nearest = qqq_dca_2020.index[min(idx, len(qqq_dca_2020) - 1)]
            val     = qqq_dca_2020.loc[nearest, "port_value"]
            ay      = 40 if pos == "above" else -40
            fig.add_annotation(x=dt, y=val, text=label, showarrow=True,
                arrowhead=2, arrowcolor=C["clay"], arrowsize=0.8,
                font=dict(size=10, color=C["clay_d"]),
                ax=0, ay=ay, row=1, col=1)
        except Exception:
            pass

    fig.add_trace(go.Scatter(x=qqq_dca_2020.index, y=qqq_dca_2020["drawdown_pct"],
        name="QQQ Drawdown", fill="tozeroy",
        line=dict(color=C["red"], width=1.5),
        fillcolor="rgba(192,57,43,0.12)"), row=2, col=1)

    fig.update_layout(height=620, **PLOT_LAYOUT)
    fig.update_yaxes(tickprefix="$", row=1, col=1)
    fig.update_yaxes(ticksuffix="%", row=2, col=1)
    _style_axes(fig, rows=2)
    return fig


def make_yearly_chart(yearly: dict) -> go.Figure:
    fig = make_subplots(rows=2, cols=1,
        subplot_titles=(
            "QQQ Annual Price Return (per year)",
            "QQQ DCA Portfolio Return vs. Cost Basis (end of year)",
        ),
        vertical_spacing=0.18)

    fig.add_trace(go.Bar(
        x=yearly["price_years"], y=yearly["price_vals"],
        text=[f"{v:.1f}%" for v in yearly["price_vals"]],
        textposition="outside", textfont=dict(size=10),
        marker_color=yearly["price_colors"], marker_line_width=0,
        name="Annual Price Return",
    ), row=1, col=1)
    fig.add_hline(y=0, line=dict(color=C["slate"], width=1), row=1, col=1)

    fig.add_trace(go.Bar(
        x=yearly["port_years"], y=yearly["port_vals"],
        text=[f"{v:.0f}%" for v in yearly["port_vals"]],
        textposition="outside", textfont=dict(size=10),
        marker_color=yearly["port_colors"], marker_line_width=0,
        name="DCA Portfolio vs Cost",
    ), row=2, col=1)
    fig.add_hline(y=0, line=dict(color=C["slate"], width=1), row=2, col=1)

    fig.update_layout(height=620, showlegend=False, **PLOT_LAYOUT)
    fig.update_yaxes(ticksuffix="%", row=1, col=1)
    fig.update_yaxes(ticksuffix="%", row=2, col=1)
    _style_axes(fig, rows=2)
    return fig


def make_frequency_chart(freq: dict) -> go.Figure:
    fig = make_subplots(rows=1, cols=2,
        subplot_titles=("Portfolio Value Over Time", "Final Portfolio Value"),
        column_widths=[0.65, 0.35])

    colors = {"daily": C["blue"], "weekly": C["clay"], "monthly": C["olive"]}
    labels = {
        "daily":   f"Daily (${freq['daily_usd']:.2f}/day)",
        "weekly":  f"Weekly (${freq['weekly_usd']:.2f}/wk)",
        "monthly": f"Monthly (${freq['monthly_usd']:.2f}/mo)",
    }

    final_vals = []
    for key in ("daily", "weekly", "monthly"):
        df = freq[key]
        fig.add_trace(go.Scatter(
            x=df.index, y=df["port_value"],
            name=labels[key], line=dict(color=colors[key], width=2),
        ), row=1, col=1)
        final_vals.append(df["port_value"].iloc[-1])

    fig.add_trace(go.Bar(
        x=list(labels.values()), y=final_vals,
        marker_color=[colors["daily"], colors["weekly"], colors["monthly"]],
        marker_line_width=0, showlegend=False,
        text=[f"${v:,.0f}" for v in final_vals], textposition="outside",
    ), row=1, col=2)

    fig.update_layout(height=400, **PLOT_LAYOUT)
    fig.update_yaxes(tickprefix="$", row=1, col=1)
    fig.update_yaxes(tickprefix="$", row=1, col=2)
    _style_axes(fig)
    return fig


def make_recovery_chart(periods: list[dict]) -> go.Figure:
    labels      = [p["label"] for p in periods]
    to_trough   = [p["days_to_trough"] for p in periods]
    to_recover  = [p["days_to_recover"] if p["days_to_recover"] else 0 for p in periods]
    dd_labels   = [f"{p['max_drawdown_pct']:.1f}%" for p in periods]
    ongoing     = [p["recovery_date"] is None for p in periods]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Peak → Trough", y=labels, x=to_trough,
        orientation="h", marker_color=C["red"], marker_line_width=0,
        text=dd_labels, textposition="inside", textfont=dict(color="white", size=11),
    ))
    fig.add_trace(go.Bar(
        name="Trough → Recovery", y=labels,
        x=[r if not o else None for r, o in zip(to_recover, ongoing)],
        orientation="h", marker_color=C["olive"], marker_line_width=0,
        text=["Ongoing" if o else f"{r}d" for r, o in zip(to_recover, ongoing)],
        textposition="inside", textfont=dict(color="white", size=11),
    ))

    fig.update_layout(
        barmode="stack", height=max(280, 80 * len(periods)),
        xaxis=dict(title="Calendar days"),
        **PLOT_LAYOUT,
    )
    _style_axes(fig)
    return fig


def make_monte_carlo_chart(mc: dict) -> go.Figure:
    dates = mc["dates"]
    fig = go.Figure()

    # Outer band p10–p90
    fig.add_trace(go.Scatter(
        x=list(dates) + list(dates[::-1]),
        y=list(mc["p90"]) + list(mc["p10"][::-1]),
        fill="toself", fillcolor="rgba(59,111,212,0.10)",
        line=dict(width=0), name="10th–90th percentile", showlegend=True,
    ))
    # Inner band p25–p75
    fig.add_trace(go.Scatter(
        x=list(dates) + list(dates[::-1]),
        y=list(mc["p75"]) + list(mc["p25"][::-1]),
        fill="toself", fillcolor="rgba(59,111,212,0.22)",
        line=dict(width=0), name="25th–75th percentile", showlegend=True,
    ))
    # Median
    fig.add_trace(go.Scatter(
        x=dates, y=mc["p50"],
        name="Median outcome", line=dict(color=C["blue"], width=2.5),
    ))
    # Cost basis
    fig.add_trace(go.Scatter(
        x=dates, y=mc["cost_basis"],
        name="Total invested", line=dict(color=C["g500"], width=1.5, dash="dot"),
    ))

    # Milestone annotations
    for years in mc["years_list"]:
        idx = years * 252 - 1
        fig.add_vline(x=dates[idx], line=dict(color=C["g300"], width=1, dash="dash"))
        fig.add_annotation(
            x=dates[idx], y=mc["p90"][idx],
            text=f"{years}Y", showarrow=False,
            font=dict(size=11, color=C["g500"]),
            yshift=14,
        )

    fig.update_layout(height=440, yaxis=dict(tickprefix="$"), **PLOT_LAYOUT)
    _style_axes(fig)
    return fig
