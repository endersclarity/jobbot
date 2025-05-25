# JobBot Development Makefile

.PHONY: help install dev test clean lint format run-dev migrate init-db

help:
	@echo "JobBot Development Commands:"
	@echo "  install     - Install dependencies"
	@echo "  dev         - Install development dependencies"
	@echo "  run-dev     - Run development server"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting"
	@echo "  format      - Format code"
	@echo "  init-db     - Initialize database with migrations"
	@echo "  migrate     - Run database migrations"
	@echo "  clean       - Clean up temporary files"

install:
	pip install -r requirements.txt

dev: install
	pip install pytest pytest-asyncio pytest-cov black isort flake8 mypy

run-dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v --cov=app

lint:
	flake8 app/ tests/
	mypy app/

format:
	black app/ tests/
	isort app/ tests/

init-db:
	alembic revision --autogenerate -m "Initial migration"
	alembic upgrade head

migrate:
	alembic upgrade head

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/