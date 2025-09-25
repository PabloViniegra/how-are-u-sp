from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Dict, Optional, List
from enum import Enum
import re


class AnalysisStatusEnum(str, Enum):
    """
    Estados posibles del análisis facial
    """
    DENIED = "denied"
    IMPROVABLE = "improvable"
    FEASIBLE = "feasible"


class AnalysisCreate(BaseModel):
    """
    Schema para crear un nuevo análisis
    """
    filename: str = Field(..., min_length=1, max_length=255)
    overall_score: float = Field(..., ge=0, le=10)
    symmetry_score: float = Field(..., ge=0, le=10)
    proportion_score: float = Field(..., ge=0, le=10)
    skin_quality_score: float = Field(..., ge=0, le=10)
    features_harmony_score: float = Field(..., ge=0, le=10)
    scientific_explanation: str = Field(..., min_length=50, max_length=2000)
    recommendations: str = Field(..., min_length=50, max_length=2000)

    @validator('filename')
    def validate_filename(cls, v):
        # Sanitizar nombre de archivo
        if not re.match(r'^[\w\-. ]+\.(jpg|jpeg|png|webp)$', v.lower()):
            raise ValueError('Nombre de archivo no válido')
        return v

    @validator('scientific_explanation', 'recommendations')
    def validate_text_content(cls, v):
        # Verificar que el contenido sea útil
        if len(v.strip()) < 50:
            raise ValueError('El contenido debe ser más descriptivo')
        return v.strip()


class AnalysisResponse(BaseModel):
    """
    Schema para la respuesta del análisis
    """
    id: str
    status: AnalysisStatusEnum
    overall_score: float = Field(..., ge=0, le=10)
    detailed_scores: Dict[str, float] = Field(...)
    additional_scores: Optional[Dict[str, float]] = Field(default=None)
    scientific_explanation: str
    recommendations: str
    analysis_date: datetime

    @validator('detailed_scores')
    def validate_detailed_scores(cls, v):
        required_keys = {'symmetry', 'proportions',
                         'skin_quality', 'features_harmony'}
        if not required_keys.issubset(v.keys()):
            raise ValueError('Faltan puntuaciones detalladas')

        for key, score in v.items():
            if not 0 <= score <= 10:
                raise ValueError(f'Puntuación {key} fuera de rango (0-10)')

        return v

    @validator('additional_scores')
    def validate_additional_scores(cls, v):
        if v is not None:
            for key, score in v.items():
                if not 0 <= score <= 10:
                    raise ValueError(f'Puntuación adicional {key} fuera de rango (0-10)')
        return v

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class HealthResponse(BaseModel):
    """
    Schema para el health check
    """
    status: str
    message: str
    database: str
    ai_service: str
    timestamp: str


class StatsResponse(BaseModel):
    """
    Schema para estadísticas
    """
    total_analyses: int = Field(..., ge=0)
    average_score: float = Field(..., ge=0, le=10)
    score_distribution: Dict[str, int] = Field(...)


class AnalysisListItem(BaseModel):
    """
    Schema para elemento en lista de análisis
    """
    id: str
    overall_score: float = Field(..., ge=0, le=10)
    analysis_date: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorResponse(BaseModel):
    """
    Schema para respuestas de error
    """
    detail: str
    timestamp: Optional[str] = None
    error_code: Optional[str] = None
