# MarketFeed-DigitalAsset Automated Execution Bot

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/yourusername/market_feed-digital_asset-bot.svg)](https://github.com/yourusername/market_feed-digital_asset-bot)

A powerful, production-ready Python bot that automates execution between MarketFeed and DigitalAsset Futures. Execute trades automatically from MarketFeed alert signals with advanced risk management, backtesting capabilities, and real-time monitoring.

## Features

### Core Execution Features
- **MarketFeed Alert Integration**: Monitor email alerts and execute trades instantly
- **DigitalAsset Futures Support**: Trade on Spot, Margin, and Futures markets
- **Multiple Order Types**: Market, Limit, Stop-Loss, Take-Profit orders
- **Position Management**: Auto-scaling, trailing stops, partial takes
- **Risk Management**: Risk percentage, max loss, position sizing
- **Multi-Pair Execution**: Handle multiple execution pairs simultaneously

### Technical Features
- **CCXT Library**: Support for 50+ cryptocurrency exchanges
- **Email Monitoring**: Real-time alert processing via IMAP
- **JSON Configuration**: Easy setup without coding
- **Backtesting Engine**: Test strategies on historical data
- **Logging & Monitoring**: Detailed execution logs and statistics
- **Error Handling**: Automatic retry and error recovery

### Pine Script Support
- Ready-to-use Pine Script strategies
- MarketFeed alert formatting
- Customizable signal generation

## Quick Start

### Prerequisites
- Python 3.8 or higher
- DigitalAsset account (Spot or Futures)
- MarketFeed account
- Gmail account (for email alerts)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/market_feed-digital_asset-bot.git
cd market_feed-digital_asset-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. **Create `.env` file** in project root:
```env
# DigitalAsset API
BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_api_secret
BINANCE_TESTNET=true  # Set to false for live execution

# Email Configuration
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_IMAP_SERVER=imap.gmail.com

# Execution Parameters
DEFAULT_SYMBOL=BTCUSDT
DEFAULT_LEVERAGE=1
RISK_PERCENTAGE=2
MAX_POSITIONS=5
```

2. **Update `config.json`** with your execution parameters:
```json
{
  "execution": {
    "demo_mode": false,
    "live_mode": true,
    "symbols": ["BTCUSDT", "ETHUSDT"],
    "leverage": 1,
    "order_type": "MARKET"
  },
  "risk_management": {
    "risk_per_trade": 2.0,
    "max_daily_loss": 5.0,
    "max_open_positions": 5,
    "trailing_stop_percent": 2.0
  },
  "email": {
    "check_interval": 30,
    "alert_folder": "MarketFeed"
  }
}
```

### Running the Bot

```bash
# Start email monitoring
python main.py

# Or run with configuration file
python main.py --config config.json

# Backtest strategy
python backtest.py --symbol BTCUSDT --timeframe 1h
```

## Project Structure

```
market_feed-digital_asset-bot/
├── src/
│   ├── main.py                 # Entry point
│   ├── email_monitor.py        # Email alert handler
│   ├── trading_engine.py       # Core execution logic
│   ├── binance_api.py          # DigitalAsset API wrapper
│   ├── risk_manager.py         # Risk management
│   ├── logger.py               # Logging setup
│   └── utils.py                # Utility functions
├── strategies/
│   ├── pine_scripts/           # MarketFeed Pine Script files
│   └── python_strategies/      # Python strategy implementations
├── config/
│   ├── config.json             # Main configuration
│   └── symbols.json            # Execution pairs config
├── logs/                       # Execution logs
├── backtesting/
│   ├── backtest.py            # Backtesting engine
│   └── results/               # Backtest results
├── tests/
│   ├── test_trading.py        # Unit tests
│   └── test_api.py            # API tests
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── README.md                  # This file
└── LICENSE                    # MIT License
```

## API Configuration

### DigitalAsset API Setup

1. Go to [DigitalAsset API Management](https://www.digital_asset.com/en/account/api-management)
2. Create new API Key
3. Enable required permissions:
   - ✅ Enable Reading
   - ✅ Enable Spot & Margin Execution
   - ✅ Enable Futures Execution (if using Futures)
4. Set IP Whitelist (recommended)
5. Save API Key and Secret

### Gmail Setup (for Email Alerts)

1. Enable 2-Factor Authentication in Gmail
2. Generate [App Password](https://myaccount.google.com/apppasswords)
3. Use app password in `.env` file

### MarketFeed Alert Configuration

1. In your MarketFeed strategy, create alert:
```
Alert Message:
{
  "symbol": "BTCUSDT",
  "side": "buy",
  "quantity": 0.01,
  "type": "market",
  "take_profit": 89500,
  "stop_loss": 88500
}
```

## Execution Examples

### Example 1: Simple Market Order
```python
from src.trading_engine import TradingEngine

engine = TradingEngine()
order = engine.place_order(
    symbol='BTCUSDT',
    side='buy',
    quantity=0.01,
    order_type='MARKET'
)
print(f"Order placed: {order['orderId']}")
```

### Example 2: With Risk Management
```python
order = engine.place_order(
    symbol='ETHUSDT',
    side='buy',
    quantity=0.1,
    order_type='LIMIT',
    price=3000,
    stop_loss=2950,
    take_profit=3050
)
```

### Example 3: Process Email Alert
```python
from src.email_monitor import EmailMonitor

monitor = EmailMonitor()
alert = monitor.get_latest_alert()
if alert:
    signal = monitor.parse_alert(alert)
    order = engine.execute_signal(signal)
```

## Risk Management

The bot includes sophisticated risk management:

- **Position Sizing**: Automatically calculates position size based on risk percentage
- **Stop Loss**: Automatic stop-loss placement
- **Take Profit**: Multiple take-profit levels
- **Max Drawdown**: Daily loss limits
- **Trailing Stop**: Dynamic stop-loss adjustment
- **Exposure Limits**: Maximum open positions

## Backtesting

```bash
python backtesting/backtest.py \
  --symbol BTCUSDT \
  --timeframe 1h \
  --start-date 2023-01-01 \
  --end-date 2023-12-31 \
  --initial-capital 10000
```

## Monitoring & Logging

All trades are logged to `logs/` directory:

```
logs/
├── trades_2024.log         # Trade execution logs
├── alerts_2024.log         # Alert processing logs
├── errors_2024.log         # Error logs
└── performance_2024.log    # Performance metrics
```

## Advanced Features

### Multi-Signal Processing
Handle multiple concurrent execution signals

### Portfolio Management
Manage positions across multiple pairs

### Custom Strategies
Implement your own execution strategies in Python

### Webhook Support
Alternative to email-based alerts

## Performance

- **Alert Response Time**: < 1 second
- **Order Execution**: < 500ms
- **Email Check Interval**: Configurable (default: 30s)
- **Memory Usage**: ~100-150MB

## Security

⚠️ **IMPORTANT SECURITY NOTES**:

1. Never commit `.env` file or API keys to repository
2. Use IP whitelisting on DigitalAsset API
3. Enable 2FA on all accounts
4. Use strong, unique passwords
5. Regularly audit API permissions
6. Consider running bot on dedicated VPS
7. Always backtest strategies before live execution

## Testing

```bash
# Run unit tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_trading.py::TestTradingEngine::test_place_order
```

## Troubleshooting

### Bot not receiving alerts?
- Check email folder is "MarketFeed"
- Verify Gmail app password is correct
- Check IMAP is enabled in Gmail settings

### Orders not executing?
- Verify API keys have correct permissions
- Check if execution pair exists on DigitalAsset
- Review account balance
- Check logs for detailed errors

### Connection issues?
- Verify internet connection
- Check if DigitalAsset API is accessible
- Try updating CCXT library

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## Disclaimer

⚠️ **Execution Disclaimer**:

This bot is for educational and research purposes only. Cryptocurrency and futures execution carries significant risk:

- You can lose your entire investment
- Past performance does not guarantee future results
- Always test thoroughly on testnet first
- Start with small position sizes
- Never trade with money you cannot afford to lose
- The authors are not responsible for execution losses

## License

MIT License - see LICENSE file for details

## Support

- 📖 [Documentation](https://github.com/yourusername/market_feed-digital_asset-bot/wiki)
- 🐛 [Report Issues](https://github.com/yourusername/market_feed-digital_asset-bot/issues)
- 💬 [Discussions](https://github.com/yourusername/market_feed-digital_asset-bot/discussions)
- 📧 Email: your-email@example.com

## Acknowledgments

- [CCXT](https://github.com/ccxt/ccxt) - Cryptocurrency exchange execution library
- [DigitalAsset API](https://digital_asset-docs.github.io/apidocs/) - DigitalAsset official documentation
- [MarketFeed](https://www.market_feed.com/) - Execution platform

## Roadmap

- [ ] Web dashboard for monitoring
- [ ] Telegram notifications
- [ ] Discord integration
- [ ] Advanced ML-based signal filtering
- [ ] Portfolio optimization
- [ ] Multi-exchange support
- [ ] Mobile app

---

**Made with ❤️ for traders**

If you found this helpful, please consider giving it a ⭐
