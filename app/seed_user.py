from sqlalchemy import select

from app.config.sources import DEFAULT_USER
from app.database import SessionLocal
from app.models import User


def seed_user() -> None:
    """Create the default user, or update name/interests if it exists."""

    with SessionLocal() as session:
        existing = session.execute(
            select(User).where(User.email == DEFAULT_USER["email"])
        ).scalar_one_or_none()

        if existing:
            existing.name = DEFAULT_USER["name"]
            existing.interests = DEFAULT_USER["interests"]
            print("User updated.")
        else:
            session.add(User(**DEFAULT_USER))
            print("User created.")

        session.commit()


if __name__ == "__main__":
    seed_user()
