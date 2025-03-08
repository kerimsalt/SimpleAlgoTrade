import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# Fetch BTC/TRY prices from Binance
def get_btc_try_prices():
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": "BTCTRY", "interval": "1d", "limit": 300}

    response = requests.get(url, params=params)
    data = response.json()

    df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low",
                                     "close", "volume", "close_time",
                                     "quote_asset_volume", "trades",
                                     "taker_base_vol",
                                     "taker_quote_vol", "ignore"])

    df = df[["timestamp", "open", "high", "low", "close", "volume"]]
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df = df.astype(float)
    df.set_index("timestamp", inplace=True)

    return df


# Compute moving averages, RSI, and volume confirmation
def compute_indicators(df):
    df["MA_10"] = df["close"].rolling(window=10).mean()
    df["MA_20"] = df["close"].rolling(window=20).mean()
    df["MA_300"] = df["close"].rolling(window=300).mean()

    # RSI Calculation
    delta = df["close"].diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # Volume Confirmation: Use 20-day average volume
    df["Volume_MA"] = df["volume"].rolling(window=20).mean()

    # Buy/Sell Signals with Volume Confirmation
    df["Signal"] = np.where(
        (df["MA_10"] > df["MA_20"]) &
        (df["MA_10"].shift(1) <= df["MA_20"].shift(1)) &
        (df["RSI"] < 70) & (df["volume"] > df["Volume_MA"]), 1, 0
    )
    df["Signal"] = np.where(
        (df["MA_10"] < df["MA_20"]) &
        (df["MA_10"].shift(1) >= df["MA_20"].shift(1)) &
        (df["RSI"] > 30) & (df["volume"] > df["Volume_MA"]), 0, df["Signal"]
    )

    return df


# Backtest Strategy
def backtest(df, stop_loss=0.05, take_profit=0.1):
    capital = 10000  # Starting capital in TRY
    position = 0
    entry_price = 0

    df["Trade"] = np.nan  # 1 for buy, -1 for sell, NaN otherwise
    df["PnL"] = 0  # Track profit and loss

    for i in range(1, len(df)):
        if df["Signal"].iloc[i] == 1 and position == 0:  # Buy Signal
            position = capital / df["close"].iloc[i]
            entry_price = df["close"].iloc[i]
            capital = 0
            df.at[df.index[i], "Trade"] = 1  # Mark buy trade

        elif position > 0:
            current_price = df["close"].iloc[i]
            price_change = (current_price - entry_price) / entry_price
            # Take profit or stop loss
            if price_change >= take_profit or price_change <= -stop_loss:
                capital = position * current_price
                position = 0
                df.at[df.index[i], "Trade"] = -1  # Mark sell trade
                df.at[df.index[i], "PnL"] = capital - 10000  # Record PnL
    # Calculate total capital
    df["Capital"] = capital + (position * df["close"])
    return df


# Plot BTC/TRY prices, signals, and backtesting results
def plot_results(df):
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Plot BTC price and moving averages
    ax1.plot(df.index, df["close"], label="BTC/TRY Price", marker="o",
             alpha=0.6)
    ax1.plot(df.index, df["MA_10"], label="10-day MA", linestyle="dashed",
             color="red")
    ax1.plot(df.index, df["MA_20"], label="20-day MA", linestyle="dashed",
             color="green")
    ax1.plot(df.index, df["MA_300"], label="300-day MA", linestyle="dashed",
             color="blue")

    # Buy and Sell Signals
    buy_signals = df[df["Trade"] == 1]
    sell_signals = df[df["Trade"] == -1]

    ax1.scatter(buy_signals.index, buy_signals["close"], color="green",
                marker="^", label="Buy", s=100)
    ax1.scatter(sell_signals.index, sell_signals["close"], color="red",
                marker="v", label="Sell", s=100)

    ax1.set_title("BTC/TRY Trading Strategy with Volume & RSI")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Price (TRY)")
    ax1.legend()
    ax1.grid(True)
    plt.xticks(rotation=45)

    # Second subplot for RSI
    fig, ax2 = plt.subplots(figsize=(12, 3))
    ax2.plot(df.index, df["RSI"], label="RSI", color="purple")
    ax2.axhline(70, linestyle="dashed", color="red", label="Overbought (70)")
    ax2.axhline(30, linestyle="dashed", color="green", label="Oversold (30)")
    ax2.set_title("Relative Strength Index (RSI)")
    ax2.set_xlabel("Date")
    ax2.set_ylabel("RSI")
    ax2.legend()
    ax2.grid(True)
    plt.xticks(rotation=45)

    # Third subplot for Capital Growth
    fig, ax3 = plt.subplots(figsize=(12, 3))
    ax3.plot(df.index, df["Capital"], label="Capital Growth", color="blue")
    ax3.set_title("Trading Capital Over Time")
    ax3.set_xlabel("Date")
    ax3.set_ylabel("Capital (TRY)")
    ax3.legend()
    ax3.grid(True)
    plt.xticks(rotation=45)

    plt.show()

    return df


# Main execution
df = get_btc_try_prices()
df = compute_indicators(df)
df = backtest(df, stop_loss=0.05, take_profit=0.1)
df = plot_results(df)

# Display backtesting results
print(df[["close", "RSI", "Volume_MA", "Signal", "Trade", "PnL", "Capital"]])
