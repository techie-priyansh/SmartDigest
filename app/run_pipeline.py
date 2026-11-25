import argparse

from sqlalchemy import select

from app.database import SessionLocal
from app.emailer import build_html, build_subject, build_text, send_email
from app.models import SentItem, User
from app.ranking import rank_for_user
from app.run_ingestion import run_ingestion


# Items scoring below this are not worth emailing.
MIN_SCORE = 4


def mark_sent(user_id: int, items: list[dict]) -> None:
    """Record emailed items so they are never sent to the user again."""

    with SessionLocal() as session:
        for item in items:
            session.add(
                SentItem(
                    user_id=user_id,
                    item_type=item["item_type"],
                    item_id=item["item_id"],
                )
            )

        session.commit()


def run_pipeline(
    lookback_hours: int = 24,
    top_n: int = 10,
    dry_run: bool = False,
    skip_ingestion: bool = False,
) -> None:
    """
    Full SmartDigest run:
        ingest feeds -> score per user -> email the top N.
    """

    if not skip_ingestion:
        run_ingestion(lookback_hours=lookback_hours)

    with SessionLocal() as session:
        users = session.execute(
            select(User).where(User.is_active.is_(True))
        ).scalars().all()

    for user in users:
        try:
            items = rank_for_user(user, lookback_hours, top_n)
            items = [item for item in items if item["score"] >= MIN_SCORE]

            if not items:
                print(f"No new relevant items for {user.name}. Skipping email.")
                continue

            subject = build_subject(len(items))
            html = build_html(user.name, items)
            text = build_text(user.name, items)

            if dry_run:
                path = f"digest_preview_{user.id}.html"

                with open(path, "w", encoding="utf-8") as file:
                    file.write(html)

                print(f"[dry run] Preview written to {path}. Nothing sent.")
                continue

            send_email(user.email, subject, html, text)
            mark_sent(user.id, items)

            print(f"Digest sent to {user.email} ({len(items)} items).")

        except Exception as error:
            # One user's failure must not stop the others.
            print(f"Digest failed for {user.email}: {error}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the SmartDigest pipeline.")
    parser.add_argument("--lookback-hours", type=int, default=24)
    parser.add_argument("--top-n", type=int, default=10)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Write an HTML preview instead of sending email.",
    )
    parser.add_argument(
        "--skip-ingestion",
        action="store_true",
        help="Skip fetching feeds; only rank and email existing items.",
    )

    args = parser.parse_args()

    run_pipeline(
        lookback_hours=args.lookback_hours,
        top_n=args.top_n,
        dry_run=args.dry_run,
        skip_ingestion=args.skip_ingestion,
    )
