from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Index, Enum
from sqlalchemy.sql import func
from database import Base
import enum


class AnalysisStatus(enum.Enum):
    """
    Estados posibles del análisis facial
    """
    DENIED = "denied"  # Imagen claramente no válida (no es una cara)
    IMPROVABLE = "improvable"  # Es una cara pero calidad insuficiente
    FEASIBLE = "feasible"  # Imagen válida y de calidad para análisis


class AnalysisResult(Base):
    """
    Modelo para almacenar los resultados de análisis facial
    """
    __tablename__ = "analysis_results"

    # Campos principales
    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False, index=True)

    # Puntuaciones principales (0-10)
    overall_score = Column(Float, nullable=False, index=True)
    symmetry_score = Column(Float, nullable=False)
    proportion_score = Column(Float, nullable=False)
    skin_quality_score = Column(Float, nullable=False)
    features_harmony_score = Column(Float, nullable=False)

    # Estado del análisis
    analysis_status = Column(Enum(AnalysisStatus), nullable=False, default=AnalysisStatus.FEASIBLE, index=True)

    # Puntuaciones detalladas adicionales (0-10)
    eye_appeal_score = Column(Float, nullable=True)  # Atractivo de los ojos
    nose_harmony_score = Column(Float, nullable=True)  # Armonía nasal
    lip_aesthetics_score = Column(Float, nullable=True)  # Estética labial
    jawline_definition_score = Column(Float, nullable=True)  # Definición mandibular
    cheekbone_prominence_score = Column(Float, nullable=True)  # Prominencia pómulos
    facial_composition_score = Column(Float, nullable=True)  # Composición general

    # Análisis textual
    scientific_explanation = Column(Text, nullable=False)
    recommendations = Column(Text, nullable=False)

    # Metadatos
    created_at = Column(DateTime, default=func.now(),
                        nullable=False, index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Campos adicionales para futuras funcionalidades
    user_ip = Column(String, nullable=True)  # Para estadísticas anónimas
    processing_time = Column(Float, nullable=True)  # Tiempo de procesamiento
    ai_model_version = Column(String, default="gemini-1.5-flash")

    # Índices compuestos para optimizar consultas
    __table_args__ = (
        Index('ix_analysis_created_score', 'created_at', 'overall_score'),
        Index('ix_analysis_filename_created', 'filename', 'created_at'),
    )

    def __repr__(self):
        return f"<AnalysisResult(id='{self.id}', overall_score={self.overall_score}, created_at='{self.created_at}')>"

    def to_dict(self):
        """
        Convertir a diccionario para serialización
        """
        return {
            'id': self.id,
            'filename': self.filename,
            'overall_score': self.overall_score,
            'symmetry_score': self.symmetry_score,
            'proportion_score': self.proportion_score,
            'skin_quality_score': self.skin_quality_score,
            'features_harmony_score': self.features_harmony_score,
            'scientific_explanation': self.scientific_explanation,
            'recommendations': self.recommendations,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class AnalysisStats(Base):
    """
    Modelo para almacenar estadísticas agregadas (opcional para optimización)
    """
    __tablename__ = "analysis_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, default=func.now(), nullable=False, index=True)
    total_analyses = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)
    max_score = Column(Float, default=0.0)
    min_score = Column(Float, default=0.0)

    def __repr__(self):
        return f"<AnalysisStats(date='{self.date}', total={self.total_analyses})>"
