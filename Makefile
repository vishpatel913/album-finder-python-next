# Album Finder — dev entrypoints.
# Run `make` (or `make help`) to see everything. Targets wrap docker compose
# and the frontend npm scripts so you don't have to remember either.

# Use bash and fail loudly.
SHELL := /bin/bash

.DEFAULT_GOAL := help

## ----------------------------------------------------------------------------
## Stack (docker compose: database, api, web, pgadmin)
## ----------------------------------------------------------------------------

.PHONY: up
up: ## Start the full stack in the background (db + api + web)
	docker compose up -d database api web

.PHONY: backend
backend: ## Start just the backend (db + api) for working on the FE locally
	docker compose up -d database api

.PHONY: down
down: ## Stop and remove containers (keeps data volumes)
	docker compose down

.PHONY: ps
ps: ## Show container status
	docker compose ps

.PHONY: logs
logs: ## Tail logs for api + web (Ctrl-C to stop)
	docker compose logs -f api web

.PHONY: rebuild
rebuild: ## Rebuild images from scratch (after dependency changes)
	docker compose build --no-cache

.PHONY: nuke
nuke: ## DESTRUCTIVE: stop everything and drop the database volume
	docker compose down -v

## ----------------------------------------------------------------------------
## Database
## ----------------------------------------------------------------------------

.PHONY: init-db
init-db: ## Create tables (idempotent)
	docker compose run --rm api python -m scripts.init_db

.PHONY: seed
seed: ## Seed / upsert data (idempotent)
	docker compose run --rm api python -m scripts.seed

.PHONY: pgadmin
pgadmin: ## Open pgAdmin (http://localhost:5050 — admin@admin.com / admin)
	open http://localhost:5050

## ----------------------------------------------------------------------------
## Frontend (frontend/ — Vite + React)
## ----------------------------------------------------------------------------

.PHONY: install
install: ## Install frontend dependencies
	cd frontend && npm install

.PHONY: dev
dev: ## Run the Vite dev server on the host (needs `make backend` up)
	cd frontend && npm run dev

.PHONY: build
build: ## Production build of the frontend
	cd frontend && npm run build

.PHONY: typecheck
typecheck: ## Typecheck the frontend
	cd frontend && npm run typecheck

.PHONY: gen-api
gen-api: ## Regenerate TS types from the API's OpenAPI doc (needs api on :8004)
	cd frontend && npm run gen:api

## ----------------------------------------------------------------------------

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'
