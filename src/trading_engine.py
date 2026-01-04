import ccxt
import logging
from typing import Dict, Optional, List, Tuple
from decimal import Decimal
from datetime import datetime

logger = logging.getLogger(__name__)

class TradingEngine:
    """
    Trading engine for executing trades on Binance Futures.
    Handles order management, position sizing, and execution.
    """
    
    def __init__(self, exchange_id: str, api_key: str, api_secret: str, 
                 sandbox: bool = False):
        """
        Initialize trading engine.
        
        Args:
            exchange_id: Exchange ID (e.g., 'binance')
            api_key: API key for authentication
            api_secret: API secret for authentication
            sandbox: Use sandbox/demo trading
        """
        self.exchange_id = exchange_id
        self.sandbox = sandbox
        
        # Initialize exchange
        exchange_class = getattr(ccxt, exchange_id)
        self.exchange = exchange_class({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'sandbox': sandbox
        })
        
        # CRITICAL FIX #1: Load markets before any trading operations
        try:
            self.exchange.load_markets()
            logger.info(f"Markets loaded successfully for {exchange_id}")
        except Exception as e:
            logger.error(f"Error loading markets: {str(e)}")
        
        self.positions = {}
        self.open_orders = {}
    
    def _format_symbol(self, symbol: str) -> str:
        """
        Format symbol to CCXT standard (with forward slash).
        Converts BTCUSDT -> BTC/USDT
        
        Args:
            symbol: Symbol in any format
            
        Returns:
            Formatted symbol for CCXT
        """
        # If symbol already has /, return as-is
        if '/' in symbol:
            return symbol
        
        # Handle common formats
        if symbol.endswith('USDT'):
            return symbol[:-4] + '/USDT'
        elif symbol.endswith('BUSD'):
            return symbol[:-4] + '/BUSD'
        elif symbol.endswith('USDC'):
            return symbol[:-4] + '/USDC'
        elif symbol.endswith('USDT'):
            return symbol[:-4] + '/USDT'
        else:
            # Default: assume last 4 chars are quote currency
            return symbol[:-4] + '/' + symbol[-4:]
    
    def get_account_balance(self) -> Dict:
        """
        Get account balance and available funds.
        
        Returns:
            Dictionary with balance information
        """
        try:
            balance = self.exchange.fetch_balance()
            return {
                'total': balance.get('total', {}),
                'free': balance.get('free', {}),
                'used': balance.get('used', {})
            }
        except Exception as e:
            logger.error(f"Error fetching balance: {str(e)}")
            return {}
    
    def place_market_order(self, symbol: str, side: str, amount: float,
                          reduce_only: bool = False) -> Optional[Dict]:
        """
        Place a market order.
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT' or 'BTC/USDT')
            side: Order side ('buy' or 'sell')
            amount: Order amount
            reduce_only: Reduce position only (for futures)
            
        Returns:
            Order details or None
        """
        try:
            # CRITICAL FIX #2: Format symbol correctly for CCXT
            formatted_symbol = self._format_symbol(symbol)
            
            # Validate inputs
            if not formatted_symbol:
                logger.error(f"Invalid symbol format: {symbol}")
                return None
            
            if side.lower() not in ['buy', 'sell']:
                logger.error(f"Invalid side: {side}. Must be 'buy' or 'sell'")
                return None
            
            if amount <= 0:
                logger.error(f"Invalid amount: {amount}. Must be positive")
                return None
            
            params = {}
            if reduce_only:
                params['reduceOnly'] = True
            
            logger.info(f"Placing market order: {side.upper()} {amount} {formatted_symbol}")
            
            # CRITICAL FIX #3: Use correct CCXT method with formatted symbol
            order = self.exchange.create_market_order(
                symbol=formatted_symbol,
                side=side.lower(),
                amount=amount,
                params=params
            )
            
            logger.info(f"Market order placed successfully: {order['id']} - {side} {amount} {formatted_symbol}")
            self.open_orders[order['id']] = order
            return order
            
        except Exception as e:
            logger.error(f"Error placing market order for {symbol}: {str(e)}", exc_info=True)
            return None
    
    def place_limit_order(self, symbol: str, side: str, amount: float,
                         price: float, reduce_only: bool = False) -> Optional[Dict]:
        """
        Place a limit order.
        
        Args:
            symbol: Trading pair
            side: Order side
            amount: Order amount
            price: Limit price
            reduce_only: Reduce position only
            
        Returns:
            Order details or None
        """
        try:
            # Format symbol correctly
            formatted_symbol = self._format_symbol(symbol)
            
            if not formatted_symbol:
                logger.error(f"Invalid symbol format: {symbol}")
                return None
            
            params = {}
            if reduce_only:
                params['reduceOnly'] = True
            
            logger.info(f"Placing limit order: {side.upper()} {amount} {formatted_symbol} @ {price}")
            
            order = self.exchange.create_limit_order(
                symbol=formatted_symbol,
                side=side.lower(),
                amount=amount,
                price=price,
                params=params
            )
            
            logger.info(f"Limit order placed: {order['id']} - {side} {amount} {formatted_symbol} @ {price}")
            self.open_orders[order['id']] = order
            return order
            
        except Exception as e:
            logger.error(f"Error placing limit order: {str(e)}", exc_info=True)
            return None
    
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """
        Cancel an open order.
        
        Args:
            order_id: Order ID to cancel
            symbol: Trading pair
            
        Returns:
            True if successful, False otherwise
        """
        try:
            formatted_symbol = self._format_symbol(symbol)
            self.exchange.cancel_order(order_id, symbol=formatted_symbol)
            if order_id in self.open_orders:
                del self.open_orders[order_id]
            logger.info(f"Order cancelled: {order_id}")
            return True
        except Exception as e:
            logger.error(f"Error cancelling order: {str(e)}")
            return False
    
    def get_open_positions(self, symbol: str = None) -> List[Dict]:
        """
        Get open positions.
        
        Args:
            symbol: Specific symbol or None for all
            
        Returns:
            List of open positions
        """
        try:
            if symbol:
                symbol = self._format_symbol(symbol)
            positions = self.exchange.fetch_positions([symbol] if symbol else None)
            return [p for p in positions if p['contracts'] > 0]
        except Exception as e:
            logger.error(f"Error fetching positions: {str(e)}", exc_info=True)
            return []
    
    def get_ticker(self, symbol: str) -> Optional[Dict]:
        """
        Get current ticker information.
        
        Args:
            symbol: Trading pair
            
        Returns:
            Ticker data or None
        """
        try:
            formatted_symbol = self._format_symbol(symbol)
            return self.exchange.fetch_ticker(formatted_symbol)
        except Exception as e:
            logger.error(f"Error fetching ticker: {str(e)}")
            return None
    
    def calculate_order_size(self, symbol: str, risk_percent: float,
                            entry_price: float, stop_loss_price: float) -> float:
        """
        Calculate order size based on risk management.
        
        Args:
            symbol: Trading pair
            risk_percent: Risk percentage of account
            entry_price: Entry price
            stop_loss_price: Stop loss price
            
        Returns:
            Order size
        """
        try:
            balance = self.get_account_balance()
            usdt_balance = balance['free'].get('USDT', 0)
            
            risk_amount = usdt_balance * (risk_percent / 100)
            price_risk = abs(entry_price - stop_loss_price)
            
            if price_risk == 0:
                return 0
            
            order_size = risk_amount / price_risk
            return round(order_size, 4)
        except Exception as e:
            logger.error(f"Error calculating order size: {str(e)}")
            return 0
