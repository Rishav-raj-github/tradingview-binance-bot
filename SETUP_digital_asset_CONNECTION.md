# 🚀 COMPLETE SETUP: Make Your First DigitalAsset Order

**Goal:** Connect MarketFeed → Railway → DigitalAsset and place your first live order

**Time to complete:** 15 minutes

---

## PART 1: GET DIGITAL_ASSET TESTNET API KEYS (5 minutes)

### Step 1.1: Go to DigitalAsset Testnet
```
URL: https://testnet.binance.vision
```

### Step 1.2: Create API Keys
1. Click "Generate HMAC SHA256 Key"
2. Copy the **API Key** (long string)
3. Copy the **Secret Key** (another long string)
4. **SAVE BOTH** - you need them now

### Step 1.3: Enable Spot Futures Testing (Optional)
- Go to "Testnet Spot"
- Verify you have test USDT balance
- If not, click "Faucet" to get test funds

✅ **DONE:** You have testnet API keys

---

## PART 2: SET UP RAILWAY.COM (5 minutes)

### Step 2.1: Create Railway Account
1. Go to https://railway.app
2. Sign up with GitHub (recommended)
3. Authorize the connection

### Step 2.2: Create New Project
1. Click "+ New Project"
2. Select "Deploy from GitHub repo"
3. Connect your GitHub account
4. Select: `Rishav-raj-github/market_feed-digital_asset-bot`
5. Click "Deploy"

### Step 2.3: Add Environment Variables
1. Go to **Deployments** tab
2. Click the latest deployment
3. Go to **Variables**
4. Add these variables:

```
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_secret_here
BINANCE_TESTNET=true
PORT=8080
```

5. Click "Save"
6. Railway will auto-redeploy

### Step 2.4: Get Your Railway Webhook URL
1. Go to **Settings**
2. Find **"Public URL"** or **"Domain"**
3. Copy the URL (should look like: `https://your-app-xxxx.railway.app`)
4. **YOUR WEBHOOK URL IS:** `https://your-app-xxxx.railway.app/webhook`

✅ **DONE:** Flask app is running on Railway

---

## PART 3: SET UP MARKET_FEED ALERT (3 minutes)

### Step 3.1: Create a Simple Chart Alert
1. Go to https://market_feed.com
2. Open any BTCUSDT chart (1-hour timeframe)
3. Create a simple strategy or use an existing indicator

### Step 3.2: Create Alert
1. Click "Alert" (bell icon)
2. Create new alert with these settings:

**Alert Name:** `DigitalAsset Test Order`

**Condition:** `Close > Open` (or any simple condition)

**Notification type:** `Webhook`

**Webhook URL:** `https://your-app-xxxx.railway.app/webhook`

**Message:** Copy this EXACTLY:
```json
{
  "broker": "DIGITAL_ASSET",
  "symbol": "BTCUSDT",
  "side": "buy",
  "quantity": 0.001,
  "type": "MARKET"
}
```

3. Click "Create Alert"

✅ **DONE:** Alert is set up to send orders to Railway

---

## PART 4: TEST THE CONNECTION (2 minutes)

### Step 4.1: Manually Fire the Webhook
**Option A: Using Postman (Easiest)**

1. Download Postman: https://www.postman.com/downloads/
2. Open Postman
3. Create a new POST request:

**URL:** `https://your-app-xxxx.railway.app/webhook`

**Method:** POST

**Headers:**
- Key: `Content-Type`
- Value: `application/json`

**Body:** (select "raw" and "JSON")
```json
{
  "broker": "DIGITAL_ASSET",
  "symbol": "BTCUSDT",
  "side": "buy",
  "quantity": 0.001,
  "type": "MARKET"
}
```

4. Click **Send**

**Option B: Using curl (Command Line)**

```bash
curl -X POST https://your-app-xxxx.railway.app/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "broker": "DIGITAL_ASSET",
    "symbol": "BTCUSDT",
    "side": "buy",
    "quantity": 0.001,
    "type": "MARKET"
  }'
```

### Step 4.2: Check Railway Logs
1. Go to Railway dashboard
2. Click **Deployments** → Latest
3. Go to **Logs** tab
4. Look for:
   - `"Processing DigitalAsset Signal: BUY BTCUSDT 0.001 @ MARKET"`
   - `"Order placed successfully"`
   - Order ID number

✅ **SUCCESS:** You should see order confirmation in logs

