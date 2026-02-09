.PHONY: help install dev lint format test up down logs k6

help:
	@echo "make install   - install deps"
	@echo "make dev       - run locally"
	@echo "make lint      - ruff check"
	@echo "make format    - ruff format + check"
	@echo "make test      - pytest"
	@echo "make up        - docker compose up --build"
	@echo "make down      - docker compose down"
	@echo "make logs      - docker compose logs -f"
	@echo "make k6        - run k6 load test"

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

dev:
	./scripts/run_dev.sh

lint:
	ruff check .

format:
	ruff format .
	ruff check .

test:
	pytest -q

up:
	docker compose up --build

down:
	docker compose down --remove-orphans

logs:
	docker compose logs -f

k6:
	k6 run load/k6_check.js
