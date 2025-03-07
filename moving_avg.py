import requests
import pandas as pd
import matplotlib.pyplot as plt


# Fetch historical Bitcoin price data from Binance
def get_btc_try_prices():
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": "BTCTRY",   # BTC to Turkish Lira pair
        "interval": "1d",     # Daily prices
        "limit": 30           # Last 30 days
    }

    response = requests.get(url, params=params)
    data = response.json()

    # Convert response to a DataFrame
    df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low",
                                     "close", "volume", "close_time",
                                     "quote_asset_volume", "trades",
                                     "taker_base_vol",
                                     "taker_quote_vol", "ignore"])

    # Keep only relevant columns
    df = df[["timestamp", "close"]]
    # Convert timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df["close"] = df["close"].astype(float)  # Convert close price to float
    df.set_index("timestamp", inplace=True)

    return df


# Compute moving average
def compute_moving_average(df, window=7):
    df["Moving_Avg"] = df["close"].rolling(window=window).mean()
    return df


# Plot BTC/TRY prices and moving average
def plot_prices(df):
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df["close"], label="BTC/TRY Price", marker="o")
    plt.plot(df.index, df["Moving_Avg"], label="Moving Average (7-day)",
             linestyle="dashed", color="red")

    plt.title("Bitcoin to Turkish Lira (BTC/TRY) - Last 30 Days")
    plt.xlabel("Date")
    plt.ylabel("Price (TRY)")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.show()


# Main execution
df = get_btc_try_prices()
df = compute_moving_average(df, window=7)  # 7-day moving average
plot_prices(df)
