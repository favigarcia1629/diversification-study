import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

from data.fetch import fetch_prices, get_returns, MAG7, DIVERSIFIED, BENCHMARK
from analysis.metrics import (
    portfolio_returns, cumulative_returns, rolling_sharpe,
    summary_table, cagr, annualized_volatility, sharpe_ratio,
    max_drawdown, sortino_ratio, calmar_ratio,
)
from analysis.backtest import run_backtest, REGIMES

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Diversification vs Concentration | Market Study",
    page_icon="📊",
    layout="wide",
)

COLORS = {
    "Magnificent 7 (Concentrated)": "#FF6B35",
    "Diversified (11 Sectors)":     "#2196F3",
    "S&P 500 (SPY Benchmark)":      "#9E9E9E",
}

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<h1 style='text-align:center; color:#FFFFFF; margin-bottom:4px'>
    📊 Diversification vs. Concentration
</h1>
<p style='text-align:center; color:#AAAAAA; font-size:1.1rem; margin-bottom:0'>
    Does spreading risk still make sense when a handful of stocks dominate the market?
</p>
<hr style='border:1px solid #333; margin:18px 0'>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Fetching market data...")
def load():
    return run_backtest()

strategies, cum_returns, regime_df, prices, returns = load()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    show_regimes = st.toggle("Highlight market regimes", value=True)
    risk_free = st.slider("Risk-free rate (%)", 0.0, 6.0, 4.0, 0.25) / 100
    st.markdown("---")
    st.markdown("**Portfolios**")
    st.markdown("🟠 **Concentrated** — Mag7 (equal-weight)")
    st.markdown("🔵 **Diversified** — 11 sectors, 1 stock each")
    st.markdown("⚫ **Benchmark** — SPY (S&P 500 ETF)")
    st.markdown("---")
    st.caption("Data via yfinance · 2019–2025")

