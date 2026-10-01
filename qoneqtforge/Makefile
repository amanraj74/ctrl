.PHONY: setup dev dev-backend dev-frontend test lint demo docker clean

setup:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

dev-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

dev:
	$(MAKE) dev-backend &
	$(MAKE) dev-frontend

test:
	cd backend && pytest -v
	cd frontend && npm run build

lint:
	cd backend && ruff check . && ruff format --check .

demo:
	cd backend && python -m scripts.generate_sample "AI is changing education"

docker:
	docker compose up --build

clean:
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/data/jobs/* 2>/dev/null || true
	rm -rf frontend/.next 2>/dev/null || true
