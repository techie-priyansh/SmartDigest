import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


load_dotenv()


def _build_database_url() -> str:
    """
    Resolve the database URL.

    DATABASE_URL (used by Render and most hosts) wins when set.
    Otherwise the URL is built from the POSTGRES_* variables.
    """

    url = os.getenv("DATABASE_URL")

    if url:
        # Hosts hand out "postgres://" or "postgresql://" URLs, but
        # SQLAlchemy needs the psycopg2 driver named explicitly.
        for prefix in ("postgres://", "postgresql://"):
            if url.startswith(prefix):
                return "postgresql+psycopg2://" + url[len(prefix):]

        return url

    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    name = os.getenv("POSTGRES_DB")

    if not all([user, password, name]):
        raise ValueError(
            "Database configuration is missing. Set DATABASE_URL, "
            "or POSTGRES_USER, POSTGRES_PASSWORD and POSTGRES_DB."
        )

    return (
        f"postgresql+psycopg2://"
        f"{user}:{password}@"
        f"{host}:{port}/{name}"
    )


DATABASE_URL = _build_database_url()


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)
