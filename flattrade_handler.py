import os
from pya3 import Aliceblue

def handle_flattrade_order(data):
    user_id = os.getenv("FLATTRADE_USER_ID")
    api_key = os.getenv("FLATTRADE_API_KEY")
    # For now, simplistic login. In prod, use session caching.
    alice = Aliceblue(user_id=user_id, api_key=api_key)
    print(f"Flattrade Login: {alice.get_session_id()}")
    
    # CIPLA Token (Hardcoded for checking, better to fetch)
    # NSE Equity CIPLA
    symbol = data.get('symbol', 'CIPLA')
    side = data.get('action', 'BUY').upper()
    
    # Place Order
    print(f"Placing Flattrade Order: {symbol} {side}")
    # ... (Actual placement logic) ...
    return {"status": "success", "broker": "flattrade"}
