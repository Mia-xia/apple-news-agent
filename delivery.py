# Email and Messaging Delivery

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import logging
import os
from typing import List

logger = logging.getLogger(__name__)

class EmailDelivery:
    """Handles email delivery of news briefings"""
    
    def __init__(self, sender: str, password: str, smtp_server: str, smtp_port: int):
        self.sender = sender
        self.password = password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
    
    def send(self, recipients: List[str], subject: str, body_html: str, body_text: str = None):
        """
        Send email with both HTML and plain text versions
        
        Args:
            recipients: List of email addresses
            subject: Email subject
            body_html: HTML formatted email body
            body_text: Plain text fallback (optional)
        """
        if not recipients or not self.sender or not self.password:
            logger.warning("Email delivery not configured. Skipping email send.")
            return False
        
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.sender
            msg["To"] = ", ".join(recipients)
            
            # Add plain text version
            if body_text:
                msg.attach(MIMEText(body_text, "plain"))
            
            # Add HTML version (preferred)
            msg.attach(MIMEText(body_html, "html"))
            
            # Send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender, self.password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {len(recipients)} recipients")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

class SlackDelivery:
    """Sends briefing to Slack webhook"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send(self, content: str, title: str = "Apple Daily News Brief"):
        """
        Send message to Slack
        
        Args:
            content: Message content
            title: Message title
        """
        if not self.webhook_url:
            logger.warning("Slack webhook not configured")
            return False
        
        try:
            payload = {
                "text": title,
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": content[:3000]  # Slack message limit
                        }
                    }
                ]
            }
            
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            
            logger.info("Message sent to Slack")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send Slack message: {e}")
            return False

class FileDelivery:
    """Saves briefing to local file"""
    
    @staticmethod
    def save(content: str, filename: str = "apple_news_brief.md"):
        """
        Save content to file
        
        Args:
            content: Formatted content to save
            filename: Output filename
        """
        try:
            parent = os.path.dirname(filename)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(filename, "w") as f:
                f.write(content)
            logger.info(f"Daily briefing saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to save briefing to file: {e}")
            return False
