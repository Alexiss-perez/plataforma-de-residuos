# Rol DevOps — EcoMatch ♻️

> Documento de resumen del trabajo realizado por el rol **QA/DevOps** en el proyecto EcoMatch.
> **Fecha:** 2026-09-03
> **Repo:** `Alexiss-perez/plataforma-de-residuos`

---

## 1. Infraestructura como Código

### Docker Compose
- **`docker-compose.yml`** — Stack completo de 3 servicios:
  - `db-ecmatch` — PostgreSQL 16-alpine con healthcheck (`pg_isready`)
  - `backend` — FastAPI en puerto 8000 con healthcheck
  - `ai-orchestrator` — Agente IA GLM 5.2 en puerto 8001 con healthcheck
  - Red bridge `ecmatch-net` + volumen `pgdata` persistente
  - Dependencias con `condition: service_healthy`

### Scripts de Infraestructura
- **`devops/crear_infraestructura.sh`** — Script IaC para AWS con `set -euo pipefail`:
  - Security groups restrictivos (puerto 80 público, 8080/8000 solo VPC)
  - RDS MySQL con contraseña desde Secrets Manager
  - ECS Fargate cluster + task definition + service (desired-count 2)
  - Validación de variables de entorno requeridas antes de ejecutar
- **`devops/task-definition.json`** — Definición de tarea ECS:
  - 3 contenedores: `front-web`, `back-api`, `ai-orchestrator`
  - CPU 1024 / Memory 2048
  - Secrets desde AWS Secrets Manager (no hardcodeados)
  - Healthchecks por contenedor

### Dockerfiles
- **`backend/Dockerfile`** — `python:3.12-slim`, expone 8000, uvicorn
- **`ia/Dockerfile`** — `python:3.12-slim`, expone 8001, uvicorn
- **`devops/ai-orchestrator/Dockerfile`** — Placeholder con healthcheck
- **`devops/.dockerignore`** — Excluye `.env`, `node_modules`, `__pycache__`, `.git`, docs

---

## 2. CI/CD — GitHub Actions

### Workflow de CI (`ci.yml`)
- **Escaneo de secretos** con TruffleHog (`--only-verified`)
- **Lint Frontend** — condicional con `hashFiles()` (fix aplicado)
- **Build Frontend** — condicional
- **Build Backend (Docker)** — construye imagen si existe Dockerfile
- **Build AI Orchestrator (Docker)** — construye imagen si existe Dockerfile
- **Tests del Agente** — pendiente de implementación automatizada
- Triggers: `push` y `pull_request` a `main`/`master`

