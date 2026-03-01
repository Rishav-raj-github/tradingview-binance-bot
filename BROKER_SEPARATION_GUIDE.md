# Broker Separation Implementation Guide

## ✅ COMPLETED: Firestore PnL Module Updates

The `src/firestore_pnl.py` file has been successfully updated to include the `broker` field in both orders and trades collections.

### Changes Made to firestore_pnl.py:

**1. Added broker field to `record_order()` function (Line 80):**
```python
order_doc = {
    'orderId': order_data.get('orderId'),
    'broker': order_data.get('broker', 'UNKNOWN'),  # ← NEW FIELD
    'symbol': order_data.get('symbol'),
    'side': order_data.get('side'),
    # ... rest of fields
}
```

**2. Added broker field to `record_trade()` function (Line 127):**
```python
trade_doc = {
    'tradeId': trade_data.get('tradeId'),
    'broker': trade_data.get('broker', 'UNKNOWN'),  # ← NEW FIELD
    'symbol': trade_data.get('symbol'),
    'entry_price': entry_price,
    # ... rest of fields
}
```

---

## ⏳ TODO: Update Handler Files

The following three handler files need to be updated to pass the `broker` field when calling the recording functions:

### 1. binance_handler.py

Find the calls to `record_order_to_firestore()` and `record_trade_to_firestore()` and add `'broker': 'BINANCE'` to the data dictionaries:

```python
# For orders:
order_data = {
    'orderId': order_id,
    'broker': 'BINANCE',  # ← ADD THIS
    'symbol': symbol,
    'side': side,
    'price': price,
    'quantity': quantity,
    'status': 'EXECUTED',
    'timestamp': datetime.now()
}
record_order_to_firestore(order_data)

# For trades:
trade_data = {
    'tradeId': trade_id,
    'broker': 'BINANCE',  # ← ADD THIS
    'symbol': symbol,
    'entry_price': entry_price,
    'exit_price': exit_price,
    'quantity': quantity,
    'status': 'CLOSED'
}
record_trade_to_firestore(trade_data)
```

### 2. binance_real_handler.py

Same as above, but use `'broker': 'BINANCE_REAL'` or `'broker': 'BINANCE_SPOT'`:

```python
order_data = {
    'orderId': order_id,
    'broker': 'BINANCE_REAL',  # ← ADD THIS
    # ... rest of fields
}
record_order_to_firestore(order_data)
```

### 3. flattrade_handler.py

For Kotak/Flattrade, use `'broker': 'KOTAK'`:

```python
order_data = {
    'orderId': order_id,
    'broker': 'KOTAK',  # ← ADD THIS
    'symbol': symbol,
    'side': side,
    'price': price,
    'quantity': quantity,
    'status': 'EXECUTED'
}
record_order_to_firestore(order_data)

trade_data = {
    'tradeId': trade_id,
    'broker': 'KOTAK',  # ← ADD THIS
    'symbol': symbol,
    'entry_price': entry_price,
    'exit_price': exit_price,
    'quantity': quantity
}
record_trade_to_firestore(trade_data)
```

---

## 📊 PnL Separation in Firestore

Once all handlers are updated, you'll be able to query PnL by broker:

```python
# Get all Binance trades
binance_trades = db.collection('trades').where('broker', '==', 'BINANCE').stream()

# Get all Kotak trades
kotak_trades = db.collection('trades').where('broker', '==', 'KOTAK').stream()

# Calculate PnL separately
binance_pnl = sum(trade.pnl for trade in binance_trades)
kotak_pnl = sum(trade.pnl for trade in kotak_trades)
```

---

## 🔄 Migration: Existing Records

For existing records that don't have the `broker` field, you have two options:

### Option 1: Leave as 'UNKNOWN'
Existing records will show `'broker': 'UNKNOWN'` by default. You can filter these out in queries:
```python
# Only get records with known brokers
trades = db.collection('trades').where('broker', '!=', 'UNKNOWN').stream()
```

### Option 2: Bulk Update Existing Records
If you want to backfill existing data, create a Cloud Function or local script:

```python
from firebase_admin import firestore

db = firestore.client()

# Example: Mark all BTCUSDT trades as BINANCE
trades = db.collection('trades').where('symbol', '==', 'BTCUSDT').stream()
for trade in trades:
    if trade.get('broker') is None or trade.get('broker') == 'UNKNOWN':
        db.collection('trades').document(trade.id).update({'broker': 'BINANCE'})
```

---

## ✓ Testing

After updating all handlers, verify the setup:

1. Create a test trade in Binance
2. Check Firestore: Should see `'broker': 'BINANCE'`
3. Create a test trade in Kotak
4. Check Firestore: Should see `'broker': 'KOTAK'`
5. Run query to separate PnL by broker

---

## Summary

✅ **Done:** `firestore_pnl.py` updated with broker field
⏳ **Todo:** Update 3 handler files (binance_handler.py, binance_real_handler.py, flattrade_handler.py)
⏳ **Todo:** Test the implementation
⏳ **Optional:** Migrate existing records
