from datetime import datetime

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Article


def article_exists(url: str) -> bool:
    """Check whether an article already exists."""

    with SessionLocal() as session:
        statement = select(Article.id).where(
            Article.url == url
        )

        result = session.execute(statement).first()

        return result is not None


def save_article(
    url: str,
    source: str,
    title: str,
    published_at: datetime,
) -> Article:
    """Save a new article."""

    with SessionLocal() as session:
        article = Article(
            url=url,
            source=source,
            title=title,
            published_at=published_at,
        )

        session.add(article)
        session.commit()
        session.refresh(article)

        return article


def get_article(url: str) -> Article | None:
    """Retrieve an article by URL."""

    with SessionLocal() as session:
        statement = select(Article).where(
            Article.url == url
        )

        return session.execute(
            statement
        ).scalar_one_or_none()


def update_content(
    url: str,
    content: str | None,
    status: str,
) -> None:
    """Update article content and its status."""

    with SessionLocal() as session:
        statement = select(Article).where(
            Article.url == url
        )

        article = session.execute(
            statement
        ).scalar_one_or_none()

        if article is None:
            raise ValueError(
                f"Article '{url}' not found."
            )

        article.content = content
        article.content_status = status

        session.commit()


def update_summary(
    url: str,
    summary: str | None,
    status: str,
) -> None:
    """Update article summary and its status."""

    with SessionLocal() as session:
        statement = select(Article).where(
            Article.url == url
        )

        article = session.execute(
            statement
        ).scalar_one_or_none()

        if article is None:
            raise ValueError(
                f"Article '{url}' not found."
            )

        article.summary = summary
        article.summary_status = status

        session.commit()