.PHONY: help install dev-install clean test lint format run init validate docker-up docker-down docker-logs

help:
	@echo "Callaiag AI Agent - Development Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make install       - Install production dependencies"
	@echo "  make dev-install   - Install development dependencies"
	@echo "  make clean         - Clean temporary files and caches"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run code linters"
	@echo "  make format        - Format code with black"
	@echo "  make run           - Run the agent"
	@echo "  make init          - Initialize configuration"
	@echo "  make validate      - Validate setup"
	@echo "  make docker-up     - Start Docker containers"
	@echo "  make docker-down   - Stop Docker containers"
	@echo "  make docker-logs   - View Docker logs"

install:
	pip install -r requirements.txt

dev-install: install
	pip install -r requirements-dev.txt

clean:
	@echo "Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .coverage htmlcov/
	@echo "Clean complete!"

test:
	@echo "Running tests..."
	python -m pytest tests/ -v --cov=callaiag --cov-report=html --cov-report=term

lint:
	@echo "Running linters..."
	python -m pylint callaiag/
	python -m flake8 callaiag/
	python -m mypy callaiag/

format:
	@echo "Formatting code..."
	python -m black callaiag/ tests/
	python -m isort callaiag/ tests/

run:
	@echo "Starting Callaiag Agent..."
	python run.py start

init:
	@echo "Initializing configuration..."
	python run.py init

validate:
	@echo "Validating setup..."
	python run.py validate

docker-up:
	@echo "Starting Docker containers..."
	docker-compose up -d
	@echo "Containers started!"
	@echo "Dashboard: http://localhost:8080"

docker-down:
	@echo "Stopping Docker containers..."
	docker-compose down

docker-logs:
	docker-compose logs -f callaiag

docker-build:
	@echo "Building Docker image..."
	docker-compose build

setup-dev:
	@echo "Setting up development environment..."
	python -m venv venv
	@echo "Virtual environment created. Activate with: source venv/bin/activate"
	@echo "Then run: make dev-install"
