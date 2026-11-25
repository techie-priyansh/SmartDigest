import os

from sqlalchemy import select

from app.config.sources import DEFAULT_USER
from app.database import SessionLocal
from app.models import User


def get_user_config() -> dict:
    """
    Default user details, overridable through environment variables so
    a real email address never has to be committed to the repository.
    """

    return {
        "email": os.getenv("DIGEST_USER_EMAIL") or DEFAULT_USER["email"],
        "name": os.getenv("DIGEST_USER_NAME") or DEFAULT_USER["name"],
        "interests": (
            os.getenv("DIGEST_USER_INTERESTS") or DEFAULT_USER["interests"]
        ),
    }


def seed_user() -> None:
    """Create the default user, or update name/interests if it exists."""

    config = get_user_config()

    with SessionLocal() as session:
        existing = session.execute(
            select(User).where(User.email == config["email"])
        ).scalar_one_or_none()

        if existing:
            existing.name = config["name"]
            existing.interests = config["interests"]
            print("User updated.")
        else:
            session.add(User(**config))
            print("User created.")

        session.commit()


if __name__ == "__main__":
    seed_user()
