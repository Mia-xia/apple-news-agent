# Advanced Configuration & Extensions

## Custom RSS Feeds

## Chinese Hotspot Briefing

The agent now supports generating a Chinese formatted "Apple热点速览" suitable for internal workgroups. It structures content into two sections:

1. **品牌核心动态** – 2–4 high‑priority updates (stock, AI, new products, supply chain, etc.)
2. **社交飙升话题** – 2–4 trending social posts (Twitter, etc.)

Control the language via `LANGUAGE` in `config.py` or `.env` (default `zh`).


Add your own Apple news sources to `config.py`:

```python
RSS_FEEDS = {
    "MacRumors": "https://feeds.macrumors.com/MacRumors-Front",
    "9to5Mac": "https://9to5mac.com/feed/",
    # Add your custom feeds below:
    "My Apple Blog": "https://example.com/apple-news/feed",
    "Apple Developer": "https://developer.apple.com/news/feed.xml",
}
```

## Custom Keywords

Modify what the agent considers "Apple news":

```python
APPLE_KEYWORDS = [
    # Include existing keywords, add new ones:
    "Tim Cook",
    "Steve Jobs",
    "Apple Park",
    "WWDC",
    "Cupertino",
]
```

## Email Recipients

Add multiple recipients in `.env`:

```
EMAIL_RECIPIENTS=engineer@company.com,manager@company.com,team@company.com
```

Or dynamically in code:

```python
email_delivery.send(
    recipients=["email1@example.com", "email2@example.com"],
    subject="Apple News Brief",
    body_html=html_content
)
```

## Restrict by Time Window

Only show news from the last N hours:

```python
# In agent.py, modify fetch_all_news():
from datetime import datetime, timedelta

def fetch_all_news_recent(self, hours=24) -> List[NewsItem]:
    items = self.fetch_all_news()
    
    cutoff = datetime.now() - timedelta(hours=hours)
    return [item for item in items if item.publish_date > cutoff]
```

## Custom Filtering

Filter by source reliability:

```python
def filter_by_source_reliability(items: List[NewsItem]) -> List[NewsItem]:
    """Only include news from trusted sources"""
    trusted_sources = ["Apple Newsroom", "MacRumors", "9to5Mac"]
    return [item for item in items if item.source_name in trusted_sources]
```

## AI-Powered Summarization (OpenAI)

Add to `config.py`:
```python
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
```

Then enhance `NewsItem`:
```python
def generate_ai_summary(self) -> str:
    """Generate AI summary using OpenAI"""
    import openai
    
    openai.api_key = config.OPENAI_API_KEY
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": f"Summarize this news for a tech executive in 1-2 sentences:\n\n{self.description}"
            }
        ]
    )
    return response.choices[0].message.content
```

## Slack Rich Messages

Enhanced Slack formatting:

```python
def send_rich_slack_briefing(self, slack_delivery, items: List[NewsItem]):
    blocks = []
    
    for i, item in enumerate(items[:7], 1):
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{i}. {item.title}*\n{item.description[:200]}..."
            }
        })
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"📰 {item.source_name} | 🔗 <{item.url}|Read More>"
                }
            ]
        })
    
    slack_delivery.webhook_url = config.SLACK_WEBHOOK_URL
    requests.post(slack_delivery.webhook_url, json={"blocks": blocks})
```

## Database Storage

Store news items for historical analysis:

```python
import sqlite3
from datetime import datetime

class NewsDatabase:
    def __init__(self, db_path="apple_news.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_table()
    
    def create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS news_items (
                id INTEGER PRIMARY KEY,
                title TEXT,
                url TEXT UNIQUE,
                source TEXT,
                publish_date TIMESTAMP,
                fetch_date TIMESTAMP,
                is_official BOOLEAN,
                is_rumor BOOLEAN
            )
        """)
        self.conn.commit()
    
    def save_item(self, item: NewsItem):
        try:
            self.conn.execute("""
                INSERT INTO news_items 
                (title, url, source, publish_date, fetch_date, is_official, is_rumor)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                item.title, item.url, item.source_name,
                item.publish_date, datetime.now(),
                item.is_official, item.is_rumor
            ))
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass  # Item already exists
```

