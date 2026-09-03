# EcoMatch ♻️ — Plataforma de Economía Circular

> Conecta generadores de residuos con receptores mediante un agente de IA (GLM 5.2).

## Estructura del Monorepo

```
front-web/           # Frontend (React/Vite + Nginx)
back-api/            # Backend API REST (Spring Boot)
ai-orchestrator/     # Capa IA - Agente GLM 5.2 (Python/FastAPI)
tests/               # Casos de prueba del agente (10 frases confusas)
.github/workflows/   # CI (ci.yml) + CD (deploy.yml)
task-definition.json # Manifiesto ECS Fargate
docker-compose.yml   # Stack local con healthchecks
Makefile             # Comandos DevOps
```

## Desarrollo Local

```bash
cp .env.example .env    # Rellenar valores reales
make up                 # Levantar todo el stack
make health             # Verificar que todo está healthy
make logs               # Ver logs
```

## Comandos DevOps

```bash
make help     # Ver todos los comandos disponibles
make up       # Levantar stack
make down     # Bajar stack
make health   # Health checks
make test     # Tests del agente
```

## CI/CD

- **`ci.yml`**: Se ejecuta en cada PR. Build + lint + escaneo de secretos.
- **`deploy.yml`**: Se ejecuta en push a `main`. Build → push ECR → deploy ECS Fargate.

## Roles del equipo (7 integrantes)

Ver `CONTRIBUTING.md` para el flujo de trabajo y `tests/agent-test-cases.md` para los casos de prueba del agente.
