# Guía de Contribución — EcoMatch

## Flujo de trabajo (obligatorio)

1. **Nadie programa en `main`.** Toda tarea se hace en una rama.
2. Crea una rama desde `main` con naming convencional:
   - `feature/descripcion` — nueva funcionalidad
   - `bugfix/descripcion` — corrección de error
   - `devops/descripcion` — infraestructura, CI/CD, Docker
   - `test/descripcion` — casos de prueba
   - `docs/descripcion` — documentación
3. Abre un **Pull Request** a `main`.
4. El PR requiere **mínimo 1 approval** y que **CI pase**.
5. Solo se hace merge después de aprobado.

## Reglas de seguridad

- **NUNCA** commitear `.env`, API keys, contraseñas, ni tokens.
- Usar `.env.example` como template; el `.env` real se mantiene local.
- Secretos de producción van en **GitHub Secrets** o **AWS Secrets Manager**.
- Si descubres un secreto commiteado por error, **no hagas push**. Notifica al equipo y rota la credencial.

## Estructura del monorepo

```
front-web/           # Frontend (React/Vite)
back-api/            # Backend API REST
ai-orchestrator/     # Capa IA GLM 5.2 (Python/FastAPI)
infra/               # Infraestructura como código
tests/               # Casos de prueba del agente
.github/workflows/   # CI/CD
```

## Comandos locales

```bash
make up        # Levantar todo el stack con Docker
make down      # Bajar el stack
make logs      # Ver logs
make test      # Correr tests
make lint      # Linting
```