### Workflow de CD (`deploy.yml`)
- Configuración de AWS credentials
- Build & push a ECR
- Update ECS task definition + service
- Requiere secrets: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`

### Fix del CI (PR #4)
- **Problema:** `setup-node` fallaba cachando `front-web/package-lock.json` que no existe
- **Solución:** Hacer condicional el setup de Node con `${{ hashFiles('front-web/package.json') != '' }}`
- **Estado:** CI pasa en verde ✅

---

## 3. Calidad y Testing

### Casos de Prueba del Agente
- **`devops/tests/agent-test-cases.md`** — 10 casos documentados:

| # | Caso | Categoría rúbrica |
|---|---|---|
| TC-01 | Info mínima (solo material) | Ambigüedad |
| TC-02 | Material ambiguo | Ambigüedad |
| TC-03 | Volumen en unidades vagas | Ambigüedad |
| TC-04 | Dirección inexistente (Narnia) | Cero alucinaciones |
| TC-05 | Empresa que no existe en BD | Cero alucinaciones |
| TC-06 | Múltiples materiales mezclados | Ambigüedad |
| TC-07 | Jailbreak/prompt injection | Seguridad |
| TC-08 | Flujo completo (camino feliz) | Autonomía |
| TC-09 | Consulta sobre leyes | Cero alucinaciones |
| TC-10 | Usuario confundido | Autonomía |

### Smoke Test
- **`devops/smoke-test.sh`** — Test end-to-end:
  1. Verifica que `.env` exista
  2. Levanta el stack con `docker compose up`
  3. Espera healthchecks (max 90s)
  4. Prueba chat con el agente (`POST /chat`)
  5. Reporta estado de DB + Backend + AI

### Reportes de Testing
- **`devops/reporte-pruebas-cicd.md`** — Evaluación de 10 runs de CI/CD (2 OK, 8 fail)
- **`devops/reporte-testeo-devops.md`** — Testeo local de `devops/` (20 tests, 11 OK, 3 bugs)

---

## 4. Templates y Gobernanza

### Issue Templates (`.github/ISSUE_TEMPLATE/`)
- `bug_report.md` — Reporte de bugs con formato estructurado
- `feature_request.md` — Solicitud de features
- `test_agent.md` — Caso de prueba del agente IA

### PR Template
- **`.github/PULL_REQUEST_TEMPLATE.md`** — Checklist de revisión (tests, docs, seguridad)

### Guías
- **`CONTRIBUTING.md`** — Guía de contribución y flujo de trabajo
- **`README.md`** — Documentación del proyecto con stack, endpoints y uso

### Saneamiento de Secretos
- **`.gitignore`** — Ignora `.env`, `node_modules`, `__pycache__`, etc.
- **`.env.example`** — Template de variables sin secretos reales
- Verificado: `.env` NO está trackeado por git

---

## 5. Automatización — Makefile

**`devops/Makefile`** — 16 targets:

| Target | Función |
|---|---|
| `up` / `down` / `restart` | Levantar/bajar/reiniciar stack |
| `build` | Build sin levantar |
| `ps` / `logs` / `logs-ai` / `logs-back` / `logs-db` | Estado y logs |
| `health` | Health check de DB + Backend + AI |
| `test` / `test-backend` / `test-agent` | Runners de tests |
| `lint` | Linting (pendiente) |
| `clean` | Limpiar contenedores + volúmenes |
| `infra-plan` | Validar sintaxis del script IaC |
| `infra-apply` | Crear infraestructura en AWS |

---

## 6. PRs Mergeados

| PR # | Título | Rama | Contenido |
|---|---|---|---|
| #3 | Infraestructura DevOps + GitOps | `feature/devops-infraestructura` | CI/CD, Docker, tests, templates |
| #4 | Fix cache npm condicional | `fix/ci-frontend-cache` | Fix del CI para frontend inexistente |

---

## 7. Bugs Detectados mediante Testing

| # | Bug | Severidad | Estado |
|---|---|---|---|
| 1 | Healthcheck backend usa `curl` no disponible en `python:3.12-slim` | Alta | Pendiente fix |
| 2 | Makefile path relativo incorrecto (`devops/crear_infraestructura.sh`) | Media | Pendiente fix |
| 3 | `devops/ai-orchestrator/` es placeholder obsoleto | Media | Pendiente fix |
| 4 | `task-definition.json` configurado para Java/Spring, no Python/FastAPI | Baja | Pendiente fix |

---

## 8. Pendientes

- [ ] Aplicar fix de los 4 bugs detectados
- [ ] Configurar branch protection en `main` (requiere permisos admin)
- [ ] Agregar secrets de AWS en GitHub (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`)
- [ ] Configurar `KOSTRA_API_KEY` para integración real con GLM 5.2
- [ ] Automatizar los 10 casos de prueba del agente en el CI
- [ ] Ejecutar `smoke-test.sh` end-to-end con el stack completo
- [ ] Actualizar `task-definition.json` al stack real (Python/FastAPI/PostgreSQL)

---

## 9. Stack Tecnológico DevOps

| Herramienta | Uso |
|---|---|
| Docker + Docker Compose | Contenerización y orquestación local |
| GitHub Actions | CI/CD |
| AWS ECS Fargate + ECR + RDS | Deploy de producción |
| AWS Secrets Manager | Gestión de secretos |
| TruffleHog | Escaneo de secretos filtrados |
| PostgreSQL 16 | Base de datos |
| Make | Automatización de comandos |
| Bash | Scripts de infra y smoke tests |

---

*Documento generado el 2026-09-03 por el rol QA/DevOps del proyecto EcoMatch.*
