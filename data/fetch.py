import yfinance as yf
import pandas as pd
from pathlib import Path

# --- Portfolio Definitions ---
MAG7 = {
    "NVDA": "NVIDIA",
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Alphabet",
    "META": "Meta",
    "AMZN": "Amazon",
    "TSLA": "Tesla",
}

DIVERSIFIED = {
    "XOM":  "Energy",
    "JPM":  "Financials",
    "JNJ":  "Healthcare",
    "CAT":  "Industrials",
    "PG":   "Consumer Staples",
    "NKE":  "Consumer Discretionary",
    "AMT":  "Real Estate",
    "LIN":  "Materials",
    "NEE":  "Utilities",
    "VZ":   "Communication",
    "ORCL": "Technology (non-Mag7)",
}

BENCHMARK = "SPY"

START_DATE = "2019-01-01"
END_DATE   = "2025-04-25"

CACHE_PATH = Path(__file__).parent / "prices.parquet"


def fetch_prices(force_refresh: bool = False) -> pd.DataFrame:
    if CACHE_PATH.exists() and not force_refresh:
        return pd.read_parquet(CACHE_PATH)

    tickers = list(MAG7.keys()) + list(DIVERSIFIED.keys()) + [BENCHMARK]
    raw = yf.download(tickers, start=START_DATE, end=END_DATE, auto_adjust=True, progress=False)
    prices = raw["Close"].dropna(how="all")
    prices.to_parquet(CACHE_PATH)
    return prices


def get_returns(prices: pd.DataFrame) -> pd.DataFrame:
    return prices.pct_change().dropna()
