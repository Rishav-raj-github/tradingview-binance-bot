from binance.client import Client
from binance.enums import *
import os

def handle_binance_order(data):
    # Credentials
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    # PRODUCTION MODE: testnet=False (Default)
    client = Client(api_key, api_secret) 
    
    symbol = data.get('symbol', 'BTCUSDT').upper()
    side = data.get('action', 'BUY').upper()
    qty = float(data.get('quantity', 0.001))
    
    print(f"Processing Binance Signal: {side} {symbol} {qty}")
    
    # 1. Check Current Position (Futures)
    # Note: Using futures_position_information for accurate net view
    positions = client.futures_position_information(symbol=symbol)
    # usually returns a list, find the one with matching symbol
    target_pos = next((p for p in positions if p['symbol'] == symbol), None)
    
    current_amt = float(target_pos['positionAmt']) if target_pos else 0.0
    print(f"Current Position: {current_amt}")
    
    # 2. Square Off Logic
    if side == "BUY":
        # If we are SHORT (negative amt), we must BUY to close.
        if current_amt < 0:
            close_qty = abs(current_amt)
            print(f"Closing existing SHORT of {close_qty}...")
            client.futures_create_order(symbol=symbol, side=SIDE_BUY, type=ORDER_TYPE_MARKET, quantity=close_qty)
            
    elif side == "SELL":
        # If we are LONG (positive amt), we must SELL to close.
        if current_amt > 0:
            close_qty = abs(current_amt)
            print(f"Closing existing LONG of {close_qty}...")
            client.futures_create_order(symbol=symbol, side=SIDE_SELL, type=ORDER_TYPE_MARKET, quantity=close_qty)

    # 3. Place New Order (Target Quantity)
    print(f"Placing New {side} Order for {qty}...")
    order = client.futures_create_order(symbol=symbol, side=side, type=ORDER_TYPE_MARKET, quantity=qty)
    
    return order
