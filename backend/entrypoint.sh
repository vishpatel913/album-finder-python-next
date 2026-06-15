#!/bin/sh
# backend/entrypoint.sh
# Runs before the API server starts. Container won't even reach this until
# Postgres is healthy (compose `depends_on: condition: service_healthy`),
# so the DB is guaranteed reachable here.
set -e   # exit immediately if any command fails
 
echo "==> Creating tables (idempotent)..."
python -m scripts.init_db
 
echo "==> Seeding data (idempotent upsert)..."
python -m scripts.seed
 
echo "==> Starting API..."
# exec replaces the shell process with uvicorn, so signals (Ctrl-C, docker
# stop) reach uvicorn directly instead of being swallowed by the shell.
exec uvicorn main:app --host 0.0.0.0 --port 8000
 