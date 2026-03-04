# Apple News Agent - API Documentation

This document describes how to extend and integrate the Apple News Agent with other systems.

## Python API

### AppleNewsAgent Class

```python
from agent import AppleNewsAgent

# Initialize
agent = AppleNewsAgent()

# Fetch all news items
items = agent.fetch_all_news()

# Type: List[NewsItem]
# Returns: List of news items from all configured sources
```

### NewsItem Class

```python
from models import NewsItem
from datetime import datetime

item = NewsItem(
    title="Apple Launches iPhone 17",
    description="Apple announces the new iPhone 17 with M4 chip",
    source="RSS",
    source_name="9to5Mac",
    url="https://9to5mac.com/...",
    publish_date=datetime.now(),
    image_url="https://example.com/image.jpg",
    author="John Doe",
    sentiment="positive",
    relevance_score=1.0,
    is_official=False,
    is_rumor=False
)

# Access properties
print(item.title)           # "Apple Launches iPhone 17"
print(item.publish_date)   # datetime object
print(item.is_rumor)       # False
```

### NewsFormatter Class

```python
from formatter import NewsFormatter
from models import NewsItem

# Create formatter with items
formatter = NewsFormatter(items_list)

# Get top items
top_5 = formatter.get_top_items(5)

# Get as different formats
markdown = formatter.format_markdown()
html = formatter.format_html()
json_str = formatter.format_json()

# Group by category
categories = formatter.group_by_category()
# Returns: {
#   "Product Launch": [item1, item2],
#   "Software Updates": [item3],
#   ...
# }
```

### EmailDelivery Class

```python
from delivery import EmailDelivery

delivery = EmailDelivery(
    sender="your-email@gmail.com",
    password="app_password",
    smtp_server="smtp.gmail.com",
    smtp_port=587
)

# Send email
success = delivery.send(
    recipients=["person1@example.com", "person2@example.com"],
    subject="Apple Daily News Brief",
    body_html="<html>...</html>",
    body_text="Plain text version"
)

# Returns: True if successful, False otherwise
```

### SlackDelivery Class

```python
from delivery import SlackDelivery

delivery = SlackDelivery(webhook_url="https://hooks.slack.com/...")

# Send to Slack
success = delivery.send(
    content="Your message here",
    title="Apple News Brief"
)
```

### NewsFetcher Classes

```python
from fetchers import RSSFeedFetcher, NewsAPIFetcher, TwitterFetcher

# RSS Fetcher
rss_fetcher = RSSFeedFetcher({
    "MacRumors": "https://feeds.macrumors.com/MacRumors-Front",
    "9to5Mac": "https://9to5mac.com/feed/"
})
items = rss_fetcher.fetch()

# NewsAPI Fetcher
newsapi_fetcher = NewsAPIFetcher(api_key="your_key")
items = newsapi_fetcher.fetch()

# Twitter Fetcher
twitter_fetcher = TwitterFetcher(bearer_token="your_token")
items = twitter_fetcher.fetch()
```

## Integration Examples

### With External Scheduling (APScheduler)

```python
from apscheduler.schedulers.background import BackgroundScheduler
from agent import AppleNewsAgent

scheduler = BackgroundScheduler()
agent = AppleNewsAgent()

def daily_task():
    agent.run_daily_briefing()

# Schedule for 9 AM every day
scheduler.add_job(
    daily_task,
    'cron',
    hour=9,
    minute=0,
    timezone='UTC'
)

scheduler.start()

# Keep running
try:
    while True:
        pass
except KeyboardInterrupt:
    scheduler.shutdown()
```

### With FastAPI Web Service

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from agent import AppleNewsAgent

app = FastAPI()
agent = AppleNewsAgent()

@app.get("/api/news/latest")
async def get_latest_news(limit: int = 10):
    """Get latest Apple news"""
    items = agent.fetch_all_news()
    return {
        "total": len(items),
        "items": [
            {
                "title": item.title,
                "url": item.url,
                "source": item.source_name,
                "date": item.publish_date.isoformat(),
                "is_official": item.is_official,
                "is_rumor": item.is_rumor
            }
            for item in items[:limit]
        ]
    }

@app.get("/api/news/briefing")
async def get_briefing():
    """Get formatted daily briefing"""
    items = agent.fetch_all_news()
    markdown, html, json_data = agent.generate_daily_briefing(items)
    
    return {
        "format": "html",
        "content": html
    }

# Run: uvicorn filename:app --reload
```

### With Discord Webhook

```python
import requests
from formatter import NewsFormatter