## Rate Limiting

Prevent hammering APIs:

```python
import time
from functools import wraps

def rate_limit(calls_per_second=1):
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

@rate_limit(calls_per_second=0.5)
def fetch_news():
    """Fetch news at max 0.5 calls per second"""
    # Implementation
    pass
```

## Webhook Endpoint

Expose as a local webhook:

```python
from flask import Flask, jsonify

app = Flask(__name__)
agent = AppleNewsAgent()

@app.route('/api/briefing', methods=['GET'])
def get_briefing():
    items = agent.fetch_all_news()
    markdown, html, json_data = agent.generate_daily_briefing(items)
    return jsonify({
        "status": "success",
        "items_count": len(items),
        "briefing_html": html
    })

@app.route('/api/trigger', methods=['POST'])
def trigger_briefing():
    agent.run_daily_briefing()
    return jsonify({"status": "briefing_sent"})

if __name__ == '__main__':
    app.run(port=5000, debug=False)
```

## Performance Monitoring

Add metrics:

```python
import logging
import time

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
    
    def record(self, operation: str, duration: float):
        if operation not in self.metrics:
            self.metrics[operation] = []
        self.metrics[operation].append(duration)
        
        avg_time = sum(self.metrics[operation]) / len(self.metrics[operation])
        logging.info(f"{operation}: {duration:.2f}s (avg: {avg_time:.2f}s)")
    
    def report(self):
        for op, times in self.metrics.items():
            avg = sum(times) / len(times)
            min_t = min(times)
            max_t = max(times)
            print(f"{op}: avg={avg:.2f}s, min={min_t:.2f}s, max={max_t:.2f}s")
```

## Testing Framework

Add tests:

```python
# test_agent.py
import unittest
from agent import AppleNewsAgent
from models import NewsItem

class TestAppleNewsAgent(unittest.TestCase):
    def setUp(self):
        self.agent = AppleNewsAgent()
    
    def test_fetch_returns_list(self):
        items = self.agent.fetch_all_news()
        self.assertIsInstance(items, list)
    
    def test_items_have_required_fields(self):
        items = self.agent.fetch_all_news()
        for item in items:
            self.assertTrue(hasattr(item, 'title'))
            self.assertTrue(hasattr(item, 'url'))
            self.assertTrue(hasattr(item, 'publish_date'))

if __name__ == '__main__':
    unittest.main()
```

## Monitoring Dashboard

Create a simple status page:

```python
# dashboard.py
from datetime import datetime
import json

class DashboardGenerator:
    def __init__(self, agent: AppleNewsAgent):
        self.agent = agent
    
    def generate_html(self):
        items = self.agent.fetch_all_news()
        
        html = """
        <html>
        <head>
            <title>Apple News Agent - Dashboard</title>
            <style>
                body { font-family: Arial; margin: 20px; }
                .stat { display: inline-block; margin: 10px; padding: 10px; 
                        background: #f0f0f0; border-radius: 5px; }
                .stat-value { font-size: 24px; font-weight: bold; color: #007AFF; }
            </style>
        </head>
        <body>
            <h1>📱 Apple News Agent Dashboard</h1>
            <div class="stat">
                <div>Last Updated</div>
                <div class="stat-value">""" + datetime.now().isoformat() + """</div>
            </div>
            <div class="stat">
                <div>Items Today</div>
                <div class="stat-value">""" + str(len(items)) + """</div>
            </div>
        </body>
        </html>
        """
        return html
```

## Custom Notifications

Add desktop notifications (macOS):

```python
import os

def send_notification(title: str, message: str):
    """Send macOS notification"""
    script = f'osascript -e \'display notification "{message}" with title "{title}"\''
    os.system(script)

# Usage
send_notification("Apple News", "New briefing available")
```

---

For more advanced features or custom integrations, refer to the main source files and extend as needed!
