import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

import streamlit as st
from sqlalchemy import select

from app.database import SessionLocal
from app.models import Article, Video
st.set_page_config(
    page_title="SmartDigest",
    page_icon="📰",
    layout="wide",
)


def get_articles():
    """Fetch articles that have successful summaries."""

    with SessionLocal() as session:
        statement = (
            select(Article)
            .where(Article.summary_status == "success")
            .order_by(Article.published_at.desc())
        )

        return session.execute(statement).scalars().all()


def get_videos():
    """Fetch videos that have successful summaries."""

    with SessionLocal() as session:
        statement = (
            select(Video)
            .where(Video.summary_status == "success")
            .order_by(Video.published_at.desc())
        )

        return session.execute(statement).scalars().all()


# ---------------------------------------------------------
# Page
# ---------------------------------------------------------

st.title("SmartDigest")
st.caption("AI-powered multi-source news digest")

st.markdown("---")


# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

articles = get_articles()
videos = get_videos()
# ---------------------------------------------------------
# Today's content
# ---------------------------------------------------------

today = datetime.now(timezone.utc).date()

today_articles = [
    article
    for article in articles
    if article.published_at.date() == today
]

today_videos = [
    video
    for video in videos
    if video.published_at.date() == today
]

st.sidebar.title("Search")

search_query = st.sidebar.text_input(
    "Search news",
    placeholder="Search by title or summary...",
)

st.sidebar.markdown("---")
# ---------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------

st.sidebar.title("Filters")

article_sources = sorted(
    {article.source for article in articles}
)

selected_sources = st.sidebar.multiselect(
    "News Sources",
    options=article_sources,
    default=article_sources,
)

show_articles = st.sidebar.checkbox(
    "Articles",
    value=True,
)

show_videos = st.sidebar.checkbox(
    "Videos",
    value=True,
)

articles = [
    article
    for article in articles
    if article.source in selected_sources
]


# ---------------------------------------------------------
# Metrics
# ---------------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Articles", len(articles))

with col2:
    st.metric("Videos", len(videos))

with col3:
    st.metric(
        "Total Summaries",
        len(articles) + len(videos),
    )


st.markdown("---")

st.markdown("---")

st.header("Today's Digest")

digest_items = []

for article in today_articles:
    digest_items.append(
        {
            "title": article.title,
            "source": article.source,
            "summary": article.summary,
            "url": article.url,
            "type": "Article",
        }
    )

for video in today_videos:
    digest_items.append(
        {
            "title": video.title,
            "source": video.channel_id,
            "summary": video.summary,
            "url": video.url,
            "type": "Video",
        }
    )

if not digest_items:

    st.info(
        "No summarized content available for today."
    )

else:

    st.caption(
        f"{len(digest_items)} summarized stories "
        f"published today"
    )

    for index, item in enumerate(
        digest_items,
        start=1,
    ):

        with st.container(border=True):

            st.markdown(
                f"### {index}. {item['title']}"
            )

            st.caption(
                f"{item['type']} • {item['source']}"
            )

            st.write(item["summary"])

            st.link_button(
                "Open Original",
                item["url"],
            )
# ---------------------------------------------------------
# Articles
# ---------------------------------------------------------


if show_articles:

    st.header("Latest Articles")

    if not articles:
        st.info("No articles match the selected filters.")

    else:
        for article in articles:
            with st.expander(

                f"{article.source} — {article.title}",
                expanded=False,
            ):
        
                st.caption(
                    f"Published: "
                    f"{article.published_at:%d %b %Y, %H:%M UTC}"
                )

                st.markdown("### AI Summary")

                st.write(article.summary)

                st.markdown("### Extracted Article Content")

                if article.content:
                    st.write(article.content)
                else:
                    st.info("Article content is not available.")

                st.link_button(
                    "Read Original Article",
                    article.url,
                )
# ---------------------------------------------------------
# Videos
# ---------------------------------------------------------

# st.header("Latest Videos")

if show_videos:

    st.header("Latest Videos")

    if not videos:
        st.info("No summarized videos available.")

    else:
        for video in videos:
            with st.expander(
                f"{video.channel_id} — {video.title}",
                expanded=False,
            ):
                
                st.caption(
                    f"Published: "
                    f"{video.published_at:%d %b %Y, %H:%M UTC}"
                )

                st.markdown("### AI Summary")

                st.write(video.summary)

                st.markdown("### Transcript")

                if video.transcript:
                    st.write(video.transcript)
                else:
                    st.info("Transcript is not available.")

                st.link_button(
                    "Watch on YouTube",
                    video.url,
                )