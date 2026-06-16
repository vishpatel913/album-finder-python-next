# backend/Dockerfile
# Multi-stage: build deps in one layer, copy into a slim runtime image.

# ---- builder ----------------------------------------------------------------
FROM python:3.14-slim AS builder

ENV POETRY_VERSION=2.1.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    PIP_NO_CACHE_DIR=1

RUN pip install "poetry==${POETRY_VERSION}"

WORKDIR /app

# Copy only dependency manifests first -> this layer caches unless deps change.
COPY pyproject.toml poetry.lock* ./

# package-mode = false means --no-root is implicit; kept explicit for clarity.
RUN poetry install --no-root --without dev

# ---- runtime ----------------------------------------------------------------
FROM python:3.14-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

RUN useradd --create-home --uid 1000 appuser

WORKDIR /app

# Bring the virtualenv from the builder.
COPY --from=builder /app/.venv /app/.venv

# Copy application source. .dockerignore should exclude frontend/, .venv, etc.
COPY . .

# Make the entrypoint executable (in case the host bit didn't carry over).
RUN chmod +x ./entrypoint.sh

USER appuser

EXPOSE 8000

# Entrypoint runs init_db + seed, then exec's uvicorn. See entrypoint.sh.
ENTRYPOINT ["sh", "./entrypoint.sh"]
