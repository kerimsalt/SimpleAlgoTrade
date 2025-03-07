import time
import requests
import hmac
import hashlib
import base64
import json

# BtcTurk API Keys (replace with your actual keys)
API_KEY = "your_api_key"
API_SECRET = "your_api_secret"

# Base API URL
BASE_URL = "https://api.btcturk.com/api/v2"


# Function to generate authentication headers
def get_headers():
    timestamp = str(int(time.time() * 1000))
    message = API_KEY + timestamp
    signature = hmac.new(
        base64.b64decode(API_SECRET),
        message.encode("utf-8"),
        hashlib.sha256
    ).digest()
    signature_b64 = base64.b64encode(signature).decode("utf-8")

    return {
        "X-PCK": API_KEY,
        "X-Stamp": timestamp,
        "X-Signature": signature_b64,
        "Content-Type": "application/json"
    }


# Function to get account balance
def get_balance():
    url = f"{BASE_URL}/users/balances"
    response = requests.get(url, headers=get_headers())
    return response.json()


# Function to get order book (market prices)
def get_order_book(pair="BTC_TRY"):
    url = f"{BASE_URL}/orderbook?pairSymbol={pair}"
    response = requests.get(url)
    return response.json()


# Function to place a market order
def place_order(order_type, price, amount, pair="BTC_TRY"):
    """
    Sends a POST request with trade details.
    Uses authentication (get_headers()) to ensure the request is authorized.

    Args:
        order_type (_type_): 0 for Buy, 1 for Sell
        price (_type_): Price to buy/sell at (use None for market orders).
        amount (_type_): Quantity of the asset to trade.
        pair (str, optional): Trading pair
        (default: "BTC_TRY" for Bitcoin/Turkish Lira). Defaults to "BTC_TRY".

    Returns:
        _type_: _description_
    """
    url = f"{BASE_URL}/order"
    data = {
        "price": price,  # Set price for limit orders
        "quantity": amount,
        "orderMethod": "market",
        "orderType": order_type,  # 0 for buy, 1 for sell
        "pairSymbol": pair
    }

    response = requests.post(url, headers=get_headers(), json=data)
    return response.json()


# Example Usage
if __name__ == "__main__":
    # Get balance
    balance = get_balance()
    print(json.dumps(balance, indent=4))

    # Get order book
    order_book = get_order_book()
    print(json.dumps(order_book, indent=4))

    # Place a market order (buy 0.001 BTC)
    # Adjust price accordingly

    # order_response = place_order(order_type=0, price=500000, amount=0.001)
    # print(json.dumps(order_response, indent=4))