### Step 4.3: Verify Order in DigitalAsset Testnet
1. Go to https://testnet.binance.vision
2. Go to **Open Orders** or **Order History**
3. Look for your BTCUSDT order
4. Status should be **FILLED** or **PARTIALLY_FILLED**

✅ **DONE:** First order placed successfully!

---

## PART 5: TROUBLESHOOTING

### Issue: "Webhook 500 Error"
**Cause:** Flask app not starting  
**Fix:** Check Railway logs for Python errors

### Issue: "Order size too small (MIN_NOTIONAL)"
**Cause:** 0.001 BTC * price < 10 USDT  
**Fix:** Increase quantity to 0.05 or more

### Issue: "Order not appearing in DigitalAsset"
**Cause:** Check if testnet credentials are correct  
**Fix:** Verify API keys in Railway Variables

### Issue: "Invalid symbol BTCUSDT"
**Cause:** Symbol format wrong  
**Fix:** Use uppercase with USDT suffix

---

## PART 6: MOVE TO LIVE EXECUTION (When Ready)

### Step 6.1: Get Real DigitalAsset API Keys
1. Go to https://www.digital_asset.com/en/account/api-management (LIVE, not testnet)
2. Create new API key
3. Enable: "Enable Reading", "Enable Spot & Margin Execution", "Enable Futures Execution"
4. Copy keys

### Step 6.2: Update Railway Variables
```
BINANCE_API_KEY=your_REAL_api_key
BINANCE_API_SECRET=your_REAL_api_secret
BINANCE_TESTNET=false  ← CHANGE THIS TO FALSE
```

### Step 6.3: Update MarketFeed Alert
Change message to:
```json
{
  "broker": "BINANCE_REAL",
  "symbol": "BTCUSDT",
  "side": "buy",
  "quantity": 0.001,
  "type": "MARKET"
}
```

### Step 6.4: Test with Small Order
1. Send a test order with 0.001 BTC (~$40)
2. Watch Railway logs
3. Check DigitalAsset Live account for filled order
4. If successful, increase quantity gradually

⚠️ **WARNING:**  
- Start with SMALL quantities
- Monitor first 10-20 orders carefully
- Never trade with money you can't afford to lose
- Real money is at stake now!

---

## QUICK REFERENCE

### URLs You Need
```
DigitalAsset Testnet: https://testnet.binance.vision
Railway: https://railway.app
MarketFeed: https://market_feed.com
Webhook URL: https://your-app-xxxx.railway.app/webhook
```

### API Keys Location
```
Testnet: https://testnet.binance.vision → Generate HMAC SHA256 Key
Live: https://www.digital_asset.com/en/account/api-management
```

### Sample Webhook Messages

**Buy Order:**
```json
{"broker": "DIGITAL_ASSET", "symbol": "BTCUSDT", "side": "buy", "quantity": 0.001, "type": "MARKET"}
```

**Sell Order:**
```json
{"broker": "DIGITAL_ASSET", "symbol": "BTCUSDT", "side": "sell", "quantity": 0.001, "type": "MARKET"}
```

**Limit Order:**
```json
{"broker": "DIGITAL_ASSET", "symbol": "BTCUSDT", "side": "buy", "quantity": 0.001, "type": "LIMIT", "price": 43000}
```

---

## ✅ SUCCESS CHECKLIST

Before you consider "done", verify:

- [ ] Railway app is running (check logs)
- [ ] DigitalAsset testnet API keys are added to Railway
- [ ] MarketFeed webhook URL is correct
- [ ] Test order sent successfully
- [ ] Order appears in DigitalAsset Testnet Order History
- [ ] Railway logs show "Order placed successfully"
- [ ] You've tested at least 3-5 orders
- [ ] All orders executed correctly

✅ **When all checked:** Your system is ready!

---

## SUPPORT

If something doesn't work:

1. Check Railway Logs for error messages
2. Verify API keys are correctly set
3. Make sure webhook URL is exactly right
4. Test with Postman to isolate the issue
5. Check DigitalAsset account status and balance

**📝 Common Error Codes:**
- `-2019`: Margin insufficient
- `-1013`: Invalid quantity
- `-1000`: Unauthorized API key
- `MIN_NOTIONAL`: Order too small
- `INVALID_SYMBOL`: Wrong execution pair format

---

## 🎉 YOU'RE DONE!

Your auto-execution bot is now connected and working.

Next orders will:
1. Come from MarketFeed alerts
2. Hit your Railway webhook
3. Get processed by the Python bot
4. Execute on DigitalAsset Testnet/Live
5. Show up in Order History

**Happy execution!** 🚀
