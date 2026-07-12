.PHONY: setup dev test demo-seed demo-reset

setup:
	cp .env.example .env
	docker compose build

dev:
	docker compose up --build

test:
	cd apps/api && python -m uv run pytest -q
	cd apps/web && npm run typecheck && npm test -- --run --maxWorkers=1 && npm run build
	cd apps/web && npm run test:e2e

demo-reset:
	docker compose run --rm api uv run python -m app.demo.reset --confirm

demo-seed:
	docker compose run --rm api uv run python -m app.demo.seed
