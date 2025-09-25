"""
Aplicación FastAPI para análisis facial
Organizada con routers y siguiendo mejores prácticas
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import google.generativeai as genai
import logging
from datetime import datetime

from database import engine, Base
from config import settings
from routers import analysis, stats, health

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear tablas de base de datos
Base.metadata.create_all(bind=engine)

# Configurar Google AI usando settings (que ya carga el .env)
genai.configure(api_key=settings.GOOGLE_AI_API_KEY)

# Metadatos de la aplicación
app_metadata = {
    "title": "Facial Analysis API",
    "description": """
    API segura para análisis facial que requiere autenticación por API key.

    ## Características principales:

    * **Análisis facial avanzado** - Evaluación completa de atractivo facial
    * **Seguridad robusta** - Autenticación por API key obligatoria
    * **Estadísticas detalladas** - Métricas y distribuciones de análisis
    * **Arquitectura modular** - Organizada con routers FastAPI

    ## Autenticación:

    Todos los endpoints (excepto `/health`) requieren autenticación mediante:
    - Header `X-API-Key: tu_api_key`
    - Bearer token `Authorization: Bearer tu_api_key`
    """,
    "version": "2.0.0",
    "contact": {
        "name": "Facial Analysis API",
        "email": "contact@facial-analysis.com"
    },
    "license_info": {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    "docs_url": "/docs",
    "redoc_url": "/redoc"
}

# Crear aplicación FastAPI
app = FastAPI(**app_metadata)

# Configurar CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Incluir routers con prefijo API
API_PREFIX = "/api"

app.include_router(
    analysis.router,
    prefix=API_PREFIX,
    responses={404: {"description": "No encontrado"}}
)

app.include_router(
    stats.router,
    prefix=API_PREFIX,
    responses={404: {"description": "No encontrado"}}
)

app.include_router(
    health.router,
    prefix=API_PREFIX,
    responses={404: {"description": "No encontrado"}}
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Manejador global de excepciones para respuestas consistentes
    """
    logger.error(f"❌ Excepción no manejada: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error interno del servidor",
            "timestamp": datetime.utcnow().isoformat(),
            "type": "internal_server_error"
        }
    )


@app.on_event("startup")
async def startup_event():
    """
    Eventos de inicio de la aplicación
    """
    logger.info("🚀 Iniciando Facial Analysis API v2.0.0")
    logger.info(f"📊 Base de datos: {settings.DATABASE_URL}")
    logger.info(f"🤖 Modelo AI: {settings.AI_MODEL_NAME}")
    logger.info(f"🔒 API Keys configuradas: {len(settings.get_api_keys_list())}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Eventos de cierre de la aplicación
    """
    logger.info("🛑 Cerrando Facial Analysis API")


@app.get("/", tags=["root"])
async def root():
    """
    Endpoint raíz con información de la API
    """
    return {
        "message": "Bienvenido a Facial Analysis API v2.0.0",
        "documentation": "/docs",
        "health_check": "/api/health",
        "status": "operational",
        "features": [
            "Análisis facial avanzado",
            "Autenticación por API key",
            "Estadísticas detalladas",
            "Arquitectura modular"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )