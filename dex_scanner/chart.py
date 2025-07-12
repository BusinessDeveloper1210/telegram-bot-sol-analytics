import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
from typing import List, Dict, Any


# Define 5 static datasets for holders in profit
STATIC_PROFIT_HOLDER_DATASETS = [
    [90, 60, 40, 20, 30, 50, 40, 30, 20, 10, 30, 50, 70, 90],
    [80, 70, 60, 50, 40, 30, 20, 10, 20, 30, 40, 60, 80, 100],
    [100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 0, 10, 20, 30],
    [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 90, 80, 70, 60],
    [50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 95, 90, 85],
    [25, 55, 60, 65, 0, 5, 8, 8, 90, 95, 100, 95, 90, 85],
    [56, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 95, 90, 85],
    [34, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 95, 90, 85],
    [5, 10, 62, 6, 0, 5, 8, 8, 9, 9, 10, 5, 90, 85],
    [50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 95, 90, 85],
]
global_static_chart_counter = {'idx': 0}

def create_candlestick_chart(title: str, file_path: str, candlestick_data: List[Dict[str, Any]]):
    """Create a candlestick chart and save it to file, with static holders in profit curve only."""
    if not candlestick_data:
        return

    # Cycle through static datasets for holders in profit
    idx = global_static_chart_counter['idx']
    holders_in_profit = STATIC_PROFIT_HOLDER_DATASETS[idx]
    global_static_chart_counter['idx'] = (idx + 1) % len(STATIC_PROFIT_HOLDER_DATASETS)

    plt.style.use('dark_background')
    dates_dt = [datetime.fromtimestamp(candle['timestamp']) for candle in candlestick_data]
    dates = mdates.date2num(dates_dt)
    opens = [float(candle['open']) for candle in candlestick_data]
    highs = [float(candle['high']) for candle in candlestick_data]
    lows = [float(candle['low']) for candle in candlestick_data]
    closes = [float(candle['close']) for candle in candlestick_data]
    volumes = [float(candle.get('volume', 0)) for candle in candlestick_data]

    # Create two vertically stacked subplots (top: price/profit, bottom: volume)
    fig, (ax_profit, ax_vol) = plt.subplots(2, 1, figsize=(16, 12), sharex=True, gridspec_kw={'height_ratios': [3, 1]})
    ax_price = ax_profit.twinx()
    
    # Candlesticks (top)
    if len(dates) > 1:
        width = 0.7 * (dates[1] - dates[0])
    else:
        width = 0.02
    for i, (date, open_price, high, low, close) in enumerate(zip(dates, opens, highs, lows, closes)):
        color = '#00FF00' if close >= open_price else '#FF3333'
        ax_price.plot([date, date], [low, high], color=color, linewidth=3, zorder=2)
        ax_price.bar(date, close - open_price, bottom=min(open_price, close), width=width, color=color, alpha=0.8, zorder=3)

    # Holders in profit line (static, cycles, top)
    n = min(len(dates), len(holders_in_profit))
    ax_profit.plot(dates[:n], [v/100 for v in holders_in_profit[:n]], color='#FDBB2F', linewidth=5, zorder=4)

    # Y-axis formatting (top)
    ax_profit.set_ylabel('% of Holders in Profit', color='#FDBB2F', fontsize=28, labelpad=30, fontweight=200)
    ax_profit.set_ylim(0, 1)
    ax_profit.tick_params(axis='y', colors='#FDBB2F', labelsize=22)
    ax_profit.set_yticks(np.linspace(0, 1, 6))
    ax_profit.set_yticklabels([f'{int(v*100)}%' for v in np.linspace(0, 1, 6)], fontsize=22, color='#FDBB2F', )

    ax_price.set_ylabel('Price $', color='white', fontsize=28, labelpad=30, fontweight='bold')
    ax_price.tick_params(axis='y', colors='white', labelsize=22)

    # X axis (bottom only)
    ax_vol.set_xlabel('Time', fontsize=28, color='white', labelpad=20)
    ax_vol.xaxis.set_major_formatter(mdates.DateFormatter('%b %d\n%H:%M'))
    plt.setp(ax_vol.xaxis.get_majorticklabels(), color='white', fontsize=22, fontweight='bold')
    ax_profit.grid(True, alpha=0.3, color='white')

    # Volume bars (bottom)
    for i, (date, volume) in enumerate(zip(dates, volumes)):
        color = '#00FF00' if closes[i] >= opens[i] else '#FF3333'
        ax_vol.bar(date, volume, width=width, color=color, alpha=0.25, zorder=0)
    # Remove left y-axis for volume, use only right
    ax_vol.yaxis.set_label_position('right')
    ax_vol.yaxis.tick_right()
    ax_vol.set_ylabel('Volume $', color='white', fontsize=22, labelpad=30, fontweight='bold')
    ax_vol.tick_params(axis='y', colors='white', labelsize=18)
    ax_vol.grid(False)

    # Remove legend from graph area
    # (No legend code here)

    # Title and subtitle
    fig.suptitle(title, color='white', fontsize=34, fontweight='bold', y=0.96)
    fig.text(0.5, 0.91, ' -- % of Holders in Profit $ Price', ha='center', va='top', color='white', fontsize=26)

    plt.tight_layout(rect=(0, 0.05, 1, 0.89))
    plt.savefig(file_path, dpi=300, bbox_inches='tight', facecolor='black', edgecolor='none')
    plt.close() 