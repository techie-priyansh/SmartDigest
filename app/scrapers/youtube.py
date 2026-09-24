from datetime import datetime, timedelta, timezone

import feedparser
import requests

from youtube_transcript_api import YouTubeTranscriptApi


def fetch_recent_videos(channel_id: str, lookback_hours: int = 24) -> list[dict]:
    """
    Fetch recent videos from a YouTube channel using its RSS feed.

    Parameters
    ----------
    channel_id : str
        YouTube channel ID.
    lookback_hours : int
        Number of hours to look back from the current UTC time.

    Returns
    -------
    list[dict]
        Recent video metadata.
    """
    rss_url = (
        f"https://www.youtube.com/feeds/videos.xml"
        f"?channel_id={channel_id}"
    )

    response = requests.get(
        rss_url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=20,
    )

    response.raise_for_status()

    feed = feedparser.parse(response.content)

    cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)

    videos = []

    for entry in feed.entries:
        published_at = datetime.fromisoformat(entry.published)

        if published_at < cutoff:
            continue

        if "/shorts/" in entry.link:
            continue

        videos.append(
            {
                "video_id": entry.yt_videoid,
                "title": entry.title,
                "published_at": published_at,
                "url": entry.link,
            }
        )

    return videos


def fetch_transcript(video_id: str) -> str:
    """
    Fetch a YouTube video's transcript and return it as clean text.
    """
    api = YouTubeTranscriptApi()

    try:
        transcript = api.fetch(video_id)

        clean_text = " ".join(
            snippet.text.strip()
            for snippet in transcript
            if snippet.text.strip()
        )

        if not clean_text:
            raise ValueError("Transcript is empty.")

        return clean_text

    except Exception as e:
        raise RuntimeError(
            f"Failed to fetch transcript for video '{video_id}': {e}"
        ) from e