#!/bin/sh
# backend/entrypoint.sh
# Runs before the API server starts. Container won't even reach this until
# Postgres is healthy (compose `depends_on: condition: service_healthy`),
set -e   # exit immediately if any command fails

# If a command was passed (e.g. `docker compose run api python -m scripts.seed`),
# run exactly that and skip the default boot
if [ "$#" -gt 0 ]; then
  exec "$@"
fi

echo "==> Creating tables (idempotent)..."
alembic upgrade head
 
echo "==> Seeding data (idempotent upsert)..."
python -m scripts.seed
 
echo "==> Starting API..."
# exec replaces the shell process with uvicorn, so signals (Ctrl-C, docker
# stop) reach uvicorn directly instead of being swallowed by the shell.
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
 