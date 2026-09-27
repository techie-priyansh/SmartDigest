from datetime import datetime, timedelta, timezone

import feedparser
import requests


def fetch_recent_articles(
    feed_url: str,
    lookback_hours: int = 24,
) -> list[dict]:
    """
    Fetch recent articles from an RSS feed.

    Parameters
    ----------
    feed_url : str
        RSS feed URL.
    lookback_hours : int
        Only return articles published within this window.

    Returns
    -------
    list[dict]
        Recent articles with title, URL, published time, and source.
    """

    response = requests.get(
        feed_url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=20,
    )

    response.raise_for_status()

    feed = feedparser.parse(response.content)

    cutoff = datetime.now(timezone.utc) - timedelta(
        hours=lookback_hours
    )

    articles = []

    for entry in feed.entries:

        published_at = None

        if getattr(entry, "published_parsed", None):
            published_at = datetime(
                *entry.published_parsed[:6],
                tzinfo=timezone.utc,
            )

        elif getattr(entry, "updated_parsed", None):
            published_at = datetime(
                *entry.updated_parsed[:6],
                tzinfo=timezone.utc,
            )

        if published_at is None:
            continue

        if published_at < cutoff:
            continue

        articles.append(
            {
                "title": entry.get("title", "").strip(),
                "url": entry.get("link", "").strip(),
                "published_at": published_at,
                "source": feed.feed.get(
                    "title",
                    "Unknown",
                ),
            }
        )

    return articles