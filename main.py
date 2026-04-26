"""
Run this to fetch data and export all charts to the /exports folder.
Usage: python main.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from analysis.backtest import run_backtest
from visualizations.charts import export_all_charts
from analysis.metrics import summary_table

if __name__ == "__main__":
    print("Running backtest...")
    strategies, cum_returns, regime_df, prices, returns = run_backtest()

    print("\n=== Full Period Summary ===")
    print(summary_table(strategies).to_string())

    print("\n=== Regime Breakdown ===")
    print(regime_df.to_string(index=False))

    export_all_charts(strategies, cum_returns, regime_df, prices, returns)
    print("\nDone. Open the exports/ folder for LinkedIn-ready charts.")
    print("To launch the dashboard: streamlit run app.py")
