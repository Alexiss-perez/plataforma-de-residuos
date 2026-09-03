# ReVínculo — Backend

> Red social web de economía circular.  
> *"Lo que para ti sobra, para alguien puede construir algo."*

ReVínculo conecta personas naturales, recolectores especializados y organizaciones (fundaciones / ONG / talleres) para facilitar la reutilización de materiales mediante un flujo: publicación → análisis IA → matching → retiro → reutilización → registro de impacto.

## Requisitos

- Python 3.12+
- PostgreSQL 16+ (para desarrollo/producción)
- pip / venv

## Instalación

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
```

## Variables de entorno

Copia `.env.example` a `.env` y ajusta:

```bash
cp .env.example .env
```

| Variable | Descripción | Default |
|---|---|---|
| `DATABASE_URL` | URL de PostgreSQL | `postgresql+psycopg://revinculo:revinculo@localhost:5432/revinculo` |
| `JWT_SECRET` | Secreto para JWT | `change-me` |
| `JWT_ALGORITHM` | Algoritmo JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiración token | `1440` |
| `CORS_ORIGINS` | Orígenes CORS (comma-separated) | `http://localhost:5173` |
| `AI_BASE_URL` | URL API LLM | `https://ai.kostra.cloud/v1` |
| `AI_API_KEY` | API key LLM (vacío = mock) | `` |
| `AI_MODEL` | Modelo LLM | `glm-5.2` |
| `STORAGE_PROVIDER` | `local` o `huawei_obs` | `local` |
| `OBS_ACCESS_KEY` | Huawei OBS key | `` |
| `OBS_SECRET_KEY` | Huawei OBS secret | `` |
| `OBS_BUCKET` | Huawei OBS bucket | `` |
| `OBS_ENDPOINT` | Huawei OBS endpoint | `` |

> **Tests** usan SQLite in-memory automáticamente — no requieren PostgreSQL.

## Levantar PostgreSQL

```bash
docker compose up -d postgres
# o instalar PostgreSQL localmente
```

## Migraciones

```bash
alembic upgrade head
```

## Ejecutar backend

```bash
uvicorn app.main:app --reload
```

Swagger: http://localhost:8000/docs  
ReDoc: http://localhost:8000/redoc

## Ejecutar tests

```bash
pytest -v
```

## Seed (datos de demostración)

```bash
python scripts/seed.py
```

Genera: 1 admin, 10 personas naturales, 8 recolectores, 5 organizaciones, 4 proyectos, 20 publicaciones, 20 materiales (incluye material peligroso), 12 necesidades.

## Docker

```bash
docker compose up --build
```

Levanta PostgreSQL + backend en http://localhost:8000

## Arquitectura

Monolito modular:

```
app/
├── core/          # config, database, security, exceptions
├── models/        # SQLAlchemy 2.x models + enums
├── schemas/       # Pydantic v2 schemas
├── repositories/  # Capa de acceso a datos
├── services/      # Lógica de negocio
├── api/routes/    # Endpoints FastAPI
├── agents/        # EcoMatchAgent (IA desacoplada)
└── utils/         # distance, hazardous
```

### Roles

| Rol | Descripción |
|---|---|
| `NATURAL` | Persona natural — puede donar/publicar/solicitar |
| `COLLECTOR` | Recolector especializado — tiene perfil con vehículo, capacidad, radio |
| `ORGANIZATION` | Fundación/ONG/Taller — publica proyectos y necesidades |
| `ADMIN` | Administrador |

Una persona `NATURAL` con `can_collect=true` puede actuar como recolector ocasional.

### EcoMatchAgent

Agente IA desacoplado que usa GLM-5.2 (o cualquier API compatible con OpenAI). Capacidades:

1. **Análisis de material** — clasifica texto libre en categoría/condición/riesgo
2. **Interpretación de necesidad** — extrae material/cantidad de texto natural
3. **Explicación de match** — justifica por qué un match es bueno
4. **Detección de ambigüedad** — identifica información faltante
5. **Gestión de contingencia** — propone recolector de reemplazo

**Prevención de alucinación:** el LLM nunca escribe directamente en la DB. Toda acción pasa por `AgentTools` → servicios → validaciones.

### Motor de matching determinístico

Score 0-100 con ponderaciones:
- Compatibilidad material: 40%
- Cantidad: 20%
- Distancia (Haversine): 20%
- Prioridad: 10%
- Condición: 10%

### Privacidad de ubicación

Las coordenadas exactas solo son visibles para: dueño, recolector asignado, organización involucrada, admin. El feed público muestra solo comuna.

### Materiales peligrosos

Detección automática por keywords (asbesto, químico, combustible, etc.). Bloqueo de matching automático. Requieren `SPECIAL_HANDLING`.

## Endpoints

Ver http://localhost:8000/docs para la lista completa con tags: Auth, Users, Collectors, Organizations, Posts, Materials, Projects, Needs, Matches, Pickups, Impact, Notifications, AI, Health.

## Despliegue en Huawei Cloud

1. Configurar `STORAGE_PROVIDER=huawei_obs` con credenciales OBS
2. Usar RDS PostgreSQL de Huawei
3. `docker compose up --build` en CCE/ecs
