.PHONY: setup dev test demo-reset

setup:
	cp .env.example .env
	docker compose build

dev:
	docker compose up --build

test:
	cd apps/api && python -m uv run pytest -q
	cd apps/web && npm test -- --run

demo-reset:
	docker compose down -v

