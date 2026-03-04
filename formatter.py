# News Formatting and Output

from typing import List, Dict
from models import NewsItem
from datetime import datetime
import json
from collections import defaultdict
import requests
import urllib.parse
import re
import textwrap
import math

class NewsFormatter:
    """Formats news items for different output types"""
    
    def __init__(self, items: List[NewsItem]):
        self.items = items
        self.deduplicate()
        self.sort_by_relevance()
    
    def deduplicate(self):
        """Remove duplicate items by URL"""
        seen_urls = set()
        unique_items = []
        for item in self.items:
            if item.url not in seen_urls:
                unique_items.append(item)
                seen_urls.add(item.url)
        self.items = unique_items
    
    def sort_by_relevance(self):
        """Sort items by relevance score and publish date"""
        self.items.sort(
            key=lambda x: (-x.relevance_score, -x.publish_date.timestamp())
        )
    
    def get_top_items(self, limit: int = 7) -> List[NewsItem]:
        """Get top N items"""
        return self.items[:limit]
    
    def group_by_category(self) -> Dict[str, List[NewsItem]]:
        """Group news items by category"""
        categories = defaultdict(list)
        
        for item in self.items:
            category = self._categorize_item(item)
            categories[category].append(item)
        
        return categories
    
    def _categorize_item(self, item: NewsItem) -> str:
        """Categorize a news item"""
        title = item.title.lower()
        description = (item.description or "").lower()
        full_text = f"{title} {description}"
        
        category_keywords = {
            "Product Launch": ["launch", "announce", "reveal", "introduced", "new"],
            "Software Updates": ["update", "ios", "macos", "ipados", "tvos", "watchos", "release"],
            "AI & Machine Learning": ["apple intelligence", "ai", "machine learning", "neural"],
            "Supply Chain": ["supply", "production", "factory", "manufacturing"],
            "Financial": ["earnings", "revenue", "profit", "stock", "quarter", "fiscal"],
            "Regulation": ["regulatory", "law", "government", "legal", "doj", "ftc"],
            "Partnerships": ["partnership", "collaboration", "partner", "deal"],
            "Rumors & Leaks": ["rumor", "leak", "report", "expected", "upcoming"],
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in full_text for keyword in keywords):
                return category
        
        return "Other News"
    
    def format_markdown(self) -> str:
        """Format as Markdown for email/messaging"""
        output = []
        output.append("# Apple Daily News Brief\n")
        output.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}*\n")
        
        # Get top items
        top_items = self.get_top_items(7)
        
        if not top_items:
            output.append("No significant Apple news updates today.\n")
            return "\n".join(output)
        
        output.append("## 📰 Top Updates\n")
        
        for i, item in enumerate(top_items, 1):
            output.append(f"### {i}. {item.title}\n")
            
            # Badge indicators
            badges = []
            if item.is_official:
                badges.append("🔵 Official")
            if item.is_rumor:
                badges.append("⚠️ Rumor/Leak")
            if badges:
                output.append(f"{' | '.join(badges)}\n")
            
            # Source and date
            output.append(f"**Source:** {item.source_name} ({item.source}) | **Date:** {item.publish_date.strftime('%Y-%m-%d %H:%M')}\n")
            
            # Description
            output.append(f"{item.description}\n")
            
            # Why it matters
            output.append("\n📌 **Why it matters:**\n")
            output.append(self._generate_impact_summary(item))
            output.append("\n")
            
            # Link
            output.append(f"[**Read More →**]({item.url})\n")
            output.append("---\n")
        
        # Trending topics section
        output.append("\n## 🔥 Trending Topics\n\n")
        
        categories = self.group_by_category()
        for category, items in list(categories.items())[:5]:
            count = len(items)
            output.append(f"**{category}** ({count} items)\n")
        
        output.append("\n## 📊 Daily Stats\n\n")
        output.append(f"- **Total Articles:** {len(self.items)}\n")
        output.append(f"- **Official Apple News:** {sum(1 for item in self.items if item.is_official)}\n")
        output.append(f"- **Rumors/Leaks:** {sum(1 for item in self.items if item.is_rumor)}\n")
        output.append(f"- **Sources Monitored:** {len(set(item.source_name for item in self.items))}\n")
        
        output.append("\n---\n")
        output.append("*This brief was automatically generated by the Apple News Monitoring Agent.*\n")
        output.append("*To configure email preferences or news sources, edit the configuration file.*\n")
        
        return "\n".join(output)
    
    def format_html(self) -> str:
        """Format as HTML for email"""
        html = ["<html><body style='font-family: Arial, sans-serif; line-height: 1.6; color: #333;'>"]
        
        html.append("<h1>📱 Apple Daily News Brief</h1>")
        html.append(f"<p><em>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</em></p>")
        
        top_items = self.get_top_items(7)
        
        if not top_items:
            html.append("<p>No significant Apple news updates today.</p>")
            html.append("</body></html>")
            return "\n".join(html)
        
        html.append("<h2>📰 Top Updates</h2>")
        
        for i, item in enumerate(top_items, 1):
            html.append(f"<div style='border-left: 4px solid #555; padding: 15px; margin: 15px 0; background: #f9f9f9;'>")
            html.append(f"<h3 style='margin-top: 0;'>{i}. {item.title}</h3>")
            
            if item.image_url:
                html.append(f"<img src='{item.image_url}' style='max-width: 100%; height: auto; margin: 10px 0;' />")
            
            badges = []
            if item.is_official:
                badges.append("<span style='background: #007AFF; color: white; padding: 3px 8px; border-radius: 3px; margin-right: 5px;'>🔵 Official</span>")
            if item.is_rumor:
                badges.append("<span style='background: #FF9500; color: white; padding: 3px 8px; border-radius: 3px; margin-right: 5px;'>⚠️ Rumor</span>")
            if badges:
                html.append(f"<p>{' '.join(badges)}</p>")
            
            html.append(f"<p><strong>Source:</strong> {item.source_name} ({item.source}) | <strong>Date:</strong> {item.publish_date.strftime('%Y-%m-%d %H:%M')}</p>")
            html.append(f"<p>{item.description}</p>")
            
            html.append(f"<p><strong>📌 Why it matters:</strong></p>")
            html.append(f"<p>{self._generate_impact_summary(item)}</p>")
            
            html.append(f"<p><a href='{item.url}' style='color: #007AFF; text-decoration: none;'><strong>Read More →</strong></a></p>")
            html.append("</div>")
        
        html.append("</body></html>")
        return "\n".join(html)
    
    def format_json(self) -> str:
        """Format as JSON for integration with other systems"""
        top_items = self.get_top_items()
        
        json_data = {
            "timestamp": datetime.now().isoformat(),
            "total_items": len(self.items),
            "top_items": [
                {
                    "title": item.title,
                    "description": item.description,
                    "source": item.source,
                    "source_name": item.source_name,
                    "url": item.url,
                    "publish_date": item.publish_date.isoformat(),
                    "author": item.author,
                    "image_url": item.image_url,
                    "is_official": item.is_official,
                    "is_rumor": item.is_rumor,
                    "relevance_score": item.relevance_score,
                }
                for item in top_items
            ]
        }
        
        return json.dumps(json_data, indent=2)
    
    def _generate_impact_summary(self, item: NewsItem) -> str:
        """Generate impact summary based on item content"""
        title = item.title.lower()
        description = (item.description or "").lower()
        full_text = f"{title} {description}"
        
        if any(word in full_text for word in ["launch", "announce", "reveal"]):
            return "Major product or feature announcement that could impact market position and consumer interest."
        elif any(word in full_text for word in ["ios", "update", "release"]):
            return "Software update affecting user experience and ecosystem. Important for app developers and users."
        elif any(word in full_text for word in ["earnings", "revenue", "profit"]):
            return "Financial performance indicates economic health and investor sentiment about Apple's growth."
        elif any(word in full_text for word in ["ai", "intelligence", "machine learning"]):
            return "AI integration demonstrates Apple's competitive positioning in emerging AI-assisted features."
        elif any(word in full_text for word in ["supply", "production", "factory"]):
            return "Supply chain news affects product availability, pricing, and production capacity."
        elif any(word in full_text for word in ["regulatory", "law", "legal"]):
            return "Regulatory developments could impact App Store policies, privacy features, or business operations."
        elif "rumor" in full_text or "leak" in full_text:
            return "Unconfirmed reports about upcoming products or features. Use as speculative information only."
        else:
            return "Relevant development in Apple's product ecosystem or business operations."

    def _clean_chinese_text(self, text: str) -> str:
        """Remove translator artifacts and enforce complete Chinese prose."""
        if not text:
            return ""

        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\[[^\]]+\]', '', text)
        text = re.sub(r'\([^)]*\)', '', text)
        text = re.sub(r'（[^）]*）', '', text)
        text = re.sub(r'\s+', ' ', text).strip()

        # Remove incomplete or teaser phrasing.
        text = re.sub(r'更多[。…!！?？]*', '', text)
        text = re.sub(r'详情见[。…!！?？]*', '', text)
        text = re.sub(r'点击.*?查看', '', text)
        text = re.sub(r'继续阅读[。…!！?？]*', '', text)
        text = re.sub(r'阅读原文[。…!！?？]*', '', text)
        text = re.sub(r'Read\s*More', '', text, flags=re.IGNORECASE)

        # Normalize frequent Apple product names to Chinese form.
        replacements = [
            (r'Apple\s*Music', '苹果音乐'),
            (r'Apple\s*Newsroom', '苹果新闻编辑部'),
            (r'App\s*Store', '应用商店'),
            (r'Apple\s*Intelligence', '苹果智能'),
        ]
        for pattern, value in replacements:
            text = re.sub(pattern, value, text, flags=re.IGNORECASE)

        # Normalize punctuation.
        text = re.sub(r'\.{2,}', '。', text)
        text = re.sub(r'…{1,}', '。', text)
        text = re.sub(r'[;；]+', '，', text)
        text = re.sub(r'[，,]{2,}', '，', text)
        text = re.sub(r'[。]{2,}', '。', text)
        text = re.sub(r'[，。]\s*[，。]', '。', text)
        text = re.sub(r'^\W+', '', text)
        text = re.sub(r'\W+$', '', text)
        text = re.sub(r'\s+', '', text)

        if text and text[-1] not in "。！？":
            text = f"{text}。"
        return text

    def _is_mostly_english(self, text: str) -> bool:
        letters = len(re.findall(r'[A-Za-z]', text or ''))
        chinese = len(re.findall(r'[\u4e00-\u9fff]', text or ''))
        return letters > max(12, chinese * 2)

    def _localize_terms(self, text: str) -> str:
        if not text:
            return ""
        replacements = [
            (r'Apple\s*Music', '苹果音乐'),
            (r'Apple\s*Intelligence', '苹果智能'),
            (r'Apple\s*Newsroom', '苹果新闻编辑部'),
            (r'App\s*Store', '应用商店'),
            (r'Apple\s*Watch', '苹果手表'),
            (r'AirPods', '苹果耳机'),
            (r'iPhone', 'iPhone'),
            (r'iPad', 'iPad'),
            (r'MacBook', 'MacBook'),
            (r'Mac', 'Mac'),
            (r'Siri', 'Siri'),
            (r'Gurman', '古尔曼'),
            (r'Bloomberg', '彭博社'),
            (r'Reuters', '路透社'),
            (r'market cap', '市值'),
            (r'stock', '股价'),
            (r'shares', '股价'),
            (r'earnings', '财报'),
            (r'revenue', '营收'),
            (r'profit', '利润'),
            (r'shipment[s]?', '出货量'),
            (r'supply chain', '供应链'),
            (r'leak', '爆料'),
            (r'rumor', '传闻'),
            (r'launch', '发布'),
            (r'release', '上线'),
            (r'update', '更新'),
            (r'chip', '芯片'),
        ]
        out = text
        for pattern, value in replacements:
            out = re.sub(pattern, value, out, flags=re.IGNORECASE)
        out = re.sub(r'\bUSD\b', '美元', out, flags=re.IGNORECASE)
        out = re.sub(r'\$', '', out)
        out = re.sub(r'\s+', ' ', out).strip()
        return out

    def _hot_score(self, item: NewsItem) -> float:
        now = datetime.now()
        age_hours = max(0.0, (now - item.publish_date).total_seconds() / 3600)
        recency = max(0.0, 48 - age_hours) / 48 * 4
        base = item.relevance_score * 10 + recency
        if item.is_official:
            base += 1.2
        if item.is_rumor:
            base += 0.8

        text = f"{item.title} {item.description}".lower()
        weights = {
            "stock": 2.8,
            "market cap": 2.8,
            "earnings": 2.6,
            "revenue": 2.6,
            "profit": 2.6,
            "guidance": 2.3,
            "siri": 2.2,
            "apple intelligence": 2.4,
            "ai": 1.8,
            "iphone": 2.2,
            "ipad": 1.8,
            "mac": 1.8,
            "chip": 1.9,
            "shipment": 2.1,
            "supply chain": 2.0,
            "regulator": 2.1,
            "antitrust": 2.4,
            "lawsuit": 2.0,
            "rumor": 1.3,
            "leak": 1.3,
            "gurman": 1.5,
            "bloomberg": 1.2,
        }
        for word, weight in weights.items():
            if word in text:
                base += weight
        return base

    def _get_hot_items(self, limit: int = 7) -> List[NewsItem]:
        ranked = sorted(
            self.items,
            key=lambda x: (self._hot_score(x), x.publish_date.timestamp()),
            reverse=True
        )
        return ranked[:limit]

    def _extract_metrics(self, text: str) -> str:
        if not text:
            return ""
        normalized = text

        def _billion_to_yi(match):
            value = float(match.group(1))
            return f"{int(math.floor(value * 10))}亿美元"

        normalized = re.sub(r'(\d+(?:\.\d+)?)\s*billion', _billion_to_yi, normalized, flags=re.IGNORECASE)
        normalized = re.sub(r'(\d+(?:\.\d+)?)\s*million', r'\1百万', normalized, flags=re.IGNORECASE)

        metrics = []
        metrics.extend(re.findall(r'\d+(?:\.\d+)?%', normalized))
        metrics.extend(re.findall(r'\d+(?:\.\d+)?\s*(?:亿美元|万亿元|万台|亿台|万部|百万)', normalized))
        metrics.extend(re.findall(r'Q[1-4]\s*20\d{2}', normalized, flags=re.IGNORECASE))
        # de-dup while preserving order
        seen = set()
        compact = []
        for m in metrics:
            key = m.lower().strip()
            if key not in seen:
                compact.append(m.strip())
                seen.add(key)
        return "、".join(compact[:3])

    def _localize_source(self, source_name: str) -> str:
        source_map = {
            "Reuters": "路透社",
            "Bloomberg": "彭博社",
            "Wall Street Journal": "华尔街日报",
            "Financial Times": "金融时报",
            "Apple Newsroom": "苹果新闻编辑部",
        }
        return source_map.get(source_name, source_name)

    def _infer_cn_topic(self, text: str) -> str:
        t = text.lower()
        if any(k in t for k in ["stock", "market cap", "shares", "跌", "涨"]):
            return "苹果股价与市值波动"
        if any(k in t for k in ["earnings", "revenue", "profit", "fiscal", "quarter"]):
            return "苹果财报与业绩指引更新"
        if any(k in t for k in ["siri", "apple intelligence", "ai"]):
            return "苹果AI与Siri进展"
        if any(k in t for k in ["supply", "shipment", "production", "inventory", "factory"]):
            return "苹果供应链与出货数据变化"
        if any(k in t for k in ["regulator", "doj", "eu", "antitrust", "lawsuit", "legal"]):
            return "苹果监管与诉讼动态"
        if any(k in t for k in ["iphone", "ipad", "mac", "airpods", "chip", "launch", "release"]):
            return "苹果新品与硬件节奏更新"
        if any(k in t for k in ["music", "streaming", "fraud"]):
            return "苹果音乐平台治理升级"
        if any(k in t for k in ["rumor", "leak", "gurman", "report", "expected"]):
            return "苹果爆料线索升温"
        return "苹果业务出现新动态"

    def _infer_cn_facts(self, item: NewsItem) -> str:
        text = f"{item.title} {item.description}"
        localized = self._localize_terms(text)
        metrics = self._extract_metrics(localized)

        model_hits = re.findall(
            r'(iPhone\s*\d+\w*|iPad\s*\w+|MacBook\s*\w*|Mac\s*\w+|Siri|A\d+|M\d+|C\d+|5G)',
            localized,
            flags=re.IGNORECASE
        )
        model_hits = [m.strip() for m in model_hits][:3]
        model_part = "、".join(model_hits)

        facts = []
        if model_part:
            facts.append(f"涉及{model_part}等核心关键词")
        if metrics:
            facts.append(f"关键指标包含{metrics}")
        if item.source_name:
            facts.append(f"消息来源为{self._localize_source(item.source_name)}")

        if not facts:
            return "事件已进入当日重点追踪清单，后续将继续观察官方披露与市场反馈"
        return "，".join(facts)

    def _translate_if_needed(self, text: str) -> str:
        if not text:
            return ""
        if self._is_mostly_english(text):
            translated = self._translate_to_chinese(text)
            if translated:
                return translated
            return self._localize_terms(text)
        return text

    def _wrap_paragraph(self, text: str) -> str:
        """Force each item into roughly 3-5 display lines."""
        if not text:
            return ""
        length = len(text)
        width = max(24, min(34, round(length / 4)))
        wrapped = textwrap.wrap(text, width=width, break_on_hyphens=False)
        if len(wrapped) < 3:
            width = max(18, round(length / 3))
            wrapped = textwrap.wrap(text, width=width, break_on_hyphens=False)
        elif len(wrapped) > 5:
            width = max(16, round(length / 5) + 1)
            wrapped = textwrap.wrap(text, width=width, break_on_hyphens=False)
        if len(wrapped) >= 2 and re.fullmatch(r'[。！？]+', wrapped[-1]):
            wrapped[-2] = f"{wrapped[-2]}{wrapped[-1]}"
            wrapped.pop()
        return "\n".join(wrapped)

    def _build_cn_paragraph(self, item: NewsItem, index: int) -> str:
        title = self._translate_if_needed((item.title or "").strip())
        desc_raw = re.sub(r'<[^>]+>', '', item.description or "").strip()
        desc = self._translate_if_needed(desc_raw[:320])

        title = self._clean_chinese_text(title)
        desc = self._clean_chinese_text(desc)

        day = item.publish_date.strftime("%-m月%-d日")
        headline = title.rstrip("。！？")
        details = desc.rstrip("。！？")
        has_cn_facts = len(re.findall(r'[\u4e00-\u9fff]', headline + details)) >= 16

        if has_cn_facts:
            style = index % 4
            if style == 0:
                body = f"{day}，{self._make_hashtag(headline)}，{headline}，{details}。"
            elif style == 1:
                body = f"{day}，{self._make_hashtag(headline)}，{headline}成为市场关注焦点，{details}。"
            elif style == 2:
                body = f"{day}最新披露显示，{self._make_hashtag(headline)}，{headline}，{details}。"
            else:
                body = f"{day}，围绕苹果生态的最新进展是{self._make_hashtag(headline)}，{headline}，{details}。"
        else:
            raw = f"{item.title} {item.description}"
            topic = self._infer_cn_topic(raw)
            facts = self._infer_cn_facts(item)
            styles = [
                f"{day}，{self._make_hashtag(topic)}，{topic}在当日信息流中明显升温，{facts}。",
                f"{day}，{self._make_hashtag(topic)}，市场聚焦{topic}，{facts}。",
                f"{day}，{self._make_hashtag(topic)}，围绕{topic}的讨论快速放大，{facts}。",
                f"{day}，{self._make_hashtag(topic)}，苹果线索持续发酵，核心议题指向{topic}，{facts}。",
            ]
            body = styles[index % len(styles)]

        body = self._clean_chinese_text(body)
        body = re.sub(r'(更多|详情见|Read\s*More|点击查看|继续阅读)', '', body, flags=re.IGNORECASE)
        body = re.sub(r'[A-Za-z]{12,}', '', body)
        body = re.sub(r'\s+', '', body)
        return self._wrap_paragraph(body)
    
    def _make_hashtag(self, text: str) -> str:
        """Generate a simple hashtag from Chinese or English text.
        Prefer Chinese characters when available; otherwise use first words.
        """
        import re
        cleaned = re.sub(r'^\d{2,4}年', '', text or '')
        cleaned = re.sub(r'[0-9%％\s]+', '', cleaned)
        # try extract Chinese character sequences
        chs = re.findall(r"[\u4e00-\u9fff]{2,}", cleaned)
        if chs:
            tag = max(chs, key=len)[:10]
            return f"#{tag}#"
        # fallback to english words
        words = [w.strip("#,.!?:;'\\") for w in text.replace("#"," ").split()]
        if not words:
            return "#Apple#"
        tag = ''.join(words[:3])
        return f"#{tag}#"

    def _translate_to_chinese(self, text: str) -> str:
        """Translate English text to Chinese using free API"""
        if not text or not text.strip():
            return ""
        
        text = text[:500]  # Limit to 500 chars to avoid API issues
        
        try:
            # Use Bing Translator API via simple HTTP request
            url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(text)}&langpair=en|zh-CN"
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                result = response.json()
                translated = result.get('responseData', {}).get('translatedText', '')
                return translated if translated else ""
        except Exception as e:
            import logging
            logging.warning(f"Translation failed: {e}")
        
        return ""

    def format_chinese_briefing(self) -> str:
        """Generate paragraph-only Chinese briefing with no bullet lists."""
        date_str = datetime.now().strftime('%-m月%-d日')
        lines = []
        lines.append(f"📅 {date_str} 苹果热点速览 @全体成员\n")
        top_items = self._get_hot_items(7)
        for idx, item in enumerate(top_items, start=1):
            paragraph = self._build_cn_paragraph(item, idx)
            if not paragraph:
                continue
            lines.append(paragraph)
            lines.append("")

        return "\n".join(lines)
