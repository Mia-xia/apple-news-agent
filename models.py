# News Item Data Class

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class NewsItem:
    """Represents a single news item about Apple"""
    title: str
    description: str
    source: str  # RSS, NewsAPI, Twitter, etc.
    source_name: str  # MacRumors, 9to5Mac, etc.
    url: str
    publish_date: datetime
    image_url: Optional[str] = None
    author: Optional[str] = None
    sentiment: Optional[str] = "neutral"  # positive, negative, neutral
    relevance_score: float = 1.0  # 0-1 score for Apple relevance
    is_official: bool = False  # From official Apple sources
    is_rumor: bool = False
    
    def __hash__(self):
        return hash(self.url)
    
    def __eq__(self, other):
        if isinstance(other, NewsItem):
            return self.url == other.url
        return False