def send_discord_notification(webhook_url: str, items: list):
    """Send Apple news to Discord channel"""
    
    formatter = NewsFormatter(items)
    top_items = formatter.get_top_items(5)
    
    embeds = []
    for item in top_items:
        embed = {
            "title": item.title,
            "description": item.description[:200],
            "url": item.url,
            "color": 0x007AFF if item.is_official else 0xFF9500 if item.is_rumor else 0x34C759,
            "timestamp": item.publish_date.isoformat(),
            "footer": {
                "text": f"{item.source_name} ({item.source})"
            }
        }
        embeds.append(embed)
    
    payload = {
        "embeds": embeds
    }
    
    response = requests.post(webhook_url, json=payload)
    return response.status_code == 204
```

### With Database (SQLAlchemy)

```python
from sqlalchemy import create_engine, Column, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class NewsEntry(Base):
    __tablename__ = "news_items"
    
    url = Column(String, primary_key=True)
    title = Column(String)
    source = Column(String)
    publish_date = Column(DateTime)
    fetch_date = Column(DateTime, default=datetime.now)
    is_official = Column(Boolean)
    is_rumor = Column(Boolean)

# Setup
engine = create_engine('sqlite:///apple_news.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def save_items(items: list):
    """Save news items to database"""
    session = Session()
    
    for item in items:
        # Check if already exists
        existing = session.query(NewsEntry).filter_by(url=item.url).first()
        if not existing:
            entry = NewsEntry(
                url=item.url,
                title=item.title,
                source=item.source_name,
                publish_date=item.publish_date,
                is_official=item.is_official,
                is_rumor=item.is_rumor
            )
            session.add(entry)
    
    session.commit()
    session.close()
```

### With Telegram Bot

```python
import logging
from telegram import Bot
from telegram.error import TelegramError
from formatter import NewsFormatter

async def send_telegram_briefing(bot_token: str, chat_id: str, items: list):
    """Send briefing to Telegram"""
    
    bot = Bot(token=bot_token)
    formatter = NewsFormatter(items)
    top_items = formatter.get_top_items(5)
    
    message = "📱 Apple Daily News\n\n"
    
    for i, item in enumerate(top_items, 1):
        emoji = "🔵" if item.is_official else "⚠️" if item.is_rumor else "📰"
        message += f"{emoji} {i}. {item.title}\n"
        message += f"🔗 {item.url}\n\n"
    
    try:
        await bot.send_message(chat_id=chat_id, text=message)
        return True
    except TelegramError as e:
        logging.error(f"Telegram error: {e}")
        return False
```

## Configuration via Environment Variables

All configuration can be set via environment variables:

```bash
export NEWSAPI_KEY="your_key"
export TWITTER_BEARER_TOKEN="your_token"
export EMAIL_SENDER="email@example.com"
export EMAIL_PASSWORD="password"
export EMAIL_RECIPIENTS="person1@example.com,person2@example.com"
export SLACK_WEBHOOK_URL="https://hooks.slack.com/..."
export SCHEDULE_TIME="09:00"
export TIMEZONE="UTC"
```

## Error Handling

```python
from agent import AppleNewsAgent
import logging

logging.basicConfig(level=logging.DEBUG)

agent = AppleNewsAgent()

try:
    items = agent.fetch_all_news()
except Exception as e:
    logging.error(f"Failed to fetch news: {e}")
    # Handle error appropriately
```

## Performance Considerations

### Timeout Examples

```python
# Fetching with timeout
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Fetch operation timed out")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(30)  # 30 second timeout

try:
    items = agent.fetch_all_news()
finally:
    signal.alarm(0)  # Cancel alarm
```

### Caching Results

```python
import pickle
import os
from datetime import datetime, timedelta

class NewsCache:
    def __init__(self, cache_file="news_cache.pkl", ttl_hours=4):
        self.cache_file = cache_file
        self.ttl = timedelta(hours=ttl_hours)
    
    def get(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'rb') as f:
                data = pickle.load(f)
                if datetime.now() - data['timestamp'] < self.ttl:
                    return data['items']
        return None
    
    def set(self, items):
        with open(self.cache_file, 'wb') as f:
            pickle.dump({
                'timestamp': datetime.now(),
                'items': items
            }, f)

# Usage
cache = NewsCache()
items = cache.get()
if items is None:
    items = agent.fetch_all_news()
    cache.set(items)
```

---

For more examples and advanced integrations, see [ADVANCED.md](ADVANCED.md)
