import matplotlib.pyplot as plt
import pandas as pd

def plot_equity_curve(equity_curve: pd.DataFrame, title="Equity Curve"):
    plt.figure(figsize=(10, 6))
    plt.plot(equity_curve['timestamp'], equity_curve['equity'], label='Equity')
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Equity (USDT)')
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_drawdown(equity_curve: pd.DataFrame, title="Drawdown"):
    equity = equity_curve['equity']
    rolling_max = equity.cummax()
    drawdown = (equity - rolling_max) / rolling_max
    
    plt.figure(figsize=(10, 4))
    plt.fill_between(equity_curve['timestamp'], drawdown, 0, color='red', alpha=0.3)
    plt.plot(equity_curve['timestamp'], drawdown, color='red', alpha=0.6)
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Drawdown %')
    plt.grid(True)
    plt.show()
