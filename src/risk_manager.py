import logging
from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk level classifications."""
    LOW = 0.5
    MEDIUM = 1.0
    HIGH = 2.0
    VERY_HIGH = 3.0


@dataclass
class RiskParameters:
    """Risk management parameters."""
    max_position_size: float
    max_drawdown: float
    max_daily_loss: float
    risk_per_trade: float
    max_concurrent_positions: int
    trailing_stop_percent: float


class RiskManager:
    """
    Manages trading risk including position sizing,
    stop losses, and drawdown monitoring.
    """
    
    def __init__(self, account_balance: float, risk_params: RiskParameters):
        """
        Initialize risk manager.
        
        Args:
            account_balance: Initial account balance
            risk_params: Risk management parameters
        """
        self.account_balance = account_balance
        self.initial_balance = account_balance
        self.risk_params = risk_params
        self.open_positions = {}
        self.daily_loss = 0
        self.peak_balance = account_balance
    
    def update_balance(self, new_balance: float):
        """
        Update account balance and track drawdowns.
        
        Args:
            new_balance: Current account balance
        """
        self.account_balance = new_balance
        self.daily_loss = self.initial_balance - new_balance
        
        # Update peak balance for drawdown calculation
        if new_balance > self.peak_balance:
            self.peak_balance = new_balance
    
    def can_open_position(self, symbol: str, size: float, entry_price: float) -> bool:
        """
        Check if a new position meets risk criteria.
        
        Args:
            symbol: Trading pair
            size: Position size
            entry_price: Entry price
            
        Returns:
            True if position is acceptable, False otherwise
        """
        # Check concurrent positions limit
        if len(self.open_positions) >= self.risk_params.max_concurrent_positions:
            logger.warning(f"Max concurrent positions ({self.risk_params.max_concurrent_positions}) reached")
            return False
        
        # Check position size
        position_value = size * entry_price
        if position_value > self.risk_params.max_position_size:
            logger.warning(f"Position size ({position_value}) exceeds max ({self.risk_params.max_position_size})")
            return False
        
        # Check daily loss limit
        if self.daily_loss > self.risk_params.max_daily_loss:
            logger.warning(f"Daily loss ({self.daily_loss}) exceeds limit ({self.risk_params.max_daily_loss})")
            return False
        
        return True
    
    def calculate_stop_loss(self, entry_price: float, position_type: str,
                           atr: Optional[float] = None) -> float:
        """
        Calculate stop loss price based on risk parameters.
        
        Args:
            entry_price: Entry price
            position_type: 'long' or 'short'
            atr: Average True Range for volatility-based stops
            
        Returns:
            Stop loss price
        """
        if atr:
            # Use ATR-based stop loss
            multiplier = 2.0
            if position_type == 'long':
                return entry_price - (atr * multiplier)
            else:
                return entry_price + (atr * multiplier)
        else:
            # Use percentage-based stop loss
            stop_loss_percent = self.risk_params.risk_per_trade
            if position_type == 'long':
                return entry_price * (1 - stop_loss_percent / 100)
            else:
                return entry_price * (1 + stop_loss_percent / 100)
    
    def calculate_take_profit(self, entry_price: float, stop_loss_price: float,
                             risk_reward_ratio: float = 2.0) -> float:
        """
        Calculate take profit price based on risk/reward ratio.
        
        Args:
            entry_price: Entry price
            stop_loss_price: Stop loss price
            risk_reward_ratio: Risk to reward ratio (default 2:1)
            
        Returns:
            Take profit price
        """
        risk = abs(entry_price - stop_loss_price)
        profit_target = risk * risk_reward_ratio
        
        if entry_price > stop_loss_price:  # Long position
            return entry_price + profit_target
        else:  # Short position
            return entry_price - profit_target
    
    def add_position(self, symbol: str, size: float, entry_price: float,
                     stop_loss: float, take_profit: float):
        """
        Register an open position.
        
        Args:
            symbol: Trading pair
            size: Position size
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
        """
        self.open_positions[symbol] = {
            'size': size,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'current_price': entry_price,
            'pnl': 0
        }
        logger.info(f"Position opened: {symbol} @ {entry_price} (Size: {size})")
    
    def update_position(self, symbol: str, current_price: float):
        """
        Update position with current price.
        
        Args:
            symbol: Trading pair
            current_price: Current market price
        """
        if symbol not in self.open_positions:
            return
        
        position = self.open_positions[symbol]
        position['current_price'] = current_price
        
        # Calculate P&L
        price_diff = current_price - position['entry_price']
        position['pnl'] = price_diff * position['size']
    
    def close_position(self, symbol: str, exit_price: float) -> Optional[Dict]:
        """
        Close an open position.
        
        Args:
            symbol: Trading pair
            exit_price: Exit price
            
        Returns:
            Position details with P&L or None
        """
        if symbol not in self.open_positions:
            return None
        
        position = self.open_positions[symbol]
        pnl = (exit_price - position['entry_price']) * position['size']
        position['pnl'] = pnl
        position['exit_price'] = exit_price
        
        del self.open_positions[symbol]
        logger.info(f"Position closed: {symbol} @ {exit_price} (P&L: {pnl})")
        
        return position
    
    def get_drawdown_percent(self) -> float:
        """
        Calculate current drawdown percentage.
        
        Returns:
            Drawdown percentage
        """
        if self.peak_balance == 0:
            return 0
        return ((self.peak_balance - self.account_balance) / self.peak_balance) * 100
    
    def is_drawdown_exceeded(self) -> bool:
        """
        Check if drawdown exceeds maximum allowed.
        
        Returns:
            True if drawdown exceeded, False otherwise
        """
        return self.get_drawdown_percent() > self.risk_params.max_drawdown
