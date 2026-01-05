# 🔗 CONNECTION FLOW: TradingView → Railway → Binance

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         YOUR SYSTEM                             │
└─────────────────────────────────────────────────────────────────┘


    STEP 1: ALERT TRIGGER (TradingView)
    ────────────────────────────────────
    
    TradingView
    ├─ BTCUSDT Chart (1h timeframe)
    ├─ Condition: Close > Open OR custom indicator
    ├─ Create Alert
    └─ Send to Webhook: https://your-app.railway.app/webhook
           │
           │ JSON Payload:
           │ {
           │   "broker": "BINANCE",
           │   "symbol": "BTCUSDT",
           │   "side": "buy",
           │   "quantity": 0.001,
           │   "type": "MARKET"
           │ }
           │
           ↓

    STEP 2: WEBHOOK RECEIVER (Railway)
    ──────────────────────────────────
    
    Railway.com (Python Flask Server)
    ├─ Endpoint: POST /webhook
    ├─ Receives JSON from TradingView
    ├─ Validates JSON format
    ├─ Routes to correct broker handler:
    │  ├─ broker="BINANCE" → binance_handler.py (testnet)
    │  ├─ broker="BINANCE_REAL" → binance_real_handler.py (live)
    │  └─ broker="FLATTRADE" → flattrade_handler.py (stocks)
    │
    └─ Logs: "Processing Binance Signal: BUY BTCUSDT..."
           │
           ↓

    STEP 3: ORDER VALIDATION (Python Bot)
    ───────────────────────────────────
    
    binance_handler.py (or binance_real_handler.py)
    ├─ Extract parameters:
    │  ├─ symbol = "BTCUSDT"
    │  ├─ side = "BUY"
    │  ├─ quantity = 0.001
    │  └─ type = "MARKET"
    │
    ├─ VALIDATION CHECKS:
    │  ├─ ✅ Check MIN_NOTIONAL (10 USDT minimum)
    │  │   └─ quantity * price >= 10 ?
    │  │
    │  ├─ ✅ Round quantity to 8 decimals
    │  │   └─ 0.001 → 0.001
    │  │
    │  ├─ ✅ Verify symbol exists
    │  │   └─ Must end with USDT/USDC/BUSD
    │  │
    │  ├─ ✅ Check API keys are set
    │  │   └─ From Railway environment variables
    │  │
    │  └─ ✅ Verify balance (if configured)
    │
    ├─ Logs: "Current price: $43,500, Notional: $43.5"
    ├─ Logs: "Order params: {...}"
    │
    └─ All checks pass? YES → Continue to Step 4
               │
               ↓

    STEP 4: PLACE ORDER ON BINANCE
    ──────────────────────────────
    
    Binance API (CCXT Library)
    ├─ Environment: BINANCE_TESTNET=true (or false)
    │  ├─ true → Testnet (demo trades, no real money)
    │  └─ false → Live (REAL MONEY)
    │
    ├─ API Keys (from Railway Variables):
    │  ├─ BINANCE_API_KEY=your_key
    │  └─ BINANCE_API_SECRET=your_secret
    │
    ├─ Create order:
    │  └─ client.futures_create_order(
    │      symbol="BTCUSDT",
    │      side="BUY",
    │      type="MARKET",
    │      quantity=0.001
    │    )
    │
    ├─ Binance response:
    │  ├─ orderId: 123456789
    │  ├─ status: "FILLED"
    │  └─ executedQty: 0.001
    │
    ├─ Logs: "✅ Order placed successfully: 123456789"
    │
    └─ Return response to Railway
           │
           ↓

    STEP 5: LOG & CONFIRM
    ─────────────────────
    
    Railway Logs (visible in Dashboard)
    ├─ "Processing Binance Signal: BUY BTCUSDT 0.001 @ MARKET"
    ├─ "Current price: $43,500"
    ├─ "✅ Order placed successfully: 123456789"
    └─ "Status: FILLED, Executed: 0.001 BTC"
    
    TradingView (no response expected, fire-and-forget)
    └─ Alert triggered, message sent ✓
    
    Binance Account (Your Orders)
    ├─ Go to testnet.binance.vision (or binance.com)
    ├─ Navigate to Open Orders / Order History
    ├─ Find: BTCUSDT BUY 0.001 @ MARKET
    └─ Status: FILLED ✓
           │
           ↓

    STEP 6: REPEAT
    ──────────────
    
    Next alert from TradingView automatically triggers same flow
