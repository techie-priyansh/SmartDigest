import requests
import trafilatura


def fetch_article_content(url: str) -> str:
    """
    Fetch and extract the main text from an article webpage.
    """

    response = requests.get(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/140.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml",
        },
        timeout=20,
    )

    response.raise_for_status()

    content = trafilatura.extract(
        response.text,
        include_comments=False,
        include_tables=False,
        include_links=False,
    )

    if not content:
        raise ValueError(
            f"Could not extract article content from: {url}"
        )

    return content