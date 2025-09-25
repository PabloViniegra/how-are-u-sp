from PIL import Image, ImageEnhance, ImageOps, ImageFilter
import io
from typing import Tuple, Optional
import logging
from config import settings

logger = logging.getLogger(__name__)


class ImageProcessingService:
    """
    Servicio para procesamiento y optimización de imágenes
    """

    def __init__(self):
        self.max_size = (1024, 1024)
        self.min_size = (200, 200)
        self.quality = 85
        self.allowed_formats = {'JPEG', 'PNG', 'WEBP'}

    def process_image(self, image_bytes: bytes) -> bytes:
        """
        Procesa y optimiza la imagen para el análisis
        """
        try:
            logger.info("🖼️ Procesando imagen...")

            # Abrir y validar imagen
            image = Image.open(io.BytesIO(image_bytes))
            original_format = image.format
            original_size = image.size

            logger.info(
                f"📐 Imagen original: {original_size}, formato: {original_format}")

            # Validar formato
            if original_format not in self.allowed_formats:
                logger.warning(
                    f"⚠️ Formato no óptimo: {original_format}, convirtiendo a JPEG")

            # Convertir a RGB si es necesario
            if image.mode != 'RGB':
                logger.info(f"🔄 Convirtiendo de {image.mode} a RGB")
                # Preservar transparencia si existe
                if image.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'RGBA':
                        background.paste(image, mask=image.split()[-1])
                    else:
                        background.paste(image, mask=image.split()[-1])
                    image = background
                else:
                    image = image.convert('RGB')

            # Aplicar filtros de mejora
            image = self._enhance_image(image)

            # Redimensionar si es necesario
            if image.size != original_size:
                logger.info(f"📏 Redimensionando a: {image.size}")

            # Redimensionar manteniendo aspecto
            image = self._resize_image(image)

            # Optimizar para análisis facial
            image = self._optimize_for_facial_analysis(image)

            # Convertir de vuelta a bytes
            output_buffer = io.BytesIO()

            # Guardar con calidad optimizada
            save_kwargs = {
                'format': 'JPEG',
                'quality': self.quality,
                'optimize': True,
                'progressive': True
            }

            image.save(output_buffer, **save_kwargs)

            processed_bytes = output_buffer.getvalue()

            # Log estadísticas de procesamiento
            compression_ratio = len(processed_bytes) / len(image_bytes)
            logger.info(
                f"✅ Imagen procesada: {len(processed_bytes)} bytes (compresión: {compression_ratio:.2f})")

            return processed_bytes

        except Exception as e:
            logger.error(f"❌ Error procesando imagen: {str(e)}")
            raise Exception(f"Error procesando imagen: {str(e)}")

    def validate_image(self, image_bytes: bytes) -> bool:
        """
        Valida que la imagen sea válida y adecuada para análisis
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))

            # Verificar tamaño mínimo
            if image.size[0] < self.min_size[0] or image.size[1] < self.min_size[1]:
                logger.warning(f"❌ Imagen demasiado pequeña: {image.size}")
                return False

            # Verificar tamaño máximo
            if image.size[0] > 4000 or image.size[1] > 4000:
                logger.warning(f"❌ Imagen demasiado grande: {image.size}")
                return False

            # Verificar formato
            if image.format not in self.allowed_formats and image.format:
                logger.warning(f"⚠️ Formato no óptimo: {image.format}")
                # Aún válido, pero no óptimo

            # Verificar que no esté corrupta
            image.verify()

            # Verificar aspect ratio (no demasiado extremo)
            aspect_ratio = image.size[0] / image.size[1]
            if aspect_ratio > 3 or aspect_ratio < 0.33:
                logger.warning(f"⚠️ Aspect ratio extremo: {aspect_ratio}")
                return False

            logger.info(
                f"✅ Imagen válida: {image.size}, formato: {image.format}")
            return True

        except Exception as e:
            logger.error(f"❌ Error validando imagen: {str(e)}")
            return False

    def _resize_image(self, image: Image.Image) -> Image.Image:
        """
        Redimensiona la imagen manteniendo la relación de aspecto
        """
        original_size = image.size

        # Calcular nuevo tamaño manteniendo aspecto
        image.thumbnail(self.max_size, Image.Resampling.LANCZOS)

        # Si la imagen es muy pequeña, no redimensionar hacia arriba
        if original_size[0] < self.max_size[0] and original_size[1] < self.max_size[1]:
            # Mantener tamaño original si es menor que el máximo
            return image

        return image

    def _enhance_image(self, image: Image.Image) -> Image.Image:
        """
        Mejora la calidad de la imagen para el análisis
        """
        try:
            # Aplicar mejoras sutiles
            enhanced_image = image.copy()

            # 1. Ajustar contraste ligeramente
            contrast_enhancer = ImageEnhance.Contrast(enhanced_image)
            enhanced_image = contrast_enhancer.enhance(1.1)

            # 2. Ajustar brillo muy sutilmente
            brightness_enhancer = ImageEnhance.Brightness(enhanced_image)
            enhanced_image = brightness_enhancer.enhance(1.02)

            # 3. Mejorar nitidez ligeramente
            sharpness_enhancer = ImageEnhance.Sharpness(enhanced_image)
            enhanced_image = sharpness_enhancer.enhance(1.05)

            # 4. Reducir ruido con filtro suave
            enhanced_image = enhanced_image.filter(ImageFilter.SMOOTH_MORE)

            return enhanced_image

        except Exception as e:
            logger.warning(f"⚠️ Error en mejoras de imagen: {str(e)}")
            return image  # Devolver imagen original si falla el enhancement

    def _optimize_for_facial_analysis(self, image: Image.Image) -> Image.Image:
        """
        Optimizaciones específicas para análisis facial
        """
        try:
            # Asegurar que la imagen tenga suficiente resolución para análisis facial
            min_face_size = 300  # Mínimo 300px para el lado más pequeño

            if min(image.size) < min_face_size:
                # Si la imagen es muy pequeña, redimensionar manteniendo aspecto
                factor = min_face_size / min(image.size)
                new_size = (int(image.size[0] * factor),
                            int(image.size[1] * factor))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
                logger.info(
                    f"📈 Imagen redimensionada para análisis facial: {new_size}")

            # Aplicar corrección gamma sutil para mejorar detalles
            gamma = 1.1
            gamma_correction = ImageEnhance.Brightness(image)
            image = gamma_correction.enhance(gamma)

            # Asegurar que la imagen no sea demasiado oscura ni clara
            # Análisis básico del histograma
            histogram = image.histogram()

            # Verificar si la imagen es muy oscura (muchos píxeles en valores bajos)
            dark_pixels = sum(histogram[:85])  # Primeros 85 valores (de 0-255)
            total_pixels = image.size[0] * image.size[1] * 3  # RGB

            if dark_pixels / total_pixels > 0.6:  # Más del 60% son píxeles oscuros
                logger.info(
                    "🌅 Imagen muy oscura, aplicando corrección de brillo")
                brightness_enhancer = ImageEnhance.Brightness(image)
                image = brightness_enhancer.enhance(1.15)

            return image

        except Exception as e:
            logger.warning(f"⚠️ Error en optimización facial: {str(e)}")
            return image

    def get_image_info(self, image_bytes: bytes) -> dict:
        """
        Obtiene información detallada de la imagen
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))

            return {
                'format': image.format,
                'mode': image.mode,
                'size': image.size,
                'width': image.size[0],
                'height': image.size[1],
                'aspect_ratio': round(image.size[0] / image.size[1], 2),
                'megapixels': round((image.size[0] * image.size[1]) / 1000000, 2),
                'file_size_bytes': len(image_bytes),
                'file_size_mb': round(len(image_bytes) / 1024 / 1024, 2),
                'has_transparency': image.mode in ('RGBA', 'LA', 'P'),
                'is_animated': getattr(image, 'is_animated', False)
            }

        except Exception as e:
            logger.error(f"❌ Error obteniendo info de imagen: {str(e)}")
            return {}

    def detect_face_region(self, image_bytes: bytes) -> Optional[Tuple[int, int, int, int]]:
        """
        Detecta región facial aproximada (básico, sin ML)
        Retorna (x, y, width, height) o None
        """
        try:
            # Implementación básica usando características de imagen
            # En producción se podría usar OpenCV o MediaPipe
            image = Image.open(io.BytesIO(image_bytes))

            # Por ahora, asumimos que la cara está en el centro de la imagen
            # Esto es una aproximación muy básica
            width, height = image.size

            # Estimar región facial (centro de la imagen, 60% del área)
            face_width = int(width * 0.6)
            face_height = int(height * 0.7)

            x = (width - face_width) // 2
            y = (height - face_height) // 2

            return (x, y, face_width, face_height)

        except Exception as e:
            logger.warning(f"⚠️ No se pudo detectar región facial: {str(e)}")
            return None