```

---

## Data Flow Timeline

```
Time    Event                              Component
────    ─────                              ─────────
T+0s    Chart condition triggered          TradingView
T+1s    POST /webhook sent                 TradingView → Railway
T+2s    Webhook received, validated        Railway Flask
T+3s    Handler selected (binance)         binance_handler.py
T+4s    Parameters extracted               Python
T+5s    MIN_NOTIONAL checked               Python
T+6s    API call sent to Binance           CCXT Library
T+7s    Order created on Binance           Binance API
T+8s    Response received                  Railway
T+9s    Order confirmed in logs            Railway Logs
T+10s   Order visible in Binance UI        Binance Account
```

---

## Environment Variables (Railway)

```yaml
# Binance Testnet (DEMO)
BINANCE_API_KEY: your_testnet_api_key
BINANCE_API_SECRET: your_testnet_api_secret
BINANCE_TESTNET: true

# OR Binance Live (REAL MONEY)
BINANCE_API_KEY: your_real_api_key
BINANCE_API_SECRET: your_real_api_secret
BINANCE_TESTNET: false

# Server
PORT: 8080
```

---

## Order Message Format (JSON)

### Buy Market Order
```json
{
  "broker": "BINANCE",
  "symbol": "BTCUSDT",
  "side": "buy",
  "quantity": 0.001,
  "type": "MARKET"
}
```

### Sell Limit Order
```json
{
  "broker": "BINANCE",
  "symbol": "ETHUSDT",
  "side": "sell",
  "quantity": 0.1,
  "type": "LIMIT",
  "price": 2500
}
```

### Binance Real (Live Money)
```json
{
  "broker": "BINANCE_REAL",
  "symbol": "BTCUSDT",
  "side": "buy",
  "quantity": 0.001,
  "type": "MARKET"
}
```

### FlatTrade (Stocks)
```json
{
  "broker": "FLATTRADE",
  "symbol": "CIPLA",
  "side": "buy",
  "quantity": 10,
  "type": "MARKET"
}
```

---

## Error Handling Flow

```
┌─ MIN_NOTIONAL Error
│  └─ Quantity * Price < 10 USDT
│     └─ Response: {"error": "Order size too small"}
│        └─ No order placed
│
├─ INVALID_QUANTITY Error
│  └─ Quantity has > 8 decimals
│     └─ Response: {"error": "Invalid quantity precision"}
│        └─ No order placed
│
├─ INSUFFICIENT_BALANCE Error
│  └─ Account doesn't have enough USDT
│     └─ Response: {"error": "Insufficient balance"}
│        └─ No order placed
│
├─ INVALID_SYMBOL Error
│  └─ Symbol doesn't exist (e.g., BTC instead of BTCUSDT)
│     └─ Response: {"error": "Invalid symbol"}
│        └─ No order placed
│
└─ SUCCESS
   └─ All validations pass
      └─ Order placed on Binance
         └─ Response: {"success": true, "orderId": 123456789}
            └─ Order appears in account
```

---

## Monitoring the Flow

### 1. Watch TradingView Alert
- Chart closes above/below support
- Alert automatically triggers
- Webhook message sent (you won't see this)

### 2. Check Railway Logs (MOST IMPORTANT)
```bash
Railway Dashboard
→ Deployments
→ Latest Deployment
→ Logs tab

Watch for:
✅ "Processing Binance Signal: BUY BTCUSDT 0.001 @ MARKET"
✅ "Current price: $43,500"
✅ "✅ Order placed successfully: 123456789"
❌ "ERROR: ..." (if something goes wrong)
```

### 3. Verify in Binance
```bash
Testnet: https://testnet.binance.vision
Live: https://binance.com

→ Futures Trading (or Spot)
→ Open Orders OR Order History
→ Find your BTCUSDT order
→ Status: FILLED or PARTIALLY_FILLED
```

---

## Quick Troubleshooting

| Issue | Check | Fix |
|-------|-------|-----|
| No log entry | TradingView alert fired? | Check TradingView alert log |
| "Min notional" error | Order size | Increase quantity to 10+ USDT value |
| "Invalid quantity" | Decimal places | Use 0.001, not 0.001000001 |
| "Unauthorized API key" | API keys correct? | Verify in Railway Variables |
| Order not in Binance | Wait 5-10 seconds | Order takes time to appear |
| Webhook 500 error | Flask crashed? | Check Railway logs for Python error |
| Wrong testnet/live | BINANCE_TESTNET value | Set to true for demo, false for live |

---

## Security Notes

✅ **NEVER**:
- Share your API keys
- Commit `.env` file to Git
- Log sensitive data
- Use API keys in URLs

✅ **ALWAYS**:
- Set IP whitelist on Binance API
- Use testnet first before live
- Start with small quantities
- Monitor first 10 orders closely
- Keep API key secret in Railway Variables

---

## Success Indicators

✅ All systems working when:
1. TradingView alert fires at correct time
2. Railway logs show "Order placed successfully"
3. Order appears in Binance Order History within 10 seconds
4. Order status is FILLED or PARTIALLY_FILLED
5. Your account balance updates correctly

🎉 **System is ready for auto-trading!**
