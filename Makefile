# Makefile for Callaiag AI Agent

.PHONY: help install init validate start stop clean test lint format docker-build docker-up docker-down

help:
	@echo "Callaiag AI Agent - Development Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make install       - Install Python dependencies"
	@echo "  make init          - Initialize system configuration"
	@echo "  make validate      - Validate system setup"
	@echo "  make start         - Start the AI agent"
	@echo "  make stop          - Stop the AI agent"
	@echo "  make clean         - Clean temporary files"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linters"
	@echo "  make format        - Format code"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-up     - Start with Docker Compose"
	@echo "  make docker-down   - Stop Docker Compose"
	@echo ""

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

init:
	@echo "Initializing Callaiag system..."
	python3 run.py init

validate:
	@echo "Validating system setup..."
	python3 run.py validate

start:
	@echo "Starting Callaiag AI Agent..."
	python3 run.py start

stop:
	@echo "Stopping Callaiag AI Agent..."
	@pkill -f "python3 run.py start" || true

clean:
	@echo "Cleaning temporary files..."
	rm -rf temp/*
	rm -rf __pycache__
	rm -rf callaiag/__pycache__
	rm -rf callaiag/*/__pycache__
	rm -rf .pytest_cache
	rm -rf *.pyc
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean complete"

test:
	@echo "Running tests..."
	pytest tests/ -v --cov=callaiag

lint:
	@echo "Running linters..."
	flake8 callaiag/ --max-line-length=120
	mypy callaiag/ --ignore-missing-imports

format:
	@echo "Formatting code..."
	black callaiag/ --line-length=120

docker-build:
	@echo "Building Docker image..."
	docker build -t callaiag:latest .

docker-up:
	@echo "Starting with Docker Compose..."
	docker-compose up -d

docker-down:
	@echo "Stopping Docker Compose..."
	docker-compose down

# Development shortcuts
dev: install init
	@echo "Development environment ready!"

quick-start: validate start

status:
	@echo "System status:"
	@ps aux | grep "python3 run.py" | grep -v grep || echo "Agent not running"
