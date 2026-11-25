import json
import re
import sys
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.database import SessionLocal
from app.llm.gemini import generate_with_fallback
from app.models import Article, ItemScore, User, Video


# Items sent to Gemini per request.
BATCH_SIZE = 20

# Summary characters shown to Gemini while scoring.
SNIPPET_CHARS = 700


def _load_items(session, lookback_hours: int) -> list[dict]:
    """Load summarized articles and videos from the lookback window."""

    cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)

    items = []

    articles = session.execute(
        select(Article)
        .where(Article.summary_status == "success")
        .where(Article.published_at >= cutoff)
    ).scalars()

    for article in articles:
        items.append(
            {
                "key": f"article:{article.id}",
                "item_type": "article",
                "item_id": article.id,
                "title": article.title,
                "url": article.url,
                "source": article.source,
                "summary": article.summary or "",
                "published_at": article.published_at,
            }
        )

    videos = session.execute(
        select(Video)
        .where(Video.summary_status == "success")
        .where(Video.published_at >= cutoff)
    ).scalars()

    for video in videos:
        items.append(
            {
                "key": f"video:{video.id}",
                "item_type": "video",
                "item_id": video.id,
                "title": video.title,
                "url": video.url,
                "source": "YouTube",
                "summary": video.summary or "",
                "published_at": video.published_at,
            }
        )

    return items


def _load_scores(session, user_id: int) -> dict[str, tuple[int, str]]:
    """Return already-saved scores for a user: key -> (score, reason)."""

    rows = session.execute(
        select(ItemScore).where(ItemScore.user_id == user_id)
    ).scalars()

    return {
        f"{row.item_type}:{row.item_id}": (row.score, row.reason or "")
        for row in rows
    }


def _build_prompt(interests: str, batch: list[dict]) -> str:
    lines = []

    for item in batch:
        snippet = item["summary"][:SNIPPET_CHARS].replace("\n", " ")

        lines.append(
            f'- id: {item["key"]}\n'
            f'  title: {item["title"]}\n'
            f'  summary: {snippet}'
        )

    items_text = "\n".join(lines)

    return f"""
You are a personal news curator.

The reader's interests:
{interests}

Score each news item from 0 to 10 for how relevant and valuable it is to
this reader.

Scoring guide:
- 9-10: directly about the reader's core interests, important and new
- 6-8: clearly related or broadly useful
- 3-5: loosely related
- 0-2: irrelevant, clickbait, or low value

Items:
{items_text}

Return ONLY a JSON array, with no markdown and no extra text. Include every
item exactly once, in this format:
[{{"id": "article:12", "score": 7, "reason": "one short sentence"}}]
"""


def _parse_scores(text: str) -> list[dict]:
    """Extract the JSON array from a Gemini response."""

    cleaned = re.sub(r"```(?:json)?", "", text).strip()

    start = cleaned.find("[")
    end = cleaned.rfind("]")

    if start == -1 or end == -1 or end < start:
        raise ValueError("No JSON array found in Gemini response.")

    data = json.loads(cleaned[start : end + 1])

    if not isinstance(data, list):
        raise ValueError("Gemini response is not a JSON array.")

    return data


def _score_batch(interests: str, batch: list[dict]) -> list[tuple[dict, int, str]]:
    """Score one batch of items with Gemini."""

    response = generate_with_fallback(_build_prompt(interests, batch))
    parsed = _parse_scores(response)

    by_key = {item["key"]: item for item in batch}
    results = []

    for entry in parsed:
        item = by_key.get(str(entry.get("id")))

        if item is None:
            continue

        try:
            score = int(round(float(entry.get("score"))))
        except (TypeError, ValueError):
            continue

        score = max(0, min(10, score))
        reason = str(entry.get("reason", "")).strip()

        results.append((item, score, reason))

    return results


def rank_for_user(
    user: User,
    lookback_hours: int = 24,
    top_n: int = 10,
) -> list[dict]:
    """
    Score new items for a user and return their top N items.

    Already-scored items are not scored again, so reruns are cheap.
    """

    with SessionLocal() as session:
        items = _load_items(session, lookback_hours)
        scores = _load_scores(session, user.id)

        unscored = [item for item in items if item["key"] not in scores]

        print(
            f"{user.name}: {len(items)} items in window, "
            f"{len(unscored)} to score."
        )

        for i in range(0, len(unscored), BATCH_SIZE):
            batch = unscored[i : i + BATCH_SIZE]

            try:
                results = _score_batch(user.interests, batch)

            except Exception as error:
                # Unscored items are retried on the next run.
                print(f"Scoring batch failed: {error}")
                continue

            for item, score, reason in results:
                session.add(
                    ItemScore(
                        user_id=user.id,
                        item_type=item["item_type"],
                        item_id=item["item_id"],
                        score=score,
                        reason=reason,
                    )
                )
                scores[item["key"]] = (score, reason)

            session.commit()

    ranked = []

    for item in items:
        if item["key"] not in scores:
            continue

        score, reason = scores[item["key"]]
        ranked.append({**item, "score": score, "reason": reason})

    ranked.sort(
        key=lambda x: (x["score"], x["published_at"]),
        reverse=True,
    )

    return ranked[:top_n]


def run_ranking(lookback_hours: int = 24, top_n: int = 10) -> None:
    with SessionLocal() as session:
        users = session.execute(
            select(User).where(User.is_active.is_(True))
        ).scalars().all()

    for user in users:
        top = rank_for_user(user, lookback_hours, top_n)

        print("\n" + "=" * 60)
        print(f"TOP {len(top)} FOR {user.name}")
        print("=" * 60)

        for position, item in enumerate(top, start=1):
            print(f"{position}. [{item['score']}/10] {item['title']}")
            print(f"   {item['source']} | {item['url']}")
            print(f"   {item['reason']}")


if __name__ == "__main__":
    hours = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    run_ranking(lookback_hours=hours)
