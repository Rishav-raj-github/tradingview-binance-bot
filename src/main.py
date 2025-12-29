#!/usr/bin/env python3
"""
TradingView-Binance Automated Trading Bot
Main entry point for the trading bot application
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from email_monitor import EmailMonitor
from trading_engine import TradingEngine
from risk_manager import RiskManager
from logger import setup_logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class TradingBot:
    """Main trading bot orchestrator"""

    def __init__(self, config_file=None):
        """Initialize the trading bot with configuration"""
        setup_logging()
        
        self.email_monitor = EmailMonitor()
        self.trading_engine = TradingEngine()
        self.risk_manager = RiskManager()
        
        logger.info("Trading Bot initialized successfully")

    def start(self):
        """Start the bot and begin monitoring alerts"""
        logger.info("Starting TradingView Alert Monitoring...")
        
        try:
            while True:
                # Check for new alerts
                alerts = self.email_monitor.check_alerts()
                
                for alert in alerts:
                    logger.info(f"Processing alert: {alert}")
                    
                    # Parse alert signal
                    signal = self.email_monitor.parse_alert(alert)
                    
                    if not signal:
                        logger.warning("Could not parse alert")
                        continue
                    
                    # Validate with risk manager
                    if not self.risk_manager.validate_signal(signal):
                        logger.warning(f"Signal failed risk validation: {signal}")
                        continue
                    
                    # Execute trade
                    try:
                        order = self.trading_engine.execute_signal(signal)
                        logger.info(f"Order executed: {order}")
                    except Exception as e:
                        logger.error(f"Error executing order: {e}")
                        
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Critical error: {e}", exc_info=True)
        finally:
            self.shutdown()

    def shutdown(self):
        """Clean shutdown of the bot"""
        logger.info("Shutting down bot...")
        # Add cleanup code here
        logger.info("Bot shutdown complete")


def main():
    """Entry point for the application"""
    parser = argparse.ArgumentParser(description="TradingView-Binance Trading Bot")
    parser.add_argument(
        "--config",
        type=str,
        default="config/config.json",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo/testnet mode"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    # Set demo mode
    if args.demo:
        os.environ["BINANCE_TESTNET"] = "true"
    
    # Set debug logging
    if args.debug:
        os.environ["LOG_LEVEL"] = "DEBUG"
    
    # Create and start bot
    bot = TradingBot(config_file=args.config)
    bot.start()


if __name__ == "__main__":
    main()
