import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('trading_bot.log'),
            logging.StreamHandler()
        ]
    )


def load_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables.
    
    Returns:
        Configuration dictionary
    """
    load_dotenv()
    
    config = {
        'binance_api_key': os.getenv('BINANCE_API_KEY'),
        'binance_api_secret': os.getenv('BINANCE_API_SECRET'),
        'email_address': os.getenv('EMAIL_ADDRESS'),
        'email_password': os.getenv('EMAIL_PASSWORD'),
        'sandbox_mode': os.getenv('SANDBOX_MODE', 'true').lower() == 'true',
        'risk_percent': float(os.getenv('RISK_PERCENT', '1.0')),
        'max_concurrent_positions': int(os.getenv('MAX_CONCURRENT_POSITIONS', '3')),
        'max_daily_loss_percent': float(os.getenv('MAX_DAILY_LOSS_PERCENT', '5.0')),
        'symbol': os.getenv('TRADING_SYMBOL', 'BTC/USDT')
    }
    
    return config


def parse_alert_json(alert_json: str) -> Optional[Dict]:
    """
    Parse JSON alert from email.
    
    Args:
        alert_json: JSON string from alert
        
    Returns:
        Parsed dictionary or None
    """
    try:
        return json.loads(alert_json)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse alert JSON: {str(e)}")
        return None


def format_price(price: float, decimals: int = 2) -> str:
    """
    Format price for display.
    
    Args:
        price: Price value
        decimals: Number of decimal places
        
    Returns:
        Formatted price string
    """
    return f"{price:.{decimals}f}"


def calculate_sma(prices: List[float], period: int) -> float:
    """
    Calculate Simple Moving Average.
    
    Args:
        prices: List of prices
        period: SMA period
        
    Returns:
        SMA value
    """
    if len(prices) < period:
        return sum(prices) / len(prices)
    return sum(prices[-period:]) / period


def calculate_ema(prices: List[float], period: int) -> float:
    """
    Calculate Exponential Moving Average.
    
    Args:
        prices: List of prices
        period: EMA period
        
    Returns:
        EMA value
    """
    if len(prices) < period:
        return calculate_sma(prices, len(prices))
    
    multiplier = 2 / (period + 1)
    ema = calculate_sma(prices[:period], period)
    
    for price in prices[period:]:
        ema = (price * multiplier) + (ema * (1 - multiplier))
    
    return ema


def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """
    Calculate Relative Strength Index.
    
    Args:
        prices: List of prices
        period: RSI period
        
    Returns:
        RSI value (0-100)
    """
    if len(prices) < period + 1:
        return 50
    
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas[-period:]]
    losses = [abs(d) if d < 0 else 0 for d in deltas[-period:]]
    
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    
    if avg_loss == 0:
        return 100 if avg_gain > 0 else 50
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
    """
    Calculate MACD indicator.
    
    Args:
        prices: List of prices
        fast: Fast EMA period
        slow: Slow EMA period
        signal: Signal line period
        
    Returns:
        Dictionary with MACD, Signal, and Histogram
    """
    fast_ema = calculate_ema(prices, fast)
    slow_ema = calculate_ema(prices, slow)
    macd_line = fast_ema - slow_ema
    
    signal_line = calculate_ema([macd_line], signal)
    histogram = macd_line - signal_line
    
    return {
        'macd': macd_line,
        'signal': signal_line,
        'histogram': histogram
    }


def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2.0) -> Dict:
    """
    Calculate Bollinger Bands.
    
    Args:
        prices: List of prices
        period: BB period
        std_dev: Standard deviation multiplier
        
    Returns:
        Dictionary with upper, middle, and lower bands
    """
    if len(prices) < period:
        return {}
    
    recent_prices = prices[-period:]
    middle = sum(recent_prices) / period
    variance = sum((p - middle) ** 2 for p in recent_prices) / period
    std = variance ** 0.5
    
    return {
        'upper': middle + (std * std_dev),
        'middle': middle,
        'lower': middle - (std * std_dev)
    }


def get_time_until_next_candle(timeframe: str = "1h") -> int:
    """
    Calculate seconds until next candle opens.
    
    Args:
        timeframe: Candle timeframe (1m, 5m, 15m, 1h, 4h, 1d)
        
    Returns:
        Seconds until next candle
    """
    timeframe_minutes = {
        '1m': 1, '5m': 5, '15m': 15, '30m': 30,
        '1h': 60, '4h': 240, '1d': 1440
    }
    
    minutes = timeframe_minutes.get(timeframe, 60)
    now = datetime.now()
    
    # Round up to next period
    seconds_in_period = minutes * 60
    elapsed = (now.hour * 3600 + now.minute * 60 + now.second)
    seconds_to_next = seconds_in_period - (elapsed % seconds_in_period)
    
    return seconds_to_next


def format_alert_message(symbol: str, signal: str, entry: float, 
                        stop_loss: float, take_profit: float) -> str:
    """
    Format alert message for logging.
    
    Args:
        symbol: Trading pair
        signal: Signal type (BUY/SELL)
        entry: Entry price
        stop_loss: Stop loss price
        take_profit: Take profit price
        
    Returns:
        Formatted message
    """
    return f"""
    Trading Alert
    Symbol: {symbol}
    Signal: {signal}
    Entry: {format_price(entry)}
    Stop Loss: {format_price(stop_loss)}
    Take Profit: {format_price(take_profit)}
    Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
