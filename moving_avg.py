import requests
import pandas as pd
import matplotlib.pyplot as plt


# Fetch historical Bitcoin price data from Binance
def get_btc_try_prices():
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": "BTCTRY",  # BTC to Turkish Lira pair
        "interval": "1d",    # Daily prices
        "limit": 300       # Last 300 days to include long-term moving average
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


# Compute moving averages
def compute_moving_averages(df):
    df["MA_10"] = df["close"].rolling(window=10).mean()
    df["MA_20"] = df["close"].rolling(window=20).mean()
    df["MA_300"] = df["close"].rolling(window=300).mean()
    return df


# Plot BTC/TRY prices and moving averages
def plot_prices(df):
    plt.figure(figsize=(12, 6))
    plt.plot(
        df.index, df["close"], label="BTC/TRY Price", marker="o", alpha=0.6
    )
    plt.plot(df.index, df["MA_10"], label="10-day MA",
             linestyle="dashed", color="red")
    plt.plot(df.index, df["MA_20"], label="20-day MA",
             linestyle="dashed", color="green")
    plt.plot(df.index, df["MA_300"], label="300-day MA",
             linestyle="dashed", color="blue")

    plt.title("Bitcoin to Turkish Lira (BTC/TRY) - Last 300 Days")
    plt.xlabel("Date")
    plt.ylabel("Price (TRY)")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.show()


# Main execution
df = get_btc_try_prices()
df = compute_moving_averages(df)
plot_prices(df)
