#!/usr/bin/env python3
"""
Apple News Monitoring & Daily Push Agent

This agent continuously monitors news sources for Apple-related updates
and delivers a daily briefing via email.
"""

import logging
import schedule
import time
import os
from datetime import datetime, timedelta
from typing import List
import pytz

from config import (
    NEWSAPI_KEY, TWITTER_BEARER_TOKEN, EMAIL_SENDER, EMAIL_PASSWORD,
    SMTP_SERVER, SMTP_PORT, EMAIL_RECIPIENTS, SLACK_WEBHOOK_URL,
    RSS_FEEDS, SCHEDULE_TIME, TIMEZONE, APPLE_KEYWORDS, OUTPUT_FORMAT,
    LANGUAGE
)
from models import NewsItem
from fetchers import RSSFeedFetcher, NewsAPIFetcher, TwitterFetcher
from formatter import NewsFormatter
from delivery import EmailDelivery, SlackDelivery, FileDelivery

# Configure logging
os.makedirs("logs", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/apple_news_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AppleNewsAgent:
    """Main agent for monitoring and delivering Apple news"""
    
    def __init__(self):
        """Initialize the news agent with all fetchers and delivery methods"""
        self.fetchers: List = [
            RSSFeedFetcher(RSS_FEEDS),
        ]
        
        if NEWSAPI_KEY:
            self.fetchers.append(NewsAPIFetcher(NEWSAPI_KEY))
            logger.info("NewsAPI fetcher enabled")
        
        if TWITTER_BEARER_TOKEN:
            self.fetchers.append(TwitterFetcher(TWITTER_BEARER_TOKEN))
            logger.info("Twitter fetcher enabled")
        
        # Initialize delivery methods
        self.email_delivery = EmailDelivery(
            sender=EMAIL_SENDER,
            password=EMAIL_PASSWORD,
            smtp_server=SMTP_SERVER,
            smtp_port=SMTP_PORT
        )
        
        self.slack_delivery = SlackDelivery(SLACK_WEBHOOK_URL) if SLACK_WEBHOOK_URL else None
        self.file_delivery = FileDelivery()
        
        logger.info("Apple News Agent initialized")
    
    def fetch_all_news(self) -> List[NewsItem]:
        """Fetch news from all configured sources"""
        logger.info("Fetching news from all sources...")
        all_items = []
        
        for fetcher in self.fetchers:
            try:
                items = fetcher.fetch()
                all_items.extend(items)
                logger.info(f"Fetched {len(items)} items from {fetcher.__class__.__name__}")
            except Exception as e:
                logger.error(f"Error fetching from {fetcher.__class__.__name__}: {e}")
        
        # Filter for Apple relevance
        apple_items = self._filter_apple_news(all_items)
        logger.info(f"Filtered to {len(apple_items)} Apple-relevant items from {len(all_items)} total")
        
        return apple_items
    
    def _filter_apple_news(self, items: List[NewsItem]) -> List[NewsItem]:
        """Filter items for Apple relevance.  Require explicit Apple words to avoid
        generic matches (e.g. "app").
        """
        apple_items = []
        # specific tokens that strongly imply Apple context (not generic product names)
        specific = [
            "apple", "iphone", "ipad", "mac", "macbook", "imac", "airpods",
            "apple tv", "m4 chip", "m3 chip", "a19 chip", "a18 chip",
            "tim cook", "siri", "magsafe", "app store",
            "ipados", "ios 18", "ios 19", "macos", "watchos", "vision pro",
            "icloud", "apple intelligence", "apple music", "apple park"
        ]
        for item in items:
            title_lower = item.title.lower()
            # require specific Apple token in the title itself; ignore mentions
            # buried deeper in the description which often come from generic
            # comparison blurbs.
            if any(tok in title_lower for tok in specific):
                apple_items.append(item)
        return apple_items
    
    def generate_daily_briefing(self, items: List[NewsItem]) -> tuple:
        """
        Generate daily briefing in multiple formats
        
        Returns:
            (markdown, html, json) formatted content. markdown/lang may vary by LANGUAGE.
        """
        if not items:
            logger.warning("No items to generate briefing from")
            return ("No Apple news updates today", "", "")
        
        formatter = NewsFormatter(items)
        
        # support Chinese output
        if LANGUAGE.lower().startswith("zh"):
            markdown = formatter.format_chinese_briefing()
            # minimal HTML version by replacing newlines
            html = markdown.replace("\n", "<br />")
        else:
            markdown = formatter.format_markdown()
            html = formatter.format_html()
        
        json_data = formatter.format_json()
        
        return (markdown, html, json_data)
    
    def run_daily_briefing(self):
        """Execute the daily briefing routine"""
        logger.info("Starting daily briefing generation...")
        
        try:
            # Fetch news
            items = self.fetch_all_news()
            
            if not items:
                logger.warning("No Apple news items found")
                return
            
            # Generate briefing
            markdown, html, json_data = self.generate_daily_briefing(items)
            
            # Deliver via email
            if EMAIL_RECIPIENTS:
                logger.info(f"Sending email to {len(EMAIL_RECIPIENTS)} recipients...")
                subject = "📱 Apple Daily News Brief"
                if LANGUAGE.lower().startswith("zh"):
                    subject = "📅 Apple热点速览"
                self.email_delivery.send(
                    recipients=[r.strip() for r in EMAIL_RECIPIENTS if r.strip()],
                    subject=subject,
                    body_html=html,
                    body_text=markdown
                )
            
            # Save to file
            self.file_delivery.save(markdown, "outputs/apple_news_brief.md")
            
            # Optionally send to Slack
            if self.slack_delivery:
                logger.info("Sending Slack notification...")
                self.slack_delivery.send(markdown[:3000])
            
            logger.info("Daily briefing completed successfully")
        
        except Exception as e:
            logger.error(f"Error during daily briefing: {e}", exc_info=True)
    
    def run_on_schedule(self):
        """Run the agent on a schedule"""
        logger.info(f"Apple News Agent scheduled to run daily at {SCHEDULE_TIME} {TIMEZONE}")
        
        # Schedule daily briefing
        schedule.every().day.at(SCHEDULE_TIME).do(self.run_daily_briefing)
        
        # Also run immediately on startup
        logger.info("Running initial briefing...")
        self.run_daily_briefing()
        
        # Keep scheduler running
        logger.info("Entering scheduler loop...")
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def run_once(self):
        """Run the agent once (for manual execution)"""
        self.run_daily_briefing()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Apple News Monitoring Agent")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (default: run on schedule)"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test mode - fetch news but don't send emails"
    )
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = AppleNewsAgent()
    
    if args.test:
        logger.info("Running in TEST mode - fetching news without sending emails")
        items = agent.fetch_all_news()
        markdown, html, json_data = agent.generate_daily_briefing(items)
        
        # Save test output
        agent.file_delivery.save(markdown, "outputs/test_briefing.md")
        logger.info(f"Test briefing saved to outputs/test_briefing.md ({len(items)} items)")
        return
    
    if args.once:
        agent.run_once()
    else:
        agent.run_on_schedule()

if __name__ == "__main__":
    main()
