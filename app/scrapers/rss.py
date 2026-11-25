from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import feedparser
import requests


# Query parameters that only track clicks and never change the page.
TRACKING_PARAMS = {
    "fbclid",
    "gclid",
    "ref",
    "at_medium",
    "at_campaign",
    "at_custom1",
    "at_custom2",
    "at_custom3",
    "at_custom4",
}


def normalize_url(url: str) -> str:
    """
    Strip tracking parameters and fragments so the same article
    always maps to the same URL.
    """

    parts = urlsplit(url.strip())

    query = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if not key.lower().startswith("utm_")
        and key.lower() not in TRACKING_PARAMS
    ]

    return urlunsplit(
        (
            parts.scheme,
            parts.netloc.lower(),
            parts.path,
            urlencode(query),
            "",
        )
    )


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
                "url": normalize_url(entry.get("link", "")),
                "published_at": published_at,
                "source": feed.feed.get(
                    "title",
                    "Unknown",
                ),
            }
        )

    return articles