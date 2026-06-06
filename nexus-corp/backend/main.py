"""
Nexus-Corp KBDSS API
Knowledge-Based Decision Support System for Logistics & Tech Distribution

Main application entry point.
"""

import asyncio
import threading
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.logging_config import get_logger, setup_logging
from infrastructure.database.connection import create_tables
from presentation.api.v1.router import api_router

# Initialize logging first
setup_logging()
logger = get_logger(__name__)


def create_application() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title=settings.APP_NAME,
        description=(
            "Sistema de Soporte a Decisiones Basado en Conocimiento (KBDSS) "
            "para empresas de logística y distribución tecnológica. "
            "Implementa un motor de reglas forward-chaining para generar "
            "recomendaciones inteligentes a partir de escenarios operacionales."
        ),
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        contact={
            "name": "Nexus-Corp Dev Team",
            "email": "dev@nexuscorp.com",
        },
        license_info={
            "name": "Proprietary",
        },
    )

    # ─── CORS Middleware ────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins + ["*"],  # Permissive in dev
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ─── Routers ────────────────────────────────────────────────────────────
    app.include_router(api_router)

    # ─── Startup / Shutdown Events ──────────────────────────────────────────
    @app.on_event("startup")
    async def startup_event():
        logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
        # Run table creation in background thread to avoid blocking startup
        # (Neon serverless DB may have cold-start delay on first connection)
        def _init_db():
            try:
                create_tables()
                logger.info("Database ready.")
            except Exception as e:
                logger.error(f"Database initialization failed: {e}", exc_info=True)

        thread = threading.Thread(target=_init_db, daemon=True)
        thread.start()

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info(f"{settings.APP_NAME} shutting down.")

    # ─── Health Check ────────────────────────────────────────────────────────
    @app.get("/health", tags=["Health"], summary="Health check")
    def health_check():
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
        }

    @app.get("/", tags=["Root"], summary="Root")
    def root():
        return {
            "message": f"Bienvenido a {settings.APP_NAME}",
            "docs": "/docs",
            "version": settings.APP_VERSION,
        }

    return app


app = create_application()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
