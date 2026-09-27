from datetime import datetime

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Video


def video_exists(video_id: str) -> bool:
    """Check whether a video already exists."""

    with SessionLocal() as session:
        statement = select(Video.id).where(
            Video.video_id == video_id
        )

        result = session.execute(statement).first()

        return result is not None


def save_video(
    video_id: str,
    channel_id: str,
    title: str,
    url: str,
    published_at: datetime,
) -> Video:
    """Save a new video."""

    with SessionLocal() as session:

        video = Video(
            video_id=video_id,
            channel_id=channel_id,
            title=title,
            url=url,
            published_at=published_at,
        )

        session.add(video)
        session.commit()
        session.refresh(video)

        return video


def get_video(video_id: str) -> Video | None:
    """Retrieve a video by YouTube video ID."""

    with SessionLocal() as session:

        statement = select(Video).where(
            Video.video_id == video_id
        )

        return session.execute(
            statement
        ).scalar_one_or_none()


def update_transcript(
    video_id: str,
    transcript: str | None,
    status: str,
) -> None:
    """Update transcript and its status."""

    with SessionLocal() as session:

        statement = select(Video).where(
            Video.video_id == video_id
        )

        video = session.execute(
            statement
        ).scalar_one_or_none()

        if video is None:
            raise ValueError(
                f"Video '{video_id}' not found."
            )

        video.transcript = transcript
        video.transcript_status = status

        session.commit()


def update_summary(
    video_id: str,
    summary: str | None,
    status: str,
) -> None:
    """Update summary and its status."""

    with SessionLocal() as session:

        statement = select(Video).where(
            Video.video_id == video_id
        )

        video = session.execute(
            statement
        ).scalar_one_or_none()

        if video is None:
            raise ValueError(
                f"Video '{video_id}' not found."
            )

        video.summary = summary
        video.summary_status = status

        session.commit()