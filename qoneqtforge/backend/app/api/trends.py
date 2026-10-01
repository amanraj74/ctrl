"""Trends API — fetch trending topics from various free sources."""

from __future__ import annotations

import logging
from typing import Literal

import httpx
from fastapi import APIRouter, Query

from app.schemas import TrendItem

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/trends", tags=["trends"])


async def _fetch_hackernews() -> list[TrendItem]:
    """Fetch top stories from Hacker News."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get("https://hacker-news.firebaseio.com/v0/topstories.json")
            story_ids = resp.json()[:10]

            trends = []
            for story_id in story_ids[:8]:
                detail = await client.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json")
                data = detail.json()
                if data and data.get("title"):
                    trends.append(TrendItem(
                        title=data["title"],
                        source="hackernews",
                        url=data.get("url"),
                        score=data.get("score"),
                    ))
            return trends
    except Exception as e:
        logger.warning("HackerNews fetch failed: %s", e)
        return []


async def _fetch_reddit(subreddit: str = "technology") -> list[TrendItem]:
    """Fetch trending posts from a Reddit subreddit."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            headers = {"User-Agent": "QoneqtForge/1.0"}
            resp = await client.get(
                f"https://www.reddit.com/r/{subreddit}/hot.json?limit=8",
                headers=headers,
            )
            data = resp.json()

            trends = []
            for post in data.get("data", {}).get("children", []):
                p = post.get("data", {})
                if p.get("title") and not p.get("stickied"):
                    trends.append(TrendItem(
                        title=p["title"],
                        source=f"reddit/{subreddit}",
                        url=f"https://reddit.com{p.get('permalink', '')}",
                        score=p.get("score"),
                    ))
            return trends
    except Exception as e:
        logger.warning("Reddit fetch failed: %s", e)
        return []


# Fallback trending topics
FALLBACK_TRENDS = [
    TrendItem(title="AI is transforming how students learn in 2026", source="curated"),
    TrendItem(title="The rise of community-driven social platforms", source="curated"),
    TrendItem(title="Why startups are choosing India for their HQ", source="curated"),
    TrendItem(title="5 morning habits that boost productivity", source="curated"),
    TrendItem(title="The future of remote work after 2025", source="curated"),
    TrendItem(title="How open source is changing the tech industry", source="curated"),
    TrendItem(title="Mental health awareness in the workplace", source="curated"),
    TrendItem(title="The fastest growing programming languages in 2026", source="curated"),
]


@router.get("", response_model=list[TrendItem])
async def get_trends(
    source: Literal["hn", "reddit", "all"] = Query(default="all", description="Trend source"),
):
    """Fetch trending topics from various free sources."""
    trends = []

    if source in ("hn", "all"):
        trends.extend(await _fetch_hackernews())

    if source in ("reddit", "all"):
        trends.extend(await _fetch_reddit())

    # Add fallback trends if we got nothing
    if not trends:
        trends = FALLBACK_TRENDS

    return trends[:15]
