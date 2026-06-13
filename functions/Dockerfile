# backend/Dockerfile
# Multi-stage: build deps in one layer, copy into a slim runtime image.

# ---- builder ----------------------------------------------------------------
FROM python:3.11-slim AS builder

ENV POETRY_VERSION=2.1.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    PIP_NO_CACHE_DIR=1

# psycopg2-binary ships wheels, so no libpq build deps needed here.
RUN pip install "poetry==${POETRY_VERSION}"

WORKDIR /app

# Copy only dependency manifests first → this layer caches unless deps change.
COPY pyproject.toml poetry.lock* ./

# package-mode = false in your pyproject means --no-root is implicit,
# but we keep --no-root explicit for clarity. Only main deps, skip dev.
RUN poetry install --no-root --without dev

# ---- runtime ----------------------------------------------------------------
FROM python:3.11-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Run as non-root.
RUN useradd --create-home --uid 1000 appuser

WORKDIR /app

# Bring the virtualenv from the builder.
COPY --from=builder /app/.venv /app/.venv

# Copy application source. .dockerignore should exclude frontend/, .venv, etc.
COPY . .

USER appuser

EXPOSE 8000

# --host 0.0.0.0 so the container is reachable from outside.
# No --reload here; that's a dev-compose override (see compose file).
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
