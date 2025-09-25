"""
Dependencias comunes de la aplicación
"""

from sqlalchemy.orm import Session
from database import SessionLocal


def get_db() -> Session:
    """
    Dependency para obtener una sesión de base de datos
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()