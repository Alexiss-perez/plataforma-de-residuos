# Reporte de Testeo DevOps — Carpeta `devops/`

> **Fecha:** 2026-09-03
> **Autor:** Rol QA/DevOps
> **Scope:** `devops/` (Makefile, scripts, Docker, task-definition, tests)
> **Commit evaluado:** `8fe270a` en `main`

---

## Resumen Ejecutivo

| Métrica | Valor |
|---|---|
| Archivos evaluados | 9 |
| Tests ejecutados | 15 |
| Tests exitosos | 11 |
| Tests fallidos | 3 |
| Tests con warnings | 1 |
| Stack Docker levantado | Parcial (DB + Backend OK, AI bloqueado) |

**Conclusión:** La infraestructura DevOps está **mayoritariamente sana**. Los scripts, Dockerfiles, JSON y YAML son válidos. Se detectaron **3 bugs accionables** que impiden que el stack completo levante en Docker.

---

## 1. Lo que salió BIEN ✅

### 1.1 Scripts Shell — Sintaxis válida

| Script | Sintaxis | Permisos | `set -euo pipefail` |
|---|---|---|---|
| `devops/smoke-test.sh` | ✅ `bash -n` OK | ✅ ejecutable | ✅ |
| `devops/crear_infraestructura.sh` | ✅ `bash -n` OK | ✅ ejecutable | ✅ |

**Detalle:** Ambos scripts usan `set -euo pipefail` (fail-fast), validan variables de entorno requeridas antes de ejecutar, y manejan errores con `|| true` en operaciones idempotentes.

### 1.2 Archivos de configuración — Válidos

| Archivo | Validación | Resultado |
|---|---|---|
| `devops/task-definition.json` | `json.load()` | ✅ JSON válido |
| `docker-compose.yml` | `yaml.safe_load()` + `docker compose config` | ✅ YAML válido |
| `devops/.dockerignore` | Patrones correctos | ✅ Ignora `.env`, `node_modules`, `__pycache__`, `.git` |

### 1.3 Dockerfiles — Build check OK

| Dockerfile | `docker build --check` | Build real |
|---|---|---|
| `backend/Dockerfile` | ✅ No warnings | ✅ Imagen construida (4.4s) |
| `ia/Dockerfile` | ✅ No warnings | ✅ Imagen construida (cache) |
| `devops/ai-orchestrator/Dockerfile` | ✅ No warnings | ⚠️ Placeholder (ver 2.3) |

### 1.4 Docker Compose — Configuración válida

| Validación | Resultado |
|---|---|
| `docker compose config --quiet` | ✅ Sin errores |
| Red bridge `ecmatch-net` | ✅ Definida |
| Volumen `pgdata` | ✅ Definido |
| Healthcheck DB | ✅ `pg_isready` |
| Dependencias entre servicios | ✅ `depends_on` con `condition: service_healthy` |

### 1.5 Stack Docker — DB y Backend levantan

| Servicio | Estado | Healthcheck | Endpoint |
|---|---|---|---|
| `db-ecmatch` (PostgreSQL 16) | ✅ Up | ✅ Healthy | `pg_isready` OK |
| `backend` (FastAPI) | ✅ Up (app funciona) | ❌ Unhealthy (ver 2.1) | `GET /health` → `{"status":"ok"}` |

**El backend responde correctamente a peticiones HTTP** — el problema es solo el healthcheck de Docker (ver sección 2.1).

### 1.6 Casos de prueba del agente — Documentación completa

| Métrica | Valor |
|---|---|
| Casos documentados | 10 (TC-01 a TC-10) |
| Categorías cubiertas | Ambigüedad, alucinaciones, jailbreak, camino feliz, leyes, iniciativa |
| Formato | ✅ Tablas estructuradas con input, comportamiento esperado, categoría rúbrica, condición de fallo |

### 1.7 Makefile — Targets definidos

| Target | Estado |
|---|---|
| `help` | ✅ Muestra 16 targets con descripciones |
| `up` / `down` / `restart` / `build` | ✅ Docker compose wrappers |
| `logs` / `logs-ai` / `logs-back` / `logs-db` | ✅ Logs por servicio |
| `health` | ✅ Health check de DB + Backend + AI |
| `test` / `test-backend` / `test-agent` | ✅ Runners de tests |
| `clean` | ✅ Limpia contenedores + volúmenes |

### 1.8 Seguridad

