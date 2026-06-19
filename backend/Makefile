# Backend (FastAPI + SQLModel) — dev entrypoints.
# Run these from this directory: `make lint`, `make lint-fix`, etc.
# Lint + typecheck run inside the local .venv so they match the editor.

SHELL := /bin/bash

.DEFAULT_GOAL := help

# Interpreter used to build the lint venv. Project requires Python >= 3.14.
PY  ?= python3.14
BIN := .venv/bin

.PHONY: setup
setup: ## Create .venv and install runtime + lint tooling
	$(PY) -m venv .venv
	$(BIN)/pip install -q --upgrade pip
	$(BIN)/pip install -q fastapi sqlmodel uvicorn psycopg2-binary python-dotenv \
		ruff pyright pytest httpx

.PHONY: lint
lint: ## Lint + typecheck (ruff check, format check, pyright)
	$(BIN)/ruff check .
	$(BIN)/ruff format --check .
	$(BIN)/pyright

.PHONY: lint-fix
lint-fix: ## Auto-fix lint and apply formatting
	$(BIN)/ruff check . --fix
	$(BIN)/ruff format .

.PHONY: test
test: ## Run the test suite
	$(BIN)/pytest

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'
