.PHONY: install dev lint format type test coverage up down logs migrate shell

install:
	uv sync --all-groups

dev:
	uv run fastapi dev src/app/main.py --host 0.0.0.0 --port 8000

lint:
	uv run ruff check .

format:
	uv run ruff format .
	uv run ruff check --fix .

type:
	uv run ty check

test:
	uv run pytest

coverage:
	uv run coverage run -m pytest
	uv run coverage report

up:
	docker compose up --build

down:
	docker compose down -v

logs:
	docker compose logs -f app

migrate:
	uv run python -m app.db.init_db

shell:
	docker compose exec app sh
