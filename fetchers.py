# News Fetchers for various sources

import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Optional
from abc import ABC, abstractmethod
from models import NewsItem
import logging

logger = logging.getLogger(__name__)

class NewsFetcher(ABC):
    """Base class for news fetchers"""
    
    @abstractmethod
    def fetch(self) -> List[NewsItem]:
        """Fetch news items"""
        pass

class RSSFeedFetcher(NewsFetcher):
    """Fetches news from RSS feeds"""
    
    def __init__(self, feeds: dict):
        """
        Args:
            feeds: Dictionary of {source_name: rss_url}
        """
        self.feeds = feeds
    
    def fetch(self) -> List[NewsItem]:
        """Fetch all RSS feeds and return news items"""
        items = []
        
        for source_name, feed_url in self.feeds.items():
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:10]:  # Limit to last 10 from each feed
                    try:
                        # Extract fields
                        title = entry.get("title", "No Title")
                        description = entry.get("summary", "")
                        url = entry.get("link", "")
                        
                        # Parse publish date
                        pub_date = None
                        if hasattr(entry, "published_parsed") and entry.published_parsed:
                            pub_date = datetime(*entry.published_parsed[:6])
                        else:
                            pub_date = datetime.now()
                        
                        # Skip old entries (older than 7 days)
                        if datetime.now() - pub_date > timedelta(days=7):
                            continue
                        
                        image_url = None
                        if "media_content" in entry:
                            image_url = entry.media_content[0].get("url")
                        
                        # Check if from official Apple source
                        is_official = "apple.com" in url.lower() or "newsroom" in source_name.lower()
                        is_rumor = any(word in title.lower() for word in ["rumor", "leak", "report"])
                        
                        item = NewsItem(
                            title=title,
                            description=description,
                            source="RSS",
                            source_name=source_name,
                            url=url,
                            publish_date=pub_date,
                            image_url=image_url,
                            is_official=is_official,
                            is_rumor=is_rumor,
                            relevance_score=1.0
                        )
                        items.append(item)
                        
                    except Exception as e:
                        logger.warning(f"Error parsing RSS entry from {source_name}: {e}")
                        continue
            
            except Exception as e:
                logger.error(f"Error fetching RSS from {source_name} ({feed_url}): {e}")
                continue
        
        return items

class NewsAPIFetcher(NewsFetcher):
    """Fetches news from NewsAPI.org"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2/everything"
    
    def fetch(self) -> List[NewsItem]:
        """Fetch news from NewsAPI"""
        if not self.api_key:
            logger.warning("NewsAPI key not configured")
            return []
        
        items = []
        
        # Search for Apple news
        params = {
            "q": "Apple iPhone iPad Mac",
            "sortBy": "publishedAt",
            "language": "en",
            "apiKey": self.api_key,
            "pageSize": 50,
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "ok":
                logger.error(f"NewsAPI error: {data.get('message')}")
                return items
            
            for article in data.get("articles", [])[:30]:
                try:
                    # Parse publish date
                    pub_date_str = article.get("publishedAt", "")
                    pub_date = datetime.fromisoformat(pub_date_str.replace("Z", "+00:00"))
                    
                    is_rumor = any(word in article.get("title", "").lower() 
                                 for word in ["rumor", "leak", "report", "claim"])
                    
                    item = NewsItem(
                        title=article.get("title", ""),
                        description=article.get("description", ""),
                        source="NewsAPI",
                        source_name=article.get("source", {}).get("name", "Unknown"),
                        url=article.get("url", ""),
                        publish_date=pub_date,
                        image_url=article.get("urlToImage"),
                        author=article.get("author"),
                        is_rumor=is_rumor,
                        relevance_score=1.0
                    )
                    items.append(item)
                
                except Exception as e:
                    logger.warning(f"Error parsing NewsAPI article: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error fetching from NewsAPI: {e}")
        
        return items

class TwitterFetcher(NewsFetcher):
    """Fetches trending tweets about Apple"""
    
    def __init__(self, bearer_token: str):
        self.bearer_token = bearer_token
        self.base_url = "https://api.twitter.com/2"
    
    def fetch(self) -> List[NewsItem]:
        """Fetch tweets about Apple (requires API v2 access)"""
        if not self.bearer_token:
            logger.warning("Twitter bearer token not configured")
            return []
        
        items = []
        
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "User-Agent": "Apple News Agent"
        }
        
        # Query for Apple-related tweets
        query = "(Apple OR iPhone OR iPad OR MacBook) lang:en -is:retweet"
        
        params = {
            "query": query,
            "max_results": 100,
            "tweet.fields": "public_metrics,created_at,author_id",
            "expansions": "author_id",
            "user.fields": "username,verified,followers_count"
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/tweets/search/recent",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            if "data" not in data:
                return items
            
            # Build user map
            users = {user["id"]: user for user in data.get("includes", {}).get("users", [])}
            
            for tweet in data["data"][:20]:
                try:
                    pub_date = datetime.fromisoformat(tweet["created_at"].replace("Z", "+00:00"))
                    author_id = tweet.get("author_id")
                    author = users.get(author_id, {}).get("username", "Unknown")
                    
                    # Filter by engagement (high likes/retweets)
                    metrics = tweet.get("public_metrics", {})
                    engagement = metrics.get("like_count", 0) + metrics.get("retweet_count", 0)
                    
                    if engagement < 10:  # Minimum engagement threshold
                        continue
                    
                    item = NewsItem(
                        title=tweet["text"][:100] + "..." if len(tweet["text"]) > 100 else tweet["text"],
                        description=tweet["text"],
                        source="Twitter",
                        source_name=f"@{author}",
                        url=f"https://twitter.com/{author}/status/{tweet['id']}",
                        publish_date=pub_date,
                        author=author,
                        is_official=users.get(author_id, {}).get("verified", False),
                        relevance_score=min(engagement / 1000, 1.0)  # Normalize by 1000
                    )
                    items.append(item)
                
                except Exception as e:
                    logger.warning(f"Error parsing tweet: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error fetching from Twitter API: {e}")
        
        return items
