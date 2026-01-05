"""Binance REAL (LIVE TRADING) Handler
USE THIS ONLY FOR LIVE/REAL TRADING with real money
Difference from binance_handler.py: Uses REAL API keys directly (testnet=False)
"""

from binance.client import Client
from binance.enums import *
import os
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_real_binance_order(data):
    """Handle real (live) Binance Futures orders - PRODUCTION MODE"""
    try:
        # REAL CREDENTIALS - DIRECTLY FROM ENV
        api_key = os.getenv("BINANCE_API_KEY")
        api_secret = os.getenv("BINANCE_API_SECRET")
        
        if not api_key or not api_secret:
            logger.error("Missing BINANCE API credentials for REAL trading")
            return {"status": "error", "message": "Missing API credentials for REAL trading"}
        
        # PRODUCTION MODE: testnet=False (REAL TRADING)
        logger.warning("⚠️ INITIALIZING REAL BINANCE TRADING - LIVE MONEY AT RISK")
        client = Client(api_key, api_secret, testnet=False)
        
        # Parse input data
        symbol = data.get('symbol', 'BTCUSDT').upper()
        side = data.get('side', data.get('action', 'BUY')).upper()
        qty = float(data.get('quantity', 0.001))
        order_type = data.get('type', 'MARKET').upper()
        price = data.get('price', None)
        
        logger.warning(f"🔴 REAL TRADE SIGNAL: {side} {qty} {symbol} @ {order_type}")
        
        # Validation: Check if symbol is valid
        if not symbol.endswith(('USDT', 'USDC', 'BUSD', 'BNB')):
            logger.warning(f"Symbol {symbol} may not exist. Adding USDT")
            symbol = symbol.replace('USDT', '') + 'USDT'
        
        # Validate quantity
        if qty <= 0:
            logger.error(f"Invalid quantity: {qty}")
            return {"status": "error", "message": f"Quantity must be > 0, got {qty}"}
        
        # Round quantity to proper precision (8 decimals for most pairs)
        qty = round(qty, 8)
        
        # Check minimum notional (usually 10 USDT for futures)
        try:
            exchange_info = client.futures_exchange_info()
            symbol_info = next((s for s in exchange_info['symbols'] if s['symbol'] == symbol), None)
            
            if symbol_info:
                # Get current price to calculate notional
                ticker = client.futures_mark_price(symbol=symbol)
                current_price = float(ticker['markPrice'])
                notional = qty * current_price
                
                logger.warning(f"Current price: {current_price}, Notional value: {notional}")
                
                # Check minimum notional
                min_notional = 10  # Default 10 USDT
                if notional < min_notional:
                    logger.warning(f"Notional {notional} < {min_notional} USDT. Skipping order.")
                    return {"status": "error", "message": f"Order notional {notional} < minimum {min_notional} USDT"}
        except Exception as e:
            logger.warning(f"Could not validate notional: {str(e)}")
        
        # Build order parameters
        order_params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': qty
        }
        
        if order_type == 'LIMIT' and price:
            order_params['price'] = float(price)
            order_params['timeInForce'] = 'GTC'
        
        logger.warning(f"🔴 REAL ORDER PARAMS: {json.dumps(order_params)}")
        
        # Place order
        try:
            order = client.futures_create_order(**order_params)
            logger.warning(f"✅ REAL ORDER PLACED SUCCESSFULLY: {order.get('orderId')}")
            return {
                "status": "success",
                "message": f"REAL ORDER {order.get('orderId')} placed",
                "order": order,
                "mode": "REAL_TRADING"
            }
        except Exception as e:
            error_msg = str(e)
            logger.error(f"REAL ORDER FAILED: {error_msg}")
            
            # Common errors
            if "MIN_NOTIONAL" in error_msg:
                return {"status": "error", "message": "Order size too small (MIN_NOTIONAL)"}
            elif "INVALID_QUANTITY" in error_msg or "LOT_SIZE" in error_msg:
                return {"status": "error", "message": "Invalid quantity for this pair"}
            elif "Account has insufficient balance" in error_msg:
                return {"status": "error", "message": "Insufficient balance"}
            elif "Margin is insufficient" in error_msg:
                return {"status": "error", "message": "Insufficient margin"}
            else:
                return {"status": "error", "message": error_msg}
    
    except Exception as e:
        logger.exception(f"REAL TRADING ERROR: {str(e)}")
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}