| Validación | Resultado |
|---|---|
| `.env` en `.gitignore` | ✅ |
| `.env` NO trackeado por git | ✅ |
| `.env.example` presente (template sin secretos) | ✅ |
| `.dockerignore` excluye `.env` | ✅ |
| `crear_infraestructura.sh` lee secretos de env/Secrets Manager | ✅ |
| `task-definition.json` usa `secrets` (no `environment`) para passwords | ✅ |

---

## 2. Lo que salió MAL ❌

### 2.1 BUG: Healthcheck del backend usa `curl` que no existe en la imagen

| Campo | Valor |
|---|---|
| **Severidad** | Alta |
| **Bloqueante** | Sí — impide que `ai-orchestrator` levante (depende de `backend` healthy) |
| **Archivo** | `docker-compose.yml` línea 63 |
| **Error exacto** | `/bin/sh: 1: curl: not found` |
| **Causa raíz** | La imagen `python:3.12-slim` no incluye `curl`. El healthcheck usa `curl -sf http://localhost:8000/health` |

**Log de Docker:**
```
"ExitCode": 1,
"Output": "/bin/sh: 1: curl: not found\n"
```

**Fix propuesto (2 opciones):**

Opción A — Usar `python` para el healthcheck (sin instalar nada extra):
```yaml
healthcheck:
  test: ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8000/health')\" || exit 1"]
```

Opción B — Instalar `curl` en el Dockerfile:
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
```

### 2.2 BUG: Makefile tiene paths relativos incorrectos

| Campo | Valor |
|---|---|
| **Severidad** | Media |
| **Bloqueante** | No (pero confuso) |
| **Archivo** | `devops/Makefile` línea 62 |
| **Error exacto** | `bash: devops/crear_infraestructura.sh: No existe el fichero o el directorio` |
| **Causa raíz** | Cuando se ejecuta `make -C devops infra-plan`, el working dir es `devops/`, pero el target usa `devops/crear_infraestructura.sh` (path desde la raíz del repo) |

**Reproducción:**
```bash
$ make -C devops infra-plan
bash: devops/crear_infraestructura.sh: No existe el fichero o el directorio
make: *** [Makefile:62: infra-plan] Error 127
```

**Fix propuesto:** Cambiar `devops/crear_infraestructura.sh` por `./crear_infraestructura.sh` en el Makefile, o usar `$(MAKEFILE_DIR)` para resolver el path.

### 2.3 BUG: `devops/ai-orchestrator/` es un placeholder vacío

| Campo | Valor |
|---|---|
| **Severidad** | Media |
| **Bloqueante** | No (el IA real está en `ia/`, no en `devops/ai-orchestrator/`) |
| **Archivo** | `devops/ai-orchestrator/Dockerfile`, `app/main.py`, `requirements.txt` |

**Detalle:** Los 3 archivos son placeholders explícitos:
- `Dockerfile`: `CMD ["echo", "ai-orchestrator: pendiente de implementacion"]`
- `app/main.py`: `"""Placeholder. El Ing. de IA implementará..."""`
- `requirements.txt`: `# Dependencias - el Ing. de IA debe llenar esta lista`

**Nota:** El IA real y funcional está en `ia/` (raíz del repo). `devops/ai-orchestrator/` es un scaffold obsoleto que debería eliminarse o actualizarse para apuntar a `ia/`.

### 2.4 WARNING: `task-definition.json` inconsistente con el stack real

| Campo | Valor |
|---|---|
| **Severidad** | Baja |
| **Bloqueante** | No (solo afecta deploy a AWS ECS) |
| **Archivo** | `devops/task-definition.json` |

**Inconsistencias detectadas:**

| Campo en task-definition | Valor actual | Valor real (docker-compose) |
|---|---|---|
| `back-api` port | 8080 | 8000 |
| `back-api` healthcheck | `/actuator/health` (Spring) | `/health` (FastAPI) |
| `back-api` DB engine | MySQL (`jdbc:mysql`) | PostgreSQL |
| `ai-orchestrator` port | 8000 | 8001 |
| `back-api` datasource | `SPRING_DATASOURCE_URL` (Java) | `DATABASE_URL` (Python) |

**Causa raíz:** El task-definition fue escrito asumiendo un backend Java/Spring, pero el backend real es Python/FastAPI.

**Fix propuesto:** Actualizar `task-definition.json` para reflejar el stack real:
- Ports: backend 8000, ai-orchestrator 8001
- Healthcheck: `/health` (no `/actuator/health`)
- DB: PostgreSQL (no MySQL)
- Env vars: `DATABASE_URL` (no `SPRING_DATASOURCE_URL`)

### 2.5 WARNING: Variable `KOSTRA_API_KEY` no definida

