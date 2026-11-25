import sys

from app.config.sources import RSS_SOURCES, YOUTUBE_SOURCES
from app.scrapers.rss import fetch_recent_articles
from app.scrapers.youtube import fetch_recent_videos


# Wide window so quiet sources are still reported as reachable.
CHECK_WINDOW_HOURS = 24 * 7


def check_sources() -> int:
    """
    Fetch every configured source and report whether it works.

    Needs no database or API keys. Returns the number of failures.
    """

    failures = 0

    print(f"{'STATUS':<8}{'ITEMS(7d)':<11}SOURCE")
    print("-" * 60)

    for source in RSS_SOURCES:
        try:
            items = fetch_recent_articles(
                feed_url=source["feed_url"],
                lookback_hours=CHECK_WINDOW_HOURS,
            )
            print(f"{'OK':<8}{len(items):<11}RSS     {source['name']}")

        except Exception as error:
            failures += 1
            print(f"{'FAIL':<8}{'-':<11}RSS     {source['name']}: {error}")

    for source in YOUTUBE_SOURCES:
        try:
            items = fetch_recent_videos(
                channel_id=source["channel_id"],
                lookback_hours=CHECK_WINDOW_HOURS,
            )
            print(f"{'OK':<8}{len(items):<11}YouTube {source['name']}")

        except Exception as error:
            failures += 1
            print(f"{'FAIL':<8}{'-':<11}YouTube {source['name']}: {error}")

    total = len(RSS_SOURCES) + len(YOUTUBE_SOURCES)

    print("-" * 60)
    print(f"{total - failures}/{total} sources reachable.")

    return failures


if __name__ == "__main__":
    sys.exit(1 if check_sources() else 0)
