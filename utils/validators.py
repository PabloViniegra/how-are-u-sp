import re
import magic


class ImageValidator:
    """
    Validador de imágenes con múltiples métodos de verificación
    """

    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
    ALLOWED_MIME_TYPES = {
        'image/jpeg', 'image/jpg', 'image/png', 'image/webp'
    }
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MIN_DIMENSIONS = (200, 200)
    MAX_DIMENSIONS = (4000, 4000)

    @classmethod
    def validate_file_extension(cls, filename: str) -> bool:
        """Valida extensión del archivo"""
        if not filename:
            return False

        extension = '.' + filename.lower().split('.')[-1]
        return extension in cls.ALLOWED_EXTENSIONS

    @classmethod
    def validate_mime_type(cls, file_content: bytes) -> bool:
        """Valida tipo MIME usando magic numbers"""
        try:
            mime_type = magic.from_buffer(file_content, mime=True)
            return mime_type in cls.ALLOWED_MIME_TYPES
        except:
            return True

    @classmethod
    def validate_file_size(cls, file_size: int) -> bool:
        """Valida tamaño del archivo"""
        return 0 < file_size <= cls.MAX_FILE_SIZE

    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """Sanitiza nombre del archivo"""
        if not filename:
            return "unknown.jpg"

        filename = re.sub(r'[^\w\-_\.]', '_', filename)

        if len(filename) > 100:
            name, ext = filename.rsplit('.', 1)
            filename = name[:95] + '.' + ext

        return filename


def validate_score_range(score: float, field_name: str) -> float:
    """Valida que la puntuación esté en el rango 0-10"""
    if not isinstance(score, (int, float)):
        raise ValueError(f"{field_name} debe ser un número")

    if not 0 <= score <= 10:
        raise ValueError(f"{field_name} debe estar entre 0 y 10")

    return round(float(score), 1)


def validate_analysis_text(text: str, field_name: str, min_length: int = 50) -> str:
    """Valida texto de análisis"""
    if not isinstance(text, str):
        raise ValueError(f"{field_name} debe ser texto")

    text = text.strip()

    if len(text) < min_length:
        raise ValueError(
            f"{field_name} debe tener al menos {min_length} caracteres")

    if len(text) > 2000:
        raise ValueError(f"{field_name} no puede exceder 2000 caracteres")

    return text