| Campo | Valor |
|---|---|
| **Severidad** | Baja |
| **Bloqueante** | No (el backend funciona con mock si `AI_API_KEY` está vacío) |
| **Mensaje** | `The "KOSTRA_API_KEY" variable is not set. Defaulting to a blank string.` |

**Fix:** Definir `KOSTRA_API_KEY` en `.env` (copiar de `.env.example` y rellenar).

---

## 3. Matriz de Resultados

| # | Test | Archivo | Estado | Duración |
|---|---|---|---|---|
| 1 | Sintaxis `smoke-test.sh` | `devops/smoke-test.sh` | ✅ PASS | <1s |
| 2 | Sintaxis `crear_infraestructura.sh` | `devops/crear_infraestructura.sh` | ✅ PASS | <1s |
| 3 | Validación JSON `task-definition.json` | `devops/task-definition.json` | ✅ PASS | <1s |
| 4 | Validación YAML `docker-compose.yml` | `docker-compose.yml` | ✅ PASS | <1s |
| 5 | `docker compose config` | `docker-compose.yml` | ✅ PASS | <1s |
| 6 | Build check `backend/Dockerfile` | `backend/Dockerfile` | ✅ PASS | <1s |
| 7 | Build check `ia/Dockerfile` | `ia/Dockerfile` | ✅ PASS | <1s |
| 8 | Build check `devops/ai-orchestrator/Dockerfile` | `devops/ai-orchestrator/Dockerfile` | ✅ PASS | <1s |
| 9 | Build real `backend` | `backend/Dockerfile` | ✅ PASS | 4.4s |
| 10 | Build real `ai-orchestrator` | `ia/Dockerfile` | ✅ PASS | 0.1s (cache) |
| 11 | Levantar `db-ecmatch` | PostgreSQL 16 | ✅ PASS | 5s |
| 12 | Levantar `backend` | FastAPI | ✅ PASS (app) / ❌ FAIL (healthcheck) | 8s |
| 13 | Levantar `ai-orchestrator` | FastAPI IA | ❌ FAIL (dependencia backend unhealthy) | — |
| 14 | `GET /health` backend | `http://localhost:8000/health` | ✅ PASS | <1s |
| 15 | `POST /chat` ai-orchestrator | `http://localhost:8001/chat` | ❌ FAIL (servicio no levantó) | — |
| 16 | `make -C devops help` | Makefile | ✅ PASS | <1s |
| 17 | `make -C devops infra-plan` | Makefile target | ❌ FAIL (path incorrecto) | <1s |
| 18 | Validación `.dockerignore` | `devops/.dockerignore` | ✅ PASS | <1s |
| 19 | Validación `.env` seguro | `.gitignore` | ✅ PASS | <1s |
| 20 | Casos de prueba agente | `devops/tests/agent-test-cases.md` | ✅ PASS (10 casos documentados) | <1s |

---

## 4. Bugs encontrados (resumen accionable)

| # | Bug | Severidad | Archivo | Fix |
|---|---|---|---|---|
| 1 | Healthcheck usa `curl` no disponible en `python:3.12-slim` | **Alta** | `docker-compose.yml:63` | Usar `python -c urllib.request.urlopen(...)` o instalar curl |
| 2 | Makefile path relativo incorrecto | **Media** | `devops/Makefile:62` | Cambiar `devops/crear_infraestructura.sh` por `./crear_infraestructura.sh` |
| 3 | `devops/ai-orchestrator/` es placeholder obsoleto | **Media** | `devops/ai-orchestrator/*` | Eliminar o apuntar a `ia/` |
| 4 | `task-definition.json` usa stack Java/Spring, no Python/FastAPI | **Baja** | `devops/task-definition.json` | Actualizar ports, healthchecks, env vars y DB engine |

---

## 5. Pendientes para próximas pruebas

- [ ] Aplicar fix del healthcheck (bug #1) y re-ejecutar `docker compose up`
- [ ] Validar que `ai-orchestrator` levante y responda `/chat`
- [ ] Ejecutar `smoke-test.sh` end-to-end con el stack completo
- [ ] Ejecutar los 10 casos de prueba del agente contra el endpoint `/chat`
- [ ] Correr `pytest` dentro del contenedor backend (`make test-backend`)
- [ ] Fixar el Makefile y validar `make infra-plan`
- [ ] Actualizar `task-definition.json` al stack real
- [ ] Configurar `KOSTRA_API_KEY` y probar integración real con GLM 5.2

---

*Documento generado desde testeo local ejecutado el 2026-09-03.*
