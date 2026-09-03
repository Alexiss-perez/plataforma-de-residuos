# ReVínculo — Red Social de Economía Circular

> *"Lo que para ti sobra, para alguien puede construir algo."*

ReVínculo es una plataforma que conecta **personas naturales**, **recolectores especializados** y **organizaciones** (fundaciones, ONG, talleres) para facilitar la reutilización de materiales mediante un flujo completo: publicación → análisis IA → matching → retiro → reutilización → registro de impacto.

## Actores

| Actor | Rol | Acciones |
|---|---|---|
| Persona natural | `NATURAL` | Donar/publicar materiales, solicitar retiros, actuar como recolector ocasional (`can_collect=true`) |
| Recolector especializado | `COLLECTOR` | Retiro de materiales con vehículo, capacidad y zona de operación |
| Fundación / ONG / Taller | `ORGANIZATION` | Publicar proyectos, indicar necesidades, recibir aportes, registrar impacto |
| Administrador | `ADMIN` | Acceso total |

## Flujo principal

```
Persona con material → Publicación → Análisis IA → Match con necesidad
→ Recolector → Retiro → Organización → Reutilización → Registro de impacto
```

## Stack

- **Python 3.12+** · **FastAPI** · **Pydantic v2** · **SQLAlchemy 2.x**
- **PostgreSQL** (producción) · **SQLite** (tests)
- **Alembic** (migraciones) · **JWT** (auth) · **bcrypt** (passwords)
- **pytest** + **TestClient** (tests) · **Uvicorn** (servidor)
- **EcoMatchAgent** — agente IA desacoplado compatible con GLM-5.2 vía API OpenAI-compatible

## Estructura

```
backend/
├── app/
│   ├── main.py              # FastAPI app + CORS + exception handlers
│   ├── core/                # config, database, security, exceptions
│   ├── models/              # SQLAlchemy 2.x models + enums
│   ├── schemas/             # Pydantic v2 schemas
│   ├── repositories/        # Capa de acceso a datos
│   ├── services/            # Lógica de negocio
│   ├── api/routes/          # Endpoints (14 routers)
│   ├── agents/              # EcoMatchAgent (IA desacoplada)
│   └── utils/               # Haversine, hazardous materials
├── alembic/                 # Migraciones
├── tests/                   # 58 tests
├── scripts/seed.py          # Datos de demostración
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Instalación

```bash
cd backend
python -m venv .venv
source .venv/bin/activate    # Linux/Mac
.venv\Scripts\activate       # Windows

pip install -r requirements.txt
cp .env.example .env
```

## Variables de entorno

| Variable | Descripción | Default |
|---|---|---|
| `DATABASE_URL` | URL PostgreSQL | `postgresql+psycopg://revinculo:revinculo@localhost:5432/revinculo` |
| `JWT_SECRET` | Secreto JWT | `change-me` |
| `JWT_ALGORITHM` | Algoritmo JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiración token | `1440` |
| `CORS_ORIGINS` | Orígenes CORS | `http://localhost:5173` |
| `AI_BASE_URL` | URL API LLM | `https://ai.kostra.cloud/v1` |
| `AI_API_KEY` | API key LLM (vacío = mock) | `` |
| `AI_MODEL` | Modelo LLM | `glm-5.2` |
| `STORAGE_PROVIDER` | `local` o `huawei_obs` | `local` |
| `OBS_ACCESS_KEY` | Huawei OBS key | `` |
| `OBS_SECRET_KEY` | Huawei OBS secret | `` |
| `OBS_BUCKET` | Huawei OBS bucket | `` |
| `OBS_ENDPOINT` | Huawei OBS endpoint | `` |

## Uso

```bash
# Levantar PostgreSQL
docker compose up -d postgres

# Migraciones
alembic upgrade head

# Seed (datos demo)
python scripts/seed.py

# Ejecutar backend
uvicorn app.main:app --reload

# Tests
pytest -v

# Docker completo
docker compose up --build
```

- **Swagger**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health**: http://localhost:8000/health

## Endpoints

| Tag | Endpoints |
|---|---|
| Auth | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` |
| Users | `GET /users/me`, `PATCH /users/me` |
| Collectors | `POST /collectors/profile`, `GET /collectors/profile/me`, `PATCH /collectors/profile/me`, `GET /collectors/available` |
| Organizations | `POST /organizations`, `GET /organizations`, `GET /organizations/{id}`, `PATCH /organizations/{id}` |
| Posts | `GET /posts`, `POST /posts`, `GET /posts/{id}`, `PATCH /posts/{id}`, `DELETE /posts/{id}` |
| Materials | `POST /materials`, `GET /materials`, `GET /materials/{id}`, `PATCH /materials/{id}` |
| Projects | `POST /projects`, `GET /projects`, `GET /projects/{id}`, `PATCH /projects/{id}` |
| Needs | `POST /needs`, `GET /needs`, `GET /needs/{id}`, `PATCH /needs/{id}` |
| Matches | `POST /matches/generate/{material_id}`, `GET /matches/material/{id}`, `GET /matches/need/{id}`, `POST /matches/{id}/accept`, `POST /matches/{id}/reject` |
| Pickups | `POST /pickups`, `GET /pickups/me`, `GET /pickups/{id}`, `POST /pickups/{id}/{accept,start,pickup,deliver,cancel}`, `GET /pickups/{id}/replacements` |
| Impact | `POST /impact`, `GET /impact`, `GET /impact/me`, `GET /impact/stats` |
| Notifications | `GET /notifications`, `POST /notifications/{id}/read` |
| AI | `POST /ai/analyze-material`, `POST /ai/interpret-need`, `POST /ai/explain-match`, `POST /ai/contingency`, `POST /ai/chat` |
| Health | `GET /health`, `GET /health/db` |

## Motor de matching

Score 0-100 con ponderaciones:

| Factor | Peso |
|---|---|
| Compatibilidad material | 40% |
| Cantidad | 20% |
| Distancia (Haversine) | 20% |
| Prioridad | 10% |
| Condición | 10% |

## EcoMatchAgent

Agente IA desacoplado que usa GLM-5.2 (o cualquier API OpenAI-compatible). Capacidades:

1. **Análisis de material** — clasifica texto libre en categoría/condición/riesgo
2. **Interpretación de necesidad** — extrae material/cantidad de texto natural
3. **Explicación de match** — justifica por qué un match es bueno
4. **Detección de ambigüedad** — identifica información faltante
5. **Gestión de contingencia** — propone recolector de reemplazo

**Prevención de alucinación**: el LLM nunca escribe directamente en la DB. Toda acción pasa por `AgentTools` → servicios → validaciones.

## Seguridad

- Contraseñas hasheadas con bcrypt · `password_hash` nunca expuesto en respuestas
- JWT con expiración configurable · auth requerida en todos los endpoints
- Autorización por rol (NATURAL / COLLECTOR / ORGANIZATION / ADMIN)
- Coordenadas/direcciones privadas solo visibles para participantes
- Materiales peligrosos bloquean matching automático
- Tests de seguridad horizontal (usuario A no puede acceder a recursos de usuario B)

## Despliegue (Huawei Cloud)

1. Configurar `STORAGE_PROVIDER=huawei_obs` con credenciales OBS
2. Usar RDS PostgreSQL de Huawei
3. `docker compose up --build` en CCE/ECS

## Licencia

MIT
