"""Firestore PnL Recording Module - Real-time Trade Recording
Records all trades (executed and rejected) to Google Cloud Firestore
for real-time PnL tracking and analysis.
"""

import os
import json
import logging
from datetime import datetime
from decimal import Decimal

try:
    import firebase_admin
    from firebase_admin import credentials
    from firebase_admin import firestore
    FIRESTORE_AVAILABLE = True
except ImportError:
    FIRESTORE_AVAILABLE = False
    print("⚠️ Firebase Admin SDK not installed. Install with: pip install firebase-admin")

logger = logging.getLogger(__name__)

class FirestorePnLRecorder:
    """Manages all PnL recording to Firestore database"""
    
    def __init__(self, credentials_path=None):
        """Initialize Firestore connection
        
        Args:
            credentials_path: Path to Google Cloud service account JSON key
                            If None, uses GOOGLE_APPLICATION_CREDENTIALS env var
        """
        self.db = None
        self.project_id = "trading-bot-automation-487910"
        self.database_name = "trading-bot-pnl"
        
        if not FIRESTORE_AVAILABLE:
            logger.warning("Firestore unavailable - PnL recording disabled")
            return
            
        try:
            # Initialize Firebase if not already done
            if not firebase_admin._apps:
                if credentials_path:
                    creds = credentials.Certificate(credentials_path)
                    firebase_admin.initialize_app(creds)
                else:
                    firebase_admin.initialize_app()
            
            self.db = firestore.client()
            logger.info(f"✅ Firestore connected to {self.database_name} database")
        except Exception as e:
            logger.error(f"❌ Firestore connection failed: {str(e)}")
            self.db = None
    
    def record_order(self, order_data):
        """Record order to 'orders' collection (executed and rejected)
        
        Args:
            order_data: Dict with order details
                - orderId: str
                - symbol: str
                - side: str (BUY/SELL)
                - price: float
                - quantity: float
                - status: str (EXECUTED/REJECTED/PENDING)
                - timestamp: datetime or str
                - error_reason: str (optional, for rejected orders)
        """
        if not self.db:
            logger.warning("Cannot record order - Firestore not connected")
            return False
            
        try:
            order_id = order_data.get('orderId', f"order_{int(datetime.now().timestamp())}")
            
            # Prepare order document
            order_doc = {
                'orderId': order_data.get('orderId'),
                'symbol': order_data.get('symbol'),
                'side': order_data.get('side'),  # BUY or SELL
                'price': float(order_data.get('price', 0)),
                'quantity': float(order_data.get('quantity', 0)),
                'status': order_data.get('status', 'PENDING'),
                'timestamp': datetime.now(),
                'error_reason': order_data.get('error_reason', ''),
            }
            
            # Record to orders collection
            self.db.collection('orders').document(order_id).set(order_doc)
            logger.info(f"📝 Order recorded: {order_id} ({order_data.get('symbol')}) - {order_data.get('status')}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to record order: {str(e)}")
            return False
    
    def record_trade(self, trade_data):
        """Record executed trade to 'trades' collection with PnL
        
        Args:
            trade_data: Dict with trade details
                - tradeId: str
                - symbol: str
                - entry_price: float
                - exit_price: float (optional, for closed trades)
                - quantity: float
                - status: str
        """
        if not self.db:
            logger.warning("Cannot record trade - Firestore not connected")
            return False
            
        try:
            trade_id = trade_data.get('tradeId', f"trade_{int(datetime.now().timestamp())}")
            
            entry_price = float(trade_data.get('entry_price', 0))
            exit_price = float(trade_data.get('exit_price', entry_price))  # Default to entry if not closed
            quantity = float(trade_data.get('quantity', 0))
            
            # Calculate PnL
            pnl = (exit_price - entry_price) * quantity
            pnl_percent = ((exit_price - entry_price) / entry_price * 100) if entry_price != 0 else 0
            
            trade_doc = {
                'tradeId': trade_data.get('tradeId'),
                'symbol': trade_data.get('symbol'),
                'entry_price': entry_price,
                'exit_price': exit_price,
                'quantity': quantity,
                'pnl': round(pnl, 2),
                'pnl_percent': round(pnl_percent, 2),
                'status': trade_data.get('status', 'OPEN'),
                'timestamp': datetime.now(),
            }
            
            self.db.collection('trades').document(trade_id).set(trade_doc)
            logger.info(f"💰 Trade recorded: {trade_id} ({trade_data.get('symbol')}) - PnL: {pnl:.2f}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to record trade: {str(e)}")
            return False
    
    def update_daily_pnl(self, date_str=None):
        """Calculate and update daily PnL summary
        
        Args:
            date_str: Date string (YYYY-MM-DD). If None, uses today's date
        """
        if not self.db:
            logger.warning("Cannot update daily PnL - Firestore not connected")
            return False
            
        try:
            from datetime import date, timedelta
            
            if date_str is None:
                date_str = date.today().isoformat()
            
            # Query trades for the day
            start_date = datetime.fromisoformat(date_str)
            end_date = start_date + timedelta(days=1)
            
            trades_ref = self.db.collection('trades')
            trades = trades_ref.where('timestamp', '>=', start_date).where(
                'timestamp', '<', end_date
            ).stream()
            
            total_pnl = 0
            winning_trades = 0
            losing_trades = 0
            total_trades = 0
            
            for trade in trades:
                trade_data = trade.to_dict()
                total_trades += 1
                pnl = float(trade_data.get('pnl', 0))
                total_pnl += pnl
                
                if pnl > 0:
                    winning_trades += 1
                elif pnl < 0:
                    losing_trades += 1
            
            # Calculate win rate
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            # Update pnl_calculations collection
            pnl_summary = {
                'period': date_str,
                'total_pnl': round(total_pnl, 2),
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': round(win_rate, 2),
                'updated_at': datetime.now(),
            }
            
            doc_id = f"pnl_{date_str.replace('-', '_')}"
            self.db.collection('pnl_calculations').document(doc_id).set(pnl_summary)
            logger.info(f"📊 Daily PnL updated: {date_str} - Total: {total_pnl:.2f}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to update daily PnL: {str(e)}")
            return False
    
    def get_trades(self, symbol=None, limit=10):
        """Retrieve recent trades from Firestore
        
        Args:
            symbol: Optional symbol filter
            limit: Number of trades to retrieve
        
        Returns:
            List of trade dictionaries
        """
        if not self.db:
            logger.warning("Cannot retrieve trades - Firestore not connected")
            return []
            
        try:
            trades_ref = self.db.collection('trades')
            
            if symbol:
                query = trades_ref.where('symbol', '==', symbol)
            else:
                query = trades_ref
            
            trades = query.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit).stream()
            
            return [trade.to_dict() for trade in trades]
        except Exception as e:
            logger.error(f"❌ Failed to retrieve trades: {str(e)}")
            return []
    
    def get_daily_pnl(self, date_str=None):
        """Get daily PnL summary
        
        Args:
            date_str: Date string (YYYY-MM-DD). If None, uses today's date
        
        Returns:
            Dictionary with daily PnL data
        """
        if not self.db:
            logger.warning("Cannot retrieve daily PnL - Firestore not connected")
            return {}
            
        try:
            from datetime import date
            
            if date_str is None:
                date_str = date.today().isoformat()
            
            doc_id = f"pnl_{date_str.replace('-', '_')}"
            doc = self.db.collection('pnl_calculations').document(doc_id).get()
            
            if doc.exists:
                return doc.to_dict()
            else:
                logger.warning(f"No PnL data found for {date_str}")
                return {}
        except Exception as e:
            logger.error(f"❌ Failed to retrieve daily PnL: {str(e)}")
            return {}

# Global instance
_pnl_recorder = None

def get_pnl_recorder():
    """Get or create global PnL recorder instance"""
    global _pnl_recorder
    if _pnl_recorder is None:
        _pnl_recorder = FirestorePnLRecorder()
    return _pnl_recorder

def record_order_to_firestore(order_data):
    """Convenience function to record order"""
    recorder = get_pnl_recorder()
    return recorder.record_order(order_data)

def record_trade_to_firestore(trade_data):
    """Convenience function to record trade"""
    recorder = get_pnl_recorder()
    return recorder.record_trade(trade_data)

def update_daily_pnl_to_firestore(date_str=None):
    """Convenience function to update daily PnL"""
    recorder = get_pnl_recorder()
    return recorder.update_daily_pnl(date_str)
