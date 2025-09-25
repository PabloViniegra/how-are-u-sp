from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings
import logging

logger = logging.getLogger(__name__)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={
        "check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

Base = declarative_base()

metadata = MetaData()
metadata.create_all(engine)


def create_tables():
    """
    Crear todas las tablas
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tablas de base de datos creadas correctamente")
    except Exception as e:
        logger.error(f"Error creando tablas: {str(e)}")
        raise


def get_db():
    """
    Dependency para obtener sesión de base de datos
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Error en sesión de base de datos: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()
