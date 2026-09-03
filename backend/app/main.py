from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import AppException
from app.api.routes import (
    ai,
    auth,
    collectors,
    health,
    impact,
    matches,
    materials,
    needs,
    notifications,
    organizations,
    pickups,
    posts,
    projects,
    users,
)
from app.integrations.osm.routes import router as osm_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="Red social de economía circular — backend",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {"exception": str(exc)},
                }
            },
        )

    api_prefix = "/api/v1"
    app.include_router(health.router, prefix=api_prefix)
    app.include_router(auth.router, prefix=api_prefix)
    app.include_router(users.router, prefix=api_prefix)
    app.include_router(collectors.router, prefix=api_prefix)
    app.include_router(organizations.router, prefix=api_prefix)
    app.include_router(posts.router, prefix=api_prefix)
    app.include_router(materials.router, prefix=api_prefix)
    app.include_router(projects.router, prefix=api_prefix)
    app.include_router(needs.router, prefix=api_prefix)
    app.include_router(matches.router, prefix=api_prefix)
    app.include_router(pickups.router, prefix=api_prefix)
    app.include_router(impact.router, prefix=api_prefix)
    app.include_router(notifications.router, prefix=api_prefix)
    app.include_router(ai.router, prefix=api_prefix)
    app.include_router(osm_router, prefix=api_prefix)

    @app.get("/health")
    def root_health():
        return {"status": "ok"}

    return app


app = create_app()
