"""
Script para iniciar el servidor de desarrollo
"""

from config import settings
from utils.logging_config import setup_logging
import os
import sys
import uvicorn
from pathlib import Path

# Agregar el directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """Función principal para iniciar el servidor"""

    # Configurar logging
    setup_logging(
        level="INFO" if not settings.DEBUG else "DEBUG",
        log_file="logs/app.log" if os.path.exists("logs") else None
    )

    # Verificar configuración crítica
    if not settings.GOOGLE_AI_API_KEY:
        print("❌ ERROR: GOOGLE_AI_API_KEY no configurada")
        print("   1. Obtén tu clave gratuita en: https://makersuite.google.com/app/apikey")
        print("   2. Copia el archivo .env.example a .env")
        print("   3. Configura tu clave en el archivo .env")
        sys.exit(1)

    print("🚀 Iniciando Facial Analysis API...")
    print(f"📊 Documentación: http://localhost:8000/docs")
    print(f"🔍 Health Check: http://localhost:8000/api/health")
    print(f"🧪 Debug Mode: {'ON' if settings.DEBUG else 'OFF'}")

    # Configuración del servidor
    server_config = {
        "app": "main:app",
        "host": "0.0.0.0",
        "port": 8000,
        "reload": settings.DEBUG,
        "log_level": "info",
        "access_log": True,
        "workers": 1,  # Importante: solo 1 worker para SQLite
    }

    try:
        uvicorn.run(**server_config)
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
