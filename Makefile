# Makefile for Air Drums Docker operations

.PHONY: help build build-dev run run-dev stop logs clean shell test

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build production Docker image
	docker build --target production -t air-drums:latest .

build-dev: ## Build development Docker image
	docker build --target development -t air-drums:dev .

run: ## Run production container
	docker-compose up -d

run-dev: ## Run development container with hot reload
	docker-compose -f docker-compose.dev.yml up -d

stop: ## Stop all containers
	docker-compose down
	docker-compose -f docker-compose.dev.yml down

logs: ## View container logs
	docker-compose logs -f

logs-dev: ## View development container logs
	docker-compose -f docker-compose.dev.yml logs -f

clean: ## Remove containers and images
	docker-compose down -v
	docker-compose -f docker-compose.dev.yml down -v
	docker rmi air-drums:latest air-drums:dev 2>/dev/null || true

shell: ## Open shell in running container
	docker exec -it air-drums bash

rebuild: ## Rebuild and restart containers
	docker-compose up --build -d

rebuild-dev: ## Rebuild and restart development containers
	docker-compose -f docker-compose.dev.yml up --build -d

status: ## Show container status
	docker-compose ps

test: ## Run basic connectivity test
	@echo "Testing application..."
	@sleep 3
	@curl -f http://localhost:5000/ > /dev/null 2>&1 && echo "✓ Application is running!" || echo "✗ Application is not responding"


