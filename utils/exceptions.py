from fastapi import HTTPException
from typing import Optional


class AnalysisError(Exception):
    """Excepción base para errores de análisis"""
    pass


class ImageProcessingError(AnalysisError):
    """Error en procesamiento de imagen"""
    pass


class AIServiceError(AnalysisError):
    """Error en servicio de IA"""
    pass


class ValidationError(AnalysisError):
    """Error de validación"""
    pass


def create_http_exception(
    status_code: int,
    message: str,
    error_type: Optional[str] = None
) -> HTTPException:
    """Crear HTTPException estandarizada"""
    detail = {
        "message": message,
        "error_type": error_type or "general_error",
        "status_code": status_code
    }

    return HTTPException(status_code=status_code, detail=detail)
