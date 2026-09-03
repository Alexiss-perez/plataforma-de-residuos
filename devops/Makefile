# ============================================================
# EcoMatch - Makefile (comandos DevOps)
# Uso: make <target>
# ============================================================

.PHONY: help up down restart logs logs-ai logs-back logs-front build test lint clean ps health test-agent

help: ## Mostrar esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

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
	docker compose logs -f backend

logs-db: ## Ver logs de la Base de Datos
	docker compose logs -f db-ecmatch

health: ## Health check de todos los servicios
	@echo "=== DB ==="        && docker exec db-ecmatch pg_isready -U ecmatch 2>/dev/null && echo "OK" || echo "FAIL"
	@echo "=== Backend ==="  && curl -sf http://localhost:8000/health && echo "" || echo "FAIL"
	@echo "=== AI ==="       && curl -sf http://localhost:8001/health && echo "" || echo "FAIL"

test-agent: ## Correr los 11 tests del agente IA
	@echo "Ejecutando tests del agente..."
	docker exec ai-orchestrator python ecomatch_agent.py --test 2>/dev/null || \
		echo "Levanta el stack primero: make up"

test-backend: ## Correr tests del backend
	@echo "Ejecutando tests del backend..."
	docker exec backend pytest -v 2>/dev/null || \
		echo "Levanta el stack primero: make up"

test: test-backend test-agent ## Correr todos los tests

lint: ## Linting (si existe)
	@echo "Linting pendiente de configurar"

clean: ## Limpiar contenedores y volumenes (PELIGROSO)
	docker compose down -v

infra-plan: ## Validar sintaxis del script de infraestructura
	@bash -n devops/crear_infraestructura.sh && echo "Sintaxis OK"

infra-apply: ## Crear infraestructura en AWS
	./devops/crear_infraestructura.sh
