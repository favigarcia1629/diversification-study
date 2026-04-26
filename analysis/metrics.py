import numpy as np
import pandas as pd

TRADING_DAYS = 252


def portfolio_returns(returns: pd.DataFrame, tickers: list[str]) -> pd.Series:
    """Equal-weight portfolio daily returns."""
    subset = returns[tickers].dropna()
    return subset.mean(axis=1)


def cumulative_returns(ret: pd.Series) -> pd.Series:
    return (1 + ret).cumprod()


def cagr(ret: pd.Series) -> float:
    cum = cumulative_returns(ret)
    n_years = len(ret) / TRADING_DAYS
    return cum.iloc[-1] ** (1 / n_years) - 1


def annualized_volatility(ret: pd.Series) -> float:
    return ret.std() * np.sqrt(TRADING_DAYS)


def sharpe_ratio(ret: pd.Series, risk_free: float = 0.04) -> float:
    excess = ret - risk_free / TRADING_DAYS
    return (excess.mean() / ret.std()) * np.sqrt(TRADING_DAYS)


def sortino_ratio(ret: pd.Series, risk_free: float = 0.04) -> float:
    excess = ret - risk_free / TRADING_DAYS
    downside = ret[ret < 0].std() * np.sqrt(TRADING_DAYS)
    return (excess.mean() * TRADING_DAYS) / downside if downside != 0 else np.nan


def max_drawdown(ret: pd.Series) -> float:
    cum = cumulative_returns(ret)
    rolling_max = cum.cummax()
    drawdown = (cum - rolling_max) / rolling_max
    return drawdown.min()


def calmar_ratio(ret: pd.Series) -> float:
    md = abs(max_drawdown(ret))
    return cagr(ret) / md if md != 0 else np.nan


def rolling_sharpe(ret: pd.Series, window: int = 126, risk_free: float = 0.04) -> pd.Series:
    excess = ret - risk_free / TRADING_DAYS
    roll_mean = excess.rolling(window).mean()
    roll_std = ret.rolling(window).std()
    return (roll_mean / roll_std) * np.sqrt(TRADING_DAYS)


def summary_table(strategies: dict[str, pd.Series]) -> pd.DataFrame:
    rows = []
    for name, ret in strategies.items():
        rows.append({
            "Strategy": name,
            "CAGR": f"{cagr(ret):.1%}",
            "Volatility": f"{annualized_volatility(ret):.1%}",
            "Sharpe Ratio": f"{sharpe_ratio(ret):.2f}",
            "Sortino Ratio": f"{sortino_ratio(ret):.2f}",
            "Max Drawdown": f"{max_drawdown(ret):.1%}",
            "Calmar Ratio": f"{calmar_ratio(ret):.2f}",
        })
    return pd.DataFrame(rows).set_index("Strategy")


def period_returns(ret: pd.Series, label: str) -> dict:
    return {
        "Strategy": label,
        "CAGR": cagr(ret),
        "Sharpe": sharpe_ratio(ret),
        "Max DD": max_drawdown(ret),
    }
