import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
from typing import List, Dict, Any


def create_candlestick_chart(title: str, file_path: str, candlestick_data: List[Dict[str, Any]]) -> None:
    """Create a candlestick chart and save it to file."""
    if not candlestick_data:
        return
    
    # Set style for black background
    plt.style.use('dark_background')
    
    # Prepare data
    dates = [datetime.fromtimestamp(candle['timestamp']) for candle in candlestick_data]
    opens = [float(candle['open']) for candle in candlestick_data]
    highs = [float(candle['high']) for candle in candlestick_data]
    lows = [float(candle['low']) for candle in candlestick_data]
    closes = [float(candle['close']) for candle in candlestick_data]
    volumes = [float(candle.get('volume', 0)) for candle in candlestick_data]
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), 
                                   gridspec_kw={'height_ratios': [3, 1]})
    
    # Plot candlesticks
    for i, (date, open_price, high, low, close, volume) in enumerate(
        zip(dates, opens, highs, lows, closes, volumes)
    ):
        # Determine color based on price movement
        color = 'green' if close >= open_price else 'red'
        
        # Plot candlestick body
        ax1.bar(date, close - open_price, bottom=min(open_price, close),
                width=0.0005, color=color, alpha=0.8)
        
        # Plot wicks
        ax1.plot([date, date], [low, high], color=color, linewidth=1)
    
    # Plot volume bars
    for i, (date, volume) in enumerate(zip(dates, volumes)):
        # Color volume bars based on price movement
        color = 'green' if closes[i] >= opens[i] else 'red'
        ax2.bar(date, volume, width=0.0005, color=color, alpha=0.6)
    
    # Customize price chart
    ax1.set_title(title, color='white', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Price (USD)', color='white')
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(colors='white')
    
    # Customize volume chart
    ax2.set_ylabel('Volume', color='white')
    ax2.set_xlabel('Time', color='white')
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(colors='white')
    
    # Format x-axis
    for ax in [ax1, ax2]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(file_path, dpi=300, bbox_inches='tight', 
                facecolor='black', edgecolor='none')
    plt.close() 