# ── KPI Row ───────────────────────────────────────────────────────────────────
st.subheader("Full Period Snapshot (Jan 2019 – Apr 2025)")
cols = st.columns(3)
for col, (name, ret) in zip(cols, strategies.items()):
    with col:
        c = cagr(ret)
        s = sharpe_ratio(ret, risk_free)
        md = max_drawdown(ret)
        growth = cumulative_returns(ret).iloc[-1]
        color = COLORS[name]
        st.markdown(f"""
        <div style='background:#1A1A2E; border-left: 4px solid {color};
                    padding:16px; border-radius:8px; margin-bottom:8px'>
            <div style='color:{color}; font-weight:700; font-size:1rem'>{name.split(" (")[0]}</div>
            <div style='font-size:2rem; font-weight:800; color:#FFF'>${growth:.2f}</div>
            <div style='color:#AAA; font-size:0.82rem'>per $1 invested</div>
            <div style='display:flex; gap:16px; margin-top:10px'>
                <div><div style='color:#FFF; font-weight:600'>{c:.1%}</div><div style='color:#888;font-size:0.75rem'>CAGR</div></div>
                <div><div style='color:#FFF; font-weight:600'>{s:.2f}</div><div style='color:#888;font-size:0.75rem'>Sharpe</div></div>
                <div><div style='color:#FF6B6B; font-weight:600'>{md:.1%}</div><div style='color:#888;font-size:0.75rem'>Max DD</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tab layout ────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Growth", "📉 Drawdown", "⚖️ Rolling Sharpe",
    "🗓️ By Regime", "🔗 Correlations"
])

# Regime shading helper
REGIME_BANDS = [
    ("2020-02-19", "2020-03-23", "rgba(255,68,68,0.12)",  "COVID Crash"),
    ("2022-01-01", "2022-12-31", "rgba(255,140,0,0.10)",  "Rate Hike Bear"),
    ("2023-01-01", "2024-12-31", "rgba(68,187,68,0.08)",  "AI Boom"),
]

def add_regime_bands(fig):
    if not show_regimes:
        return
    for start, end, color, label in REGIME_BANDS:
        fig.add_vrect(
            x0=start, x1=end,
            fillcolor=color, line_width=0,
            annotation_text=label,
            annotation_position="top left",
            annotation_font_size=10,
            annotation_font_color="#AAAAAA",
        )

# ── Tab 1: Growth ─────────────────────────────────────────────────────────────
with tab1:
    st.markdown("### 💵 $1 Invested in January 2019 — Where Are You Now?")
    fig = go.Figure()
    for name, series in cum_returns.items():
        fig.add_trace(go.Scatter(
            x=series.index, y=series.values,
            name=name, line=dict(color=COLORS[name], width=2.5),
            hovertemplate="%{y:.2f}x<extra>" + name + "</extra>",
        ))
    add_regime_bands(fig)
    fig.update_layout(
        template="plotly_dark", height=480,
        yaxis_title="Portfolio Value (×)", xaxis_title="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Shaded regions show key market regimes. All portfolios equal-weighted and rebalanced daily.")

# ── Tab 2: Drawdown ───────────────────────────────────────────────────────────
with tab2:
    st.markdown("### 📉 How Far Did Each Strategy Fall?")
    fig = go.Figure()
    for name, ret in strategies.items():
        cum = cumulative_returns(ret)
        roll_max = cum.cummax()
        dd = ((cum - roll_max) / roll_max) * 100
        fig.add_trace(go.Scatter(
            x=dd.index, y=dd.values,
            name=name, fill="tozeroy",
            line=dict(color=COLORS[name], width=1.8),
            fillcolor=COLORS[name] + "55",
            hovertemplate="%{y:.1f}%<extra>" + name + "</extra>",
        ))
    fig.update_layout(
        template="plotly_dark", height=450,
        yaxis_title="Drawdown (%)", xaxis_title="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Max drawdown comparison
    dd_cols = st.columns(3)
    for col, (name, ret) in zip(dd_cols, strategies.items()):
        md = max_drawdown(ret)
        dd_col_color = COLORS[name]
        with col:
            st.metric(label=name.split(" (")[0], value=f"{md:.1%}", delta="Max Drawdown", delta_color="inverse")

# ── Tab 3: Rolling Sharpe ────────────────────────────────────────────────────
with tab3:
    st.markdown("### ⚖️ Risk-Adjusted Returns — Rolling 6-Month Sharpe")
    fig = go.Figure()
    for name, ret in strategies.items():
        rs = rolling_sharpe(ret, window=126, risk_free=risk_free)
        fig.add_trace(go.Scatter(
            x=rs.index, y=rs.values,
            name=name, line=dict(color=COLORS[name], width=2),
            hovertemplate="Sharpe: %{y:.2f}<extra>" + name + "</extra>",
        ))
    fig.add_hline(y=0, line_dash="dash", line_color="#555555", line_width=1)
    fig.add_hline(y=1, line_dash="dot", line_color="#444444", line_width=0.8,
                  annotation_text="Sharpe = 1", annotation_position="bottom right")
    add_regime_bands(fig)
    fig.update_layout(
        template="plotly_dark", height=450,
        yaxis_title="Rolling Sharpe Ratio", xaxis_title="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Risk-free rate set to {risk_free:.1%} (adjustable in sidebar). Window: 126 trading days.")

# ── Tab 4: By Regime ─────────────────────────────────────────────────────────
with tab4:
    st.markdown("### 🗓️ Performance Breakdown by Market Regime")

    regime_order = [
        "Pre-COVID Bull (2019)",
        "COVID Crash (2020)",
        "COVID Recovery (2020-2021)",
        "Rate Hike Bear (2022)",
        "AI Boom (2023-2024)",
        "2025 YTD",
    ]

    # CAGR heatmap
    pivot_cagr = regime_df.pivot(index="Strategy", columns="Regime", values="CAGR") * 100
    valid_cols = [c for c in regime_order if c in pivot_cagr.columns]
    pivot_cagr = pivot_cagr[valid_cols]

    fig = px.imshow(
        pivot_cagr,
        color_continuous_scale="RdYlGn",
        color_continuous_midpoint=0,
        text_auto=".1f",
        aspect="auto",
        title="CAGR (%) by Regime — green = outperform, red = underperform",
    )
    fig.update_layout(template="plotly_dark", height=280, coloraxis_colorbar_title="CAGR %")
    fig.update_traces(textfont_size=13)
    st.plotly_chart(fig, use_container_width=True)

    # Sharpe heatmap
    st.markdown("**Sharpe Ratio by Regime**")
    pivot_sharpe = regime_df.pivot(index="Strategy", columns="Regime", values="Sharpe")
    pivot_sharpe = pivot_sharpe[[c for c in regime_order if c in pivot_sharpe.columns]]
    fig2 = px.imshow(
        pivot_sharpe,
        color_continuous_scale="RdYlGn",
        color_continuous_midpoint=0,
        text_auto=".2f",
        aspect="auto",
    )
    fig2.update_layout(template="plotly_dark", height=280, coloraxis_colorbar_title="Sharpe")
    fig2.update_traces(textfont_size=13)
    st.plotly_chart(fig2, use_container_width=True)

    # Full summary table
    st.markdown("**Full Metrics Table**")
    table = summary_table(strategies)
    st.dataframe(table, use_container_width=True)

# ── Tab 5: Correlations ───────────────────────────────────────────────────────
with tab5:
    st.markdown("### 🔗 Are Diversified Holdings Actually Uncorrelated?")
    all_tickers = list(MAG7.keys()) + list(DIVERSIFIED.keys())
    corr = returns[all_tickers].corr()

    labels = [f"{t} ★" for t in MAG7.keys()] + list(DIVERSIFIED.keys())
    corr_display = corr.copy()
    corr_display.index = labels
    corr_display.columns = labels

    fig = px.imshow(
        corr_display,
        color_continuous_scale="RdBu_r",
        color_continuous_midpoint=0,
        text_auto=".2f",
        aspect="auto",
        title="★ = Mag7 stocks | Correlation matrix (daily returns, 2019–2025)",
        zmin=-1, zmax=1,
    )
    fig.update_layout(template="plotly_dark", height=600)
    fig.update_traces(textfont_size=8)
    st.plotly_chart(fig, use_container_width=True)

    # Average intra-group correlations
    mag7_tickers = list(MAG7.keys())
    div_tickers = list(DIVERSIFIED.keys())

    mag7_corr = returns[mag7_tickers].corr()
    div_corr = returns[div_tickers].corr()

    mag7_avg = mag7_corr.where(~np.eye(len(mag7_tickers), dtype=bool)).stack().mean()
    div_avg  = div_corr.where(~np.eye(len(div_tickers), dtype=bool)).stack().mean()

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Avg intra-Mag7 correlation", f"{mag7_avg:.3f}",
                  help="Higher = stocks move together = less diversification benefit")
    with c2:
        st.metric("Avg intra-Diversified correlation", f"{div_avg:.3f}",
                  help="Lower = holdings move independently = more diversification benefit")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<hr style='border:1px solid #333; margin-top:32px'>", unsafe_allow_html=True)
st.markdown("""
<p style='text-align:center; color:#666; font-size:0.8rem'>
    Data sourced from Yahoo Finance via yfinance · Not financial advice · Built for research & education
</p>
""", unsafe_allow_html=True)
