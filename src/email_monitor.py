import imaplib
import json
import email
from email.header import decode_header
from typing import List, Dict, Optional
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class EmailMonitor:
    """
    Monitors email alerts from TradingView and parses trading signals.
    """
    
    def __init__(self, email_address: str, password: str, imap_server: str = "imap.gmail.com"):
        """
        Initialize email monitor.
        
        Args:
            email_address: Gmail address to monitor
            password: App-specific password for Gmail
            imap_server: IMAP server address (default: Gmail)
        """
        self.email_address = email_address
        self.password = password
        self.imap_server = imap_server
        self.mail = None
    
    def connect(self) -> bool:
        """
        Establish connection to email server.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.mail = imaplib.IMAP4_SSL(self.imap_server)
            self.mail.login(self.email_address, self.password)
            logger.info(f"Connected to {self.imap_server}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to email server: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from email server."""
        if self.mail:
            self.mail.close()
            logger.info("Disconnected from email server")
    
    def fetch_trading_alerts(self, sender_filter: str = "noreply@tradingview.com") -> List[Dict]:
        """
        Fetch unread trading alerts from email.
        
        Args:
            sender_filter: Filter emails from specific sender
            
        Returns:
            List of alert dictionaries with signal information
        """
        try:
            self.mail.select("INBOX")
            status, messages = self.mail.search(None, "UNSEEN")
            
            alerts = []
            msg_ids = messages[0].split()
            
            for msg_id in msg_ids[-10:]:  # Get last 10 messages
                status, msg = self.mail.fetch(msg_id, "(RFC822)")
                email_msg = email.message_from_bytes(msg[0][1])
                
                # Check sender
                if sender_filter not in email_msg.get("From", ""):
                    continue
                
                alert = self._parse_alert(email_msg)
                if alert:
                    alerts.append(alert)
                    # Mark as read
                    self.mail.store(msg_id, "+FLAGS", "\\Seen")
            
            return alerts
        except Exception as e:
            logger.error(f"Error fetching alerts: {str(e)}")
            return []
    
    def _parse_alert(self, email_msg) -> Optional[Dict]:
        """
        Parse TradingView alert from email message.
        
        Args:
            email_msg: Email message object
            
        Returns:
            Dictionary with parsed alert data or None
        """
        try:
            subject = email_msg.get("Subject")
            body = self._get_email_body(email_msg)
            
            # Try to parse JSON alert
            try:
                alert_data = json.loads(body)
                return {
                    "timestamp": datetime.now().isoformat(),
                    "subject": subject,
                    **alert_data
                }
            except json.JSONDecodeError:
                # Parse text format alert
                return self._parse_text_alert(subject, body)
        except Exception as e:
            logger.error(f"Error parsing alert: {str(e)}")
            return None
    
    def _get_email_body(self, email_msg) -> str:
        """
        Extract email body text.
        
        Args:
            email_msg: Email message object
            
        Returns:
            Email body as string
        """
        body = ""
        if email_msg.is_multipart():
            for part in email_msg.get_payload():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = email_msg.get_payload(decode=True).decode()
        return body
    
    def _parse_text_alert(self, subject: str, body: str) -> Optional[Dict]:
        """
        Parse text format alert.
        
        Args:
            subject: Email subject
            body: Email body
            
        Returns:
            Dictionary with alert data or None
        """
        try:
            # Extract signal type (BUY/SELL)
            signal_match = re.search(r'(BUY|SELL|LONG|SHORT)', body.upper())
            signal = signal_match.group(1) if signal_match else None
            
            if not signal:
                return None
            
            return {
                "timestamp": datetime.now().isoformat(),
                "subject": subject,
                "signal": signal,
                "body": body[:500]
            }
        except Exception as e:
            logger.error(f"Error parsing text alert: {str(e)}")
            return None
