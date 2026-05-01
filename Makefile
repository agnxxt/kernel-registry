.PHONY: dev build down setup status test help

# Default target
help:
	@echo "Agent Kernel Control Plane - Makefile"
	@echo "--------------------------------------"
	@echo "dev     : Start all services in background"
	@echo "build   : Rebuild all docker images"
	@echo "down    : Stop all services"
	@echo "setup   : Bootstrap OpenFGA and Feast models"
	@echo "status  : Check container status"
	@echo "test    : Run E2E smoke tests"

dev:
	docker compose up -d

build:
	docker compose up --build -d

down:
	docker compose down

setup:
	docker compose exec kernel-api python scripts/setup_fga_model.py
	docker compose exec feast feast -c feature_repo apply

status:
	docker compose ps

test:
	pytest tests/e2e/test_platform_flow.py
	pytest tests/journey/github_slack_summary.py
