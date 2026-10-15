.PHONY: dev dev-backend dev-frontend test build

dev:
	$(MAKE) -j2 dev-backend dev-frontend

dev-backend:
	uv run uvicorn app.main:app --app-dir backend --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

test:
	uv run pytest backend/tests
	cd frontend && npm test

build:
	cd frontend && npm run build
