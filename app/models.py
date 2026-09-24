from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    video_id: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
    )

    channel_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    transcript: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    transcript_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="pending",
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    summary_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="pending",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )