FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies first so this layer is cached between code changes.
COPY requirements-prod.txt .
RUN pip install -r requirements-prod.txt

COPY app ./app

# Run as a non-root user.
RUN useradd --create-home appuser
USER appuser

# One run of the whole job: create tables, seed the user, then
# ingest -> score -> email. Safe to repeat on every scheduled run.
CMD ["sh", "-c", "python -m app.init_db && python -m app.seed_user && python -m app.run_pipeline"]
