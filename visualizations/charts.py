import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from analysis.metrics import rolling_sharpe, max_drawdown, cumulative_returns, summary_table

EXPORT_DIR = Path(__file__).parent.parent / "exports"
EXPORT_DIR.mkdir(exist_ok=True)

COLORS = {
    "Magnificent 7 (Concentrated)": "#FF6B35",
    "Diversified (11 Sectors)":     "#2196F3",
    "S&P 500 (SPY Benchmark)":      "#9E9E9E",
}

STYLE = {
    "figure.facecolor": "#0F1117",
    "axes.facecolor":   "#0F1117",
    "axes.edgecolor":   "#333333",
    "axes.labelcolor":  "#CCCCCC",
    "xtick.color":      "#CCCCCC",
    "ytick.color":      "#CCCCCC",
    "text.color":       "#FFFFFF",
    "grid.color":       "#222222",
    "grid.linestyle":   "--",
    "grid.alpha":       0.6,
}


def apply_style():
    plt.rcParams.update(STYLE)
    plt.rcParams["font.family"] = "DejaVu Sans"


def chart1_growth(cum_returns: dict, save: bool = True) -> plt.Figure:
    apply_style()
    fig, ax = plt.subplots(figsize=(12, 6))
    for name, series in cum_returns.items():
        ax.plot(series.index, series.values, color=COLORS[name], linewidth=2.2, label=name)
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"{x:.1f}x"))
    ax.set_title("$1 Invested in 2019 → Today", fontsize=16, fontweight="bold", pad=15)
    ax.set_xlabel("")
    ax.set_ylabel("Portfolio Growth", fontsize=11)
    ax.legend(framealpha=0.15, fontsize=10)
    ax.grid(True)
    _shade_regimes(ax)
    fig.tight_layout()
    if save:
        fig.savefig(EXPORT_DIR / "01_growth.png", dpi=150, bbox_inches="tight")
    return fig


def chart2_drawdown(strategies: dict, save: bool = True) -> plt.Figure:
    apply_style()
    fig, ax = plt.subplots(figsize=(12, 5))
    for name, ret in strategies.items():
        cum = cumulative_returns(ret)
        roll_max = cum.cummax()
        dd = (cum - roll_max) / roll_max * 100
        ax.fill_between(dd.index, dd.values, 0, alpha=0.35, color=COLORS[name])
        ax.plot(dd.index, dd.values, color=COLORS[name], linewidth=1.5, label=name)
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax.set_title("Drawdown Over Time — Who Falls Hardest?", fontsize=16, fontweight="bold", pad=15)
    ax.set_ylabel("Drawdown (%)")
    ax.legend(framealpha=0.15, fontsize=10)
    ax.grid(True)
    fig.tight_layout()
    if save:
        fig.savefig(EXPORT_DIR / "02_drawdown.png", dpi=150, bbox_inches="tight")
    return fig


def chart3_rolling_sharpe(strategies: dict, save: bool = True) -> plt.Figure:
    apply_style()
    fig, ax = plt.subplots(figsize=(12, 5))
    for name, ret in strategies.items():
        rs = rolling_sharpe(ret, window=126)
        ax.plot(rs.index, rs.values, color=COLORS[name], linewidth=2, label=name)
    ax.axhline(0, color="#555555", linewidth=1, linestyle="--")
    ax.axhline(1, color="#444444", linewidth=0.8, linestyle=":")
    ax.set_title("6-Month Rolling Sharpe Ratio — Risk-Adjusted Performance", fontsize=16, fontweight="bold", pad=15)
    ax.set_ylabel("Sharpe Ratio (6-month rolling)")
    ax.legend(framealpha=0.15, fontsize=10)
    ax.grid(True)
    fig.tight_layout()
    if save:
        fig.savefig(EXPORT_DIR / "03_rolling_sharpe.png", dpi=150, bbox_inches="tight")
    return fig


