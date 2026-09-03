# ============================================================
# EcoMatch - Makefile (comandos DevOps)
# Uso: make <target>
# ============================================================

.PHONY: help up down restart logs logs-ai logs-back logs-front build test lint clean ps health

help: ## Mostrar esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

up: ## Levantar todo el stack (docker compose)
	docker compose up --build -d

down: ## Bajar todo el stack
	docker compose down

restart: ## Reiniciar todos los servicios
	docker compose restart

build: ## Solo build (sin levantar)
	docker compose build

ps: ## Ver estado de los contenedores
	docker compose ps

logs: ## Ver logs de todos los servicios
	docker compose logs -f

logs-ai: ## Ver logs del AI Orchestrator
	docker compose logs -f ai-orchestrator

logs-back: ## Ver logs del Backend
	docker compose logs -f back-api

logs-front: ## Ver logs del Frontend
	docker compose logs -f front-web

health: ## Health check de todos los servicios
	@echo "=== DB ===" && docker exec db-ecmatch mysqladmin ping -h localhost -u root -p$$(grep DB_PASSWORD .env | cut -d= -f2) --silent 2>/dev/null && echo "OK" || echo "FAIL"
	@echo "=== Backend ===" && curl -sf http://localhost:8080/actuator/health && echo "" || echo "FAIL"
	@echo "=== AI ===" && curl -sf http://localhost:8000/health && echo "" || echo "FAIL"
	@echo "=== Frontend ===" && curl -sf http://localhost/ && echo "" || echo "FAIL"

test: ## Correr tests del agente
	@echo "Ejecutando casos de prueba del agente..."
	@if [ -d ai-orchestrator ] && [ -f ai-orchestrator/requirements.txt ]; then \
		echo "Ver tests/agent-test-cases.md para casos manuales"; \
	else \
		echo "AI Orchestrator pendiente de implementacion"; \
	fi

lint: ## Linting del repo
	@echo "=== Frontend ===" && cd front-web && npm run lint --if-present || true

clean: ## Limpiar contenedores, volumenes e imagenes (PELIGROSO)
	docker compose down -v --rmi all

infra-plan: ## Simular creacion de infraestructura (dry-run)
	@echo "Revisar crear_infraestructura.sh antes de ejecutar"
	@bash -n crear_infraestructura.sh && echo "Sintaxis OK"

infra-apply: ## Crear infraestructura en AWS
	./crear_infraestructura.sh
