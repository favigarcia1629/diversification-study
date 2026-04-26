import pandas as pd
from datetime import date
from data.fetch import fetch_prices, get_returns, MAG7, DIVERSIFIED, BENCHMARK
from analysis.metrics import portfolio_returns, cumulative_returns, period_returns

TODAY = date.today().isoformat()
CURRENT_YEAR = date.today().year

# Market regimes to analyze
REGIMES = {
    "Pre-COVID Bull (2019)":       ("2019-01-01", "2020-02-19"),
    "COVID Crash (2020)":          ("2020-02-19", "2020-03-23"),
    "COVID Recovery (2020-2021)":  ("2020-03-23", "2021-12-31"),
    "Rate Hike Bear (2022)":       ("2022-01-01", "2022-12-31"),
    "AI Boom (2023-2024)":         ("2023-01-01", "2024-12-31"),
    f"{CURRENT_YEAR} YTD":             (f"{CURRENT_YEAR}-01-01", TODAY),
    f"Full Period (2019-{CURRENT_YEAR})": ("2019-01-01", TODAY),
}


def run_backtest():
    prices = fetch_prices()
    returns = get_returns(prices)

    mag7_tickers = list(MAG7.keys())
    div_tickers = list(DIVERSIFIED.keys())

    strategies = {
        "Magnificent 7 (Concentrated)": portfolio_returns(returns, mag7_tickers),
        "Diversified (11 Sectors)":     portfolio_returns(returns, div_tickers),
        "S&P 500 (SPY Benchmark)":      returns[BENCHMARK],
    }

    # Cumulative growth (full period)
    cum_returns = {name: cumulative_returns(ret) for name, ret in strategies.items()}

    # Per-regime breakdown
    regime_results = []
    for regime, (start, end) in REGIMES.items():
        for name, ret in strategies.items():
            sliced = ret.loc[start:end]
            if len(sliced) > 5:
                row = period_returns(sliced, name)
                row["Regime"] = regime
                regime_results.append(row)

    regime_df = pd.DataFrame(regime_results)

    return strategies, cum_returns, regime_df, prices, returns