def chart4_regime_heatmap(regime_df: pd.DataFrame, save: bool = True) -> plt.Figure:
    apply_style()
    pivot = regime_df.pivot(index="Strategy", columns="Regime", values="CAGR") * 100
    col_order = [
        "Pre-COVID Bull (2019)",
        "COVID Crash (2020)",
        "COVID Recovery (2020-2021)",
        "Rate Hike Bear (2022)",
        "AI Boom (2023-2024)",
        "2025 YTD",
    ]
    col_order = [c for c in col_order if c in pivot.columns]
    pivot = pivot[col_order]

    fig, ax = plt.subplots(figsize=(13, 4))
    sns.heatmap(
        pivot,
        annot=True,
        fmt=".1f",
        cmap="RdYlGn",
        center=0,
        ax=ax,
        linewidths=0.5,
        annot_kws={"size": 11, "weight": "bold"},
        cbar_kws={"label": "CAGR (%)"},
    )
    ax.set_title("CAGR (%) by Market Regime — Where Each Strategy Wins & Loses", fontsize=15, fontweight="bold", pad=15)
    ax.set_xlabel("")
    ax.set_ylabel("")
    plt.xticks(rotation=30, ha="right", fontsize=9)
    plt.yticks(rotation=0, fontsize=9)
    fig.tight_layout()
    if save:
        fig.savefig(EXPORT_DIR / "04_regime_heatmap.png", dpi=150, bbox_inches="tight")
    return fig


def chart5_metrics_bar(strategies: dict, save: bool = True) -> plt.Figure:
    from analysis.metrics import sharpe_ratio, cagr, annualized_volatility
    apply_style()

    names = list(strategies.keys())
    cagrs = [cagr(strategies[n]) * 100 for n in names]
    vols  = [annualized_volatility(strategies[n]) * 100 for n in names]
    sharpes = [sharpe_ratio(strategies[n]) for n in names]

    x = np.arange(len(names))
    width = 0.28

    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    fig.suptitle("Full Period Summary: Return, Risk & Risk-Adjusted Return", fontsize=14, fontweight="bold", y=1.02)

    for ax, vals, title, fmt in zip(
        axes,
        [cagrs, vols, sharpes],
        ["CAGR (%)", "Annualized Volatility (%)", "Sharpe Ratio"],
        ["{:.1f}%", "{:.1f}%", "{:.2f}"],
    ):
        bars = ax.bar(x, vals, color=[COLORS[n] for n in names], width=0.55, edgecolor="#333")
        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels([n.split(" (")[0] for n in names], fontsize=9)
        ax.grid(axis="y", alpha=0.4)
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                    fmt.format(val), ha="center", va="bottom", fontsize=10, fontweight="bold")

    fig.tight_layout()
    if save:
        fig.savefig(EXPORT_DIR / "05_metrics_bar.png", dpi=150, bbox_inches="tight")
    return fig


def chart6_correlation(returns: pd.DataFrame, save: bool = True) -> plt.Figure:
    from data.fetch import MAG7, DIVERSIFIED
    apply_style()

    all_tickers = list(MAG7.keys()) + list(DIVERSIFIED.keys())
    corr = returns[all_tickers].corr()

    labels = (
        [f"{t} ★" for t in MAG7.keys()] +
        [t for t in DIVERSIFIED.keys()]
    )

    fig, ax = plt.subplots(figsize=(13, 10))
    mask = np.zeros_like(corr, dtype=bool)
    mask[np.triu_indices_from(mask, k=1)] = True

    sns.heatmap(
        corr,
        mask=mask,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        ax=ax,
        linewidths=0.3,
        annot_kws={"size": 7},
        xticklabels=labels,
        yticklabels=labels,
    )
    ax.set_title("Correlation Matrix — ★ Mag7  vs  Diversified Holdings", fontsize=14, fontweight="bold", pad=15)
    plt.xticks(rotation=45, ha="right", fontsize=8)
    plt.yticks(rotation=0, fontsize=8)
    fig.tight_layout()
    if save:
        fig.savefig(EXPORT_DIR / "06_correlation.png", dpi=150, bbox_inches="tight")
    return fig


def _shade_regimes(ax):
    regimes = [
        ("2020-02-19", "2020-03-23", "#FF4444", "COVID\nCrash"),
        ("2022-01-01", "2022-12-31", "#FF8C00", "Rate\nHikes"),
        ("2023-01-01", "2024-12-31", "#44BB44", "AI Boom"),
    ]
    ylim = ax.get_ylim()
    for start, end, color, label in regimes:
        ax.axvspan(pd.Timestamp(start), pd.Timestamp(end), alpha=0.08, color=color)
        mid = pd.Timestamp(start) + (pd.Timestamp(end) - pd.Timestamp(start)) / 2
        ax.text(mid, ylim[1] * 0.97, label, ha="center", va="top",
                fontsize=7, color=color, alpha=0.7)


def export_all_charts(strategies, cum_returns, regime_df, prices, returns):
    print("Generating charts...")
    chart1_growth(cum_returns)
    chart2_drawdown(strategies)
    chart3_rolling_sharpe(strategies)
    chart4_regime_heatmap(regime_df)
    chart5_metrics_bar(strategies)
    chart6_correlation(returns)
    print(f"All charts saved to: {EXPORT_DIR}")
