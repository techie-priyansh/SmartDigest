from app.scrapers.article import fetch_article_content
from app.scrapers.rss import fetch_recent_articles
from app.storage.articles import (
    article_exists,
    save_article,
    update_content,
)

from app.llm.gemini import summarize_transcript
from app.scrapers.article import fetch_article_content
from app.scrapers.rss import fetch_recent_articles
from app.storage.articles import (
    article_exists,
    get_article,
    save_article,
    update_content,
    update_summary,
)


def process_article(url: str) -> bool:
    """
    Process an existing article using its current database state.

    Retries only the stages that have not succeeded.
    """

    article = get_article(url)

    if article is None:
        raise ValueError(
            f"Article '{url}' not found in database."
        )

    print(f"\nProcessing: {article.title}")

    # ---------------------------------------------------------
    # Step 1: Article content
    # ---------------------------------------------------------

    if article.content_status == "success":
        print("Article content already available. Skipping.")

    else:
        print("Fetching article content...")

        try:
            content = fetch_article_content(article.url)

            update_content(
                url=article.url,
                content=content,
                status="success",
            )

            article.content = content
            article.content_status = "success"

            print(
                f"Article content saved "
                f"({len(content)} characters)"
            )

        except Exception as error:
            update_content(
                url=article.url,
                content=None,
                status="failed",
            )

            print(f"Article extraction failed: {error}")
            return False

    # ---------------------------------------------------------
    # Step 2: Summary
    # ---------------------------------------------------------

    if article.summary_status == "success":
        print("Summary already available. Skipping.")
        return True

    print("Generating Gemini summary...")

    try:
        summary = summarize_transcript(
            transcript=article.content,
            title=article.title,
        )

        update_summary(
            url=article.url,
            summary=summary,
            status="success",
        )

        print(
            f"Summary saved "
            f"({len(summary)} characters)"
        )

    except Exception as error:
        update_summary(
            url=article.url,
            summary=None,
            status="failed",
        )

        print(f"Summary failed: {error}")
        return False

    return True

def ingest_rss_feed(
    feed_url: str,
    lookback_hours: int = 24,
) -> int:
    """
    Fetch recent RSS articles and process them.

    Existing articles are retried if their content or summary
    has not succeeded yet.

    Pipeline:
        RSS → PostgreSQL → Article Content → Gemini → PostgreSQL

    Returns
    -------
    int
        Number of newly discovered articles.
    """

    print(f"\nFetching RSS feed: {feed_url}")

    articles = fetch_recent_articles(
        feed_url=feed_url,
        lookback_hours=lookback_hours,
    )

    print(f"Found {len(articles)} recent articles.")

    new_articles = 0
    successful = 0
    failed = 0

    for article_data in articles:
        url = article_data["url"]
        title = article_data["title"]

        # -----------------------------------------------------
        # Check whether article already exists
        # -----------------------------------------------------

        if article_exists(url):
            print(f"\nExisting article: {title}")

            try:
                success = process_article(url)

                if success:
                    successful += 1
                else:
                    failed += 1

            except Exception as error:
                failed += 1
                print(f"Article processing failed: {error}")

            continue

        # -----------------------------------------------------
        # Save new article
        # -----------------------------------------------------

        save_article(
            url=url,
            source=article_data["source"],
            title=title,
            published_at=article_data["published_at"],
        )

        new_articles += 1

        print(f"\nNew article discovered: {title}")

        # -----------------------------------------------------
        # Process new article
        # -----------------------------------------------------

        try:
            success = process_article(url)

            if success:
                successful += 1
            else:
                failed += 1

        except Exception as error:
            failed += 1
            print(f"Article processing failed: {error}")

    print("\n" + "=" * 50)
    print("RSS INGESTION COMPLETE")
    print("=" * 50)

    print(f"Articles discovered : {len(articles)}")
    print(f"New articles       : {new_articles}")
    print(f"Successful         : {successful}")
    print(f"Failed             : {failed}")
    print("=" * 50)

    return new_articles