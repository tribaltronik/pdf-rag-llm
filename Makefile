.PHONY: help build up down restart logs clean test lint format

# Default target
help:
	@echo "Available commands:"
	@echo "  build     - Build Docker images"
	@echo "  up        - Start all services"
	@echo "  down      - Stop all services"
	@echo "  restart   - Restart all services"
	@echo "  logs      - Show service logs"
	@echo "  clean     - Remove containers and volumes"
	@echo "  test      - Run tests"
	@echo "  lint      - Run linting"
	@echo "  format    - Format code"
	@echo "  dev       - Start in development mode"

# Build Docker images
build:
	docker-compose build

# Start all services
up:
	docker-compose up -d

# Start with logs following
dev:
	docker-compose up --build

# Stop all services
down:
	docker-compose down

# Restart services
restart: down up

# Show logs
logs:
	docker-compose logs -f

# Clean up everything
clean:
	docker-compose down -v
	docker system prune -f

# Run tests
test:
	docker-compose exec app python -m pytest

# Run linting
lint:
	docker-compose exec app python -m flake8 app/
	docker-compose exec app python -m mypy app/

# Format code
format:
	docker-compose exec app python -m black app/
	docker-compose exec app python -m isort app/

# Health check
health:
	curl -s http://localhost:8000/health

# Open web UI
ui:
	@echo "Opening web UI at http://localhost:8000"
	@open http://localhost:8000 2>/dev/null || echo "Manually open http://localhost:8000 in your browser"

# Quick test query
test-query:
	curl -X POST "http://localhost:8000/query" \
		-H "Content-Type: application/json" \
		-d '{"question": "What is this document about?"}' | python -m json.tool