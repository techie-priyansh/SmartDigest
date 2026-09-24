import os

from dotenv import load_dotenv
from sqlalchemy import create_engine


load_dotenv()


DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB")


if not all([DB_USER, DB_PASSWORD, DB_NAME]):
    raise ValueError(
        "PostgreSQL configuration is missing from .env"
    )


DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{DB_USER}:{DB_PASSWORD}@"
    f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)