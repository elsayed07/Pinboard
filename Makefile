.PHONY: help dev build up down logs shell migrate migrations test lint format typecheck clean

help:
	@echo "Pinboard development commands"
	@echo ""
	@echo "  make dev          Start all services (dev)"
	@echo "  make build        Rebuild Docker images"
	@echo "  make up           Start services (detached)"
	@echo "  make down         Stop all services"
	@echo "  make logs         Tail all service logs"
	@echo "  make shell        Django shell"
	@echo "  make bash         Bash into django container"
	@echo "  make migrate      Run pending migrations"
	@echo "  make migrations   Create new migrations"
	@echo "  make test         Run test suite"
	@echo "  make test-cov     Run tests with coverage report"
	@echo "  make lint         Run Ruff linter"
	@echo "  make format       Run Black formatter"
	@echo "  make typecheck    Run Pyright"
	@echo "  make clean        Remove containers and volumes"
	@echo "  make createsuperuser  Create an admin user"

dev:
	docker compose up

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

shell:
	docker compose exec django uv run python manage.py shell

bash:
	docker compose exec django bash

migrate:
	docker compose exec django uv run python manage.py migrate

migrations:
	docker compose exec django uv run python manage.py makemigrations

test:
	docker compose exec django uv run pytest -x -q

test-cov:
	docker compose exec django uv run pytest --cov --cov-report=html -q
	@echo "Coverage report: htmlcov/index.html"

lint:
	uv run ruff check .

format:
	uv run black .
	uv run ruff check --fix .

typecheck:
	uv run pyright

createsuperuser:
	docker compose exec django uv run python manage.py createsuperuser

clean:
	docker compose down -v --remove-orphans

install:
	uv sync

pre-commit:
	uv run pre-commit run --all-files
