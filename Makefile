.PHONY: install install-dev install-browsers local-server lint fmt test build-to-deploy

# Install dependencies
install:
	uv pip install -e .

# Install dev dependencies
install-dev:
	uv pip install -e ".[dev]"

# Install Playwright browsers
install-browsers:
	playwright install chromium

# Run local development server
local-server:
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Lint code
lint:
	ruff check src/ tests/

# Format code
fmt:
	ruff format src/ tests/

# Run tests
test:
	pytest tests/ -v

# Build Docker image for deployment (Cloud Run)
build-to-deploy:
	docker build --platform linux/amd64 -t horas-registro-civil:latest .

# Run Docker container locally
run-docker:
	docker run -p 8080:8080 --env-file .env horas-registro-civil:latest
