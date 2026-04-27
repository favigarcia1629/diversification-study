# Diversification vs. Concentration — A Data-Driven Study

**Is spreading risk still a smart strategy when a handful of stocks dominate the market?**

This project compares two investment philosophies head-to-head from January 2019 to today, across every major market regime — COVID crash, rate hike bear market, AI boom, and 2025–2026 volatility.

🔗 **[Live Interactive Dashboard](https://favigarcia1629-diversification-study-app.streamlit.app)**

---

## The Question

Conventional wisdom says diversify. But the last several years have been dominated by the Magnificent 7 — a handful of mega-cap tech stocks that dramatically outperformed the broader market. So which strategy actually wins, and under what conditions?

---

## Portfolios Compared

| Portfolio | Holdings | Weighting |
|---|---|---|
| 🟠 Concentrated | NVDA, AAPL, MSFT, GOOGL, META, AMZN, TSLA | Equal-weight |
| 🔵 Diversified | 1 stock per sector × 11 sectors (XOM, JPM, JNJ, CAT, PG, NKE, AMT, LIN, NEE, VZ, ORCL) | Equal-weight |
| ⚫ Benchmark | SPY (S&P 500 ETF) | — |

---

## Key Findings (Jan 2019 – Apr 2026)

| Strategy | $1 Grew To | CAGR | Sharpe Ratio | Max Drawdown |
|---|---|---|---|---|
| Magnificent 7 | **$7.65** | 38.2% | 1.04 | -49.4% |
| Diversified | $2.24 | 13.7% | 0.57 | -31.3% |
| S&P 500 (SPY) | $2.41 | 15.0% | 0.59 | -33.7% |

**Concentration wins on raw returns — but the story changes depending on the market regime:**

- **2022 Rate Hike Bear:** Mag7 fell 45.7%. Diversified fell just 0.8%.
- **2026 YTD:** Mag7 down ~20%. Diversified down ~3%.
- **Max Drawdown:** Mag7 lost nearly half its value peak-to-trough — requiring a +96% gain just to break even.

> Diversification doesn't maximize returns — it maximizes survival. And in investing, surviving long enough to compound is the real edge.

---

## Dashboard Features

- **Growth chart** — $1 invested in 2019, with market regime overlays
- **Drawdown chart** — how far each strategy fell from its peak
- **Rolling Sharpe Ratio** — 6-month risk-adjusted performance over time
- **Regime heatmap** — CAGR and Sharpe broken down by market environment
- **Correlation matrix** — are diversified holdings actually uncorrelated?
- Adjustable risk-free rate, regime highlighting toggle

---

## Project Structure

```
diversification_study/
├── data/
│   └── fetch.py          # yfinance data fetching + caching
├── analysis/
│   ├── metrics.py        # CAGR, Sharpe, Sortino, drawdown, Calmar
│   └── backtest.py       # Portfolio construction + regime breakdown
├── visualizations/
│   └── charts.py         # Static chart exports (matplotlib/seaborn)
├── exports/              # LinkedIn-ready PNGs + PDF report (gitignored)
├── app.py                # Streamlit dashboard
├── main.py               # Headless run: backtest + export charts
└── generate_pdf.py       # Full PDF report generator
```

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.14 | Core language |
| yfinance | Free market data (Yahoo Finance) |
| pandas / numpy | Data manipulation + returns calculation |
| matplotlib / seaborn | Static chart exports |
| plotly | Interactive dashboard charts |
| Streamlit | Web dashboard + deployment |
| reportlab | PDF report generation |
| GitHub + Streamlit Cloud | Version control + free hosting |

---

## Run Locally

```bash
git clone https://github.com/favigarcia1629/diversification-study.git
cd diversification-study
pip install -r requirements.txt

# Export charts + print summary
python main.py

# Launch dashboard
streamlit run app.py

# Generate PDF report
python generate_pdf.py
```

---

## Methodology Notes

- All portfolios are **equal-weighted** and assume **daily rebalancing**
- Prices are **adjusted for dividends and stock splits** (`auto_adjust=True`)
- No transaction costs or taxes modeled — this is a theoretical backtest
- Risk-free rate defaults to **4.0%** (adjustable in the dashboard sidebar)
- Data updates dynamically each time the app loads — no hardcoded dates

---

*Data sourced from Yahoo Finance via yfinance. Not financial advice — built for research and education.*
