"""Sentiment analysis service using free APIs.

Combines:
- Fear & Greed Index from alternative.me (30%)
- News sentiment from CoinGecko /search/trending (40%)
- Reddit-style sentiment mock (30%)

Returns sentiment score 0-100 and direction: bullish/bearish/neutral.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)

# Weights for final score
WEIGHT_NEWS = 0.40
WEIGHT_FEAR_GREED = 0.30
WEIGHT_REDDIT = 0.30

TIMEOUT_SECONDS = 10


@dataclass
class SentimentResult:
    score: int  # 0-100
    components: dict[str, int]  # news, reddit, fear_greed each 0-100
    signal: str  # "bullish" | "bearish" | "neutral"


def _classify(score: int) -> str:
    if score >= 60:
        return "bullish"
    if score <= 40:
        return "bearish"
    return "neutral"


async def _fetch_fear_greed() -> int:
    """Fetch Fear & Greed Index from alternative.me (0=extreme fear, 100=extreme greed)."""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            resp = await client.get("https://api.alternative.me/fng/")
            resp.raise_for_status()
            data = resp.json()
            # data = {"data": [{"value": "72", ...}]}
            items = data.get("data", [])
            if items:
                return int(items[0].get("value", 50))
    except Exception as exc:
        logger.warning("Fear & Greed fetch failed: %s", exc)
    return 50  # neutral fallback


async def _fetch_news_sentiment() -> int:
    """Fetch trending coins from CoinGecko as a proxy for news sentiment."""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            resp = await client.get(
                "https://api.coingecko.com/api/v3/search/trending"
            )
            resp.raise_for_status()
            data = resp.json()
            # Heuristic: trending coins imply positive market interest
            # Use coin list size as a weak positive signal (0-100 scale)
            coins = data.get("coins", [])
            # Normalize: 0 coins = 30 (fear), 20+ coins = 80 (greed)
            count = len(coins)
            return min(80, max(20, 20 + count * 3))
    except Exception as exc:
        logger.warning("CoinGecko news fetch failed: %s", exc)
    return 50  # neutral fallback


def _analyze_reddit_sentiment() -> int:
    """Analyze Reddit sentiment using VADER on crypto subreddit post titles.
    
    Fetches hot posts from r/Bitcoin and r/CryptoCurrency via Reddit JSON API
    (no auth required for public subreddits) and applies VADER sentiment.
    Returns score 0-100 (higher = more bullish).
    """
    import os
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    from nltk.sentiment import SentimentIntensityAnalyzer
    
    sia = SentimentIntensityAnalyzer()
    
    # Fetch from Reddit JSON API (public, no auth needed)
    # Get post titles from crypto subreddits
    titles = []
    try:
        import json
        import urllib.request
        
        subreddits = ["Bitcoin", "CryptoCurrency", "cryptocurrency"]
        for sub in subreddits:
            url = f"https://www.reddit.com/r/{sub}/hot.json?limit=5"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as response:
                data = json.loads(response.read().decode())
                posts = data.get("data", {}).get("children", [])
                for post in posts:
                    title = post.get("data", {}).get("title", "")
                    if title:
                        titles.append(title)
    except Exception as exc:
        logger.warning("Reddit fetch failed: %s", exc)
        return 50  # neutral fallback
    
    if not titles:
        return 50
    
    # Analyze each title with VADER
    compound_scores = []
    for title in titles:
        scores = sia.polarity_scores(title)
        compound_scores.append(scores["compound"])
    
    # Average compound score (-1 to +1) -> convert to 0-100
    avg_compound = sum(compound_scores) / len(compound_scores)
    # Map: -1 -> 0, 0 -> 50, +1 -> 100
    sentiment_score = int((avg_compound + 1) * 50)
    return max(0, min(100, sentiment_score))


async def get_market_sentiment() -> SentimentResult:
    """Fetch all sentiment sources in parallel and combine into final score."""
    reddit_score = await asyncio.to_thread(_analyze_reddit_sentiment)
    fear_greed_score, news_score = await asyncio.gather(
        _fetch_fear_greed(),
        _fetch_news_sentiment(),
    )

    # Combine weighted scores
    final_score = int(
        news_score * WEIGHT_NEWS
        + fear_greed_score * WEIGHT_FEAR_GREED
        + reddit_score * WEIGHT_REDDIT
    )
    final_score = max(0, min(100, final_score))

    return SentimentResult(
        score=final_score,
        components={
            "news": news_score,
            "reddit": reddit_score,
            "fear_greed": fear_greed_score,
        },
        signal=_classify(final_score),
    )
