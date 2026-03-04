# Apple News Monitoring Agent Configuration

import os
from dotenv import load_dotenv

load_dotenv()

# API Keys & Credentials
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Email Configuration
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "your-email@company.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_RECIPIENTS = os.getenv("EMAIL_RECIPIENTS", "").split(",")

# Slack Configuration (optional)
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")

# News Source Configuration
RSS_FEEDS = {
    "MacRumors": "https://feeds.macrumors.com/MacRumors-Front",
    "9to5Mac": "https://9to5mac.com/feed/",
    "The Verge": "https://www.theverge.com/apple/rss/index.xml",
    "MacWorld": "https://www.macworld.com/feed",
    "AppleInsider": "https://appleinsider.com/articles/rss",
    "Apple Newsroom": "https://www.apple.com/newsroom/rss/apple_newsroom.rss",
}

# Apple Keywords to Monitor
APPLE_KEYWORDS = [
    "Apple",
    "iPhone",
    "iPad",
    "Mac",
    "macOS",
    "iOS",
    "iPadOS",
    "watchOS",
    "visionOS",
    "Apple Watch",
    "Vision Pro",
    "AirPods",
    "Apple Intelligence",
    "Apple TV",
    "Apple Music",
    "iCloud",
    "App Store",
    "Tim Cook",
    "Craig Federighi",
    "Siri",
    "M-series chip",
    "A-series chip",
]

# Scheduling
SCHEDULE_TIME = "09:00"  # Daily update time (24-hour format)
TIMEZONE = "UTC"

# Output Settings
MAX_ITEMS_PER_SOURCE = 5
MIN_SENTIMENT_SCORE = 0.0  # Include all items
OUTPUT_FORMAT = "markdown"  # Options: "markdown", "html", "json"

# Language for briefings ("en" or "zh")
LANGUAGE = os.getenv("LANGUAGE", "zh")
