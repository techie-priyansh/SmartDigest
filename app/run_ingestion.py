from app.config.sources import RSS_SOURCES, YOUTUBE_SOURCES
from app.ingestion import ingest_youtube_channel
from app.ingestion_rss import ingest_rss_feed


def run_ingestion(lookback_hours: int = 24) -> None:
    """
    Run ingestion for all configured sources.
    """

    print("=" * 60)
    print("SMARTDIGEST INGESTION")
    print("=" * 60)

    # ---------------------------------------------------------
    # YouTube sources
    # ---------------------------------------------------------

    for source in YOUTUBE_SOURCES:
        print("\n" + "-" * 60)
        print(f"YouTube source: {source['name']}")
        print("-" * 60)

        try:
            ingest_youtube_channel(
                channel_id=source["channel_id"],
                lookback_hours=lookback_hours,
            )

        except Exception as error:
            print(
                f"Failed to process "
                f"{source['name']}: {error}"
            )

    # ---------------------------------------------------------
    # RSS sources
    # ---------------------------------------------------------

    for source in RSS_SOURCES:
        print("\n" + "-" * 60)
        print(f"RSS source: {source['name']}")
        print("-" * 60)

        try:
            ingest_rss_feed(
                feed_url=source["feed_url"],
                lookback_hours=lookback_hours,
            )

        except Exception as error:
            print(
                f"Failed to process "
                f"{source['name']}: {error}"
            )

    print("\n" + "=" * 60)
    print("SMARTDIGEST INGESTION FINISHED")
    print("=" * 60)


if __name__ == "__main__":
    run_ingestion()