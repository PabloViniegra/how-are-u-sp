import google.generativeai as genai
from PIL import Image
import io
import json
import re
import time
import asyncio
from typing import Dict, Any
import logging
from config import settings

logger = logging.getLogger(__name__)


class FacialAnalysisService:
    """
    Servicio para realizar análisis facial usando Google AI Studio
    """

    def __init__(self):
        # Configurar la API key para Google AI
        genai.configure(api_key=settings.GOOGLE_AI_API_KEY)
        self.model = genai.GenerativeModel(settings.AI_MODEL_NAME)
        self.max_retries = 3
        self.retry_delay = 2

    async def analyze_facial_attractiveness(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Analiza el atractivo facial basado en criterios científicos
        """
        start_time = time.time()

        try:
            # Convertir bytes a imagen PIL
            image = Image.open(io.BytesIO(image_bytes))

            # Optimizar imagen para IA
            image = self._optimize_image_for_ai(image)

            # Crear prompt científico
            prompt = self._create_analysis_prompt()

            # Realizar análisis con reintentos
            for attempt in range(self.max_retries):
                try:
                    logger.info(f"🤖 Intento {attempt + 1} de análisis con IA")

                    # Generar contenido con configuración optimizada
                    response = await self._generate_content_async(prompt, image)

                    # Parsear respuesta
                    analysis_result = self._parse_ai_response(response.text)

                    # Validar resultado
                    self._validate_analysis_result(analysis_result)

                    # Agregar metadatos
                    analysis_result['processing_time'] = time.time() - \
                        start_time
                    analysis_result['ai_model'] = settings.AI_MODEL_NAME
                    analysis_result['attempt'] = attempt + 1

                    logger.info(
                        f"✅ Análisis completado en {analysis_result['processing_time']:.2f}s")
                    return analysis_result

                except Exception as e:
                    logger.warning(f"⚠️ Intento {attempt + 1} falló: {str(e)}")
                    if attempt == self.max_retries - 1:
                        raise
                    await asyncio.sleep(self.retry_delay)

        except Exception as e:
            logger.error(f"❌ Error en análisis con IA: {str(e)}")
            # Devolver resultado por defecto en caso de error
            return self._get_default_analysis_result(str(e))

    async def _generate_content_async(self, prompt: str, image: Image.Image):
        """
        Generar contenido de forma asíncrona
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.model.generate_content,
            [prompt, image]
        )

    def _optimize_image_for_ai(self, image: Image.Image) -> Image.Image:
        """
        Optimizar imagen para análisis de IA
        """
        # Redimensionar si es muy grande
        max_size = (800, 800)
        if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Asegurar modo RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')

        return image

    def _create_analysis_prompt(self) -> str:
        """
        Crear el prompt científico para el análisis facial
        """
        return """
        Eres un experto en análisis facial científico, antropometría y psicología de la percepción. Analiza esta imagen facial y proporciona un análisis exhaustivo basado en criterios científicos multidisciplinarios de atractivo facial.

        INSTRUCCIONES CRÍTICAS:
        1. Responde ÚNICAMENTE en formato JSON válido
        2. NO incluyas texto antes o después del JSON
        3. Usa números decimales para todas las puntuaciones (ejemplo: 7.5, no 7,5)
        4. Sé específico y detallado en tu análisis
        5. Mantén un tono científico pero comprensible
        6. Proporciona insights únicos y personalizados

        FORMATO REQUERIDO:
        {
            "status": "[string: 'denied', 'improvable' o 'feasible']",
            "overall_score": [número de 0-10 con decimales],
            "symmetry_score": [número de 0-10 con decimales],
            "proportion_score": [número de 0-10 con decimales],
            "skin_quality_score": [número de 0-10 con decimales],
            "features_harmony_score": [número de 0-10 con decimales],
            "eye_appeal_score": [número de 0-10 con decimales],
            "nose_harmony_score": [número de 0-10 con decimales],
            "lip_aesthetics_score": [número de 0-10 con decimales],
            "jawline_definition_score": [número de 0-10 con decimales],
            "cheekbone_prominence_score": [número de 0-10 con decimales],
            "facial_composition_score": [número de 0-10 con decimales],
            "scientific_explanation": "[explicación exhaustiva de 300-500 palabras]",
            "recommendations": "[recomendaciones específicas de 200-350 palabras]"
        }

        CRITERIOS DE EVALUACIÓN CIENTÍFICA AVANZADA:

        1. SIMETRÍA FACIAL (symmetry_score):
        - Analiza simetría bilateral usando landmarks faciales específicos
        - Evalúa desviaciones en: línea media facial, posición de ojos, altura de cejas, comisuras labiales
        - Considera micro-asimetrías y su impacto en percepción (Grammer & Thornhill, 1994)
        - Mide concordancia entre hemifacies izquierda y derecha
        - Evalúa simetría dinámica vs estática (Rhodes et al., 2001)

        2. PROPORCIONES FACIALES (proportion_score):
        - Ratio facial vertical: altura total vs ancho (ideal ~1.6-1.8)
        - Tercios faciales: frente, zona media, tercio inferior (cada uno ~33%)
        - Quintos horizontales: 5 anchos de ojos a lo largo del rostro
        - Proporción nasal: ancho nasal vs distancia intercantal
        - Ratio labial: altura del labio superior vs inferior (ideal 1:2)
        - Ángulo nasofrontal y nasolabial (Marquardt, 2005)

        3. CALIDAD DE PIEL (skin_quality_score):
        - Uniformidad cromática y textural
        - Presencia/ausencia de: manchas, cicatrices, poros dilatados, líneas finas
        - Luminosidad y translucidez (indicadores de salud - Fink et al., 2006)
        - Tono de piel y saturación cromática
        - Signos de fotoenvejecimiento y estrés oxidativo

        4. ARMONÍA Y DEFINICIÓN FACIAL (features_harmony_score):
        - Coherencia entre tamaño y forma de todos los rasgos
        - Definición de estructura ósea: pómulos, mandíbula, mentón
        - Proyección y volumen de rasgos (nariz, labios, ojos)
        - Equilibrio entre rasgos neótenicos y maduros
        - Dimorfismo sexual apropiado sin exageración
        - Expresividad y calidez facial (Jones et al., 2004)

        5. ATRACTIVO OCULAR (eye_appeal_score):
        - Forma, tamaño y posición de los ojos
        - Simetría entre ambos ojos y párpados
        - Definición de pestañas y cejas
        - Proporción del iris respecto al ojo
        - Expresividad y vivacidad de la mirada

        6. ARMONÍA NASAL (nose_harmony_score):
        - Proporción nasal respecto al rostro
        - Perfil y proyección nasal
        - Simetría de las fosas nasales
        - Ángulo nasolabial (ideal 95-105°)
        - Integración con otros rasgos faciales

        7. ESTÉTICA LABIAL (lip_aesthetics_score):
        - Proporción entre labio superior e inferior
        - Definición del arco de cupido
        - Volumen y plenitud labial
        - Simetría de las comisuras
        - Armonía con la estructura facial

        8. DEFINICIÓN MANDIBULAR (jawline_definition_score):
        - Claridad de la línea mandibular
        - Ángulo gonial (ideal 120-130°)
        - Proporción mandibular con el rostro
        - Definición del mentón
        - Masculinidad/feminidad apropiada

        9. PROMINENCIA DE PÓMULOS (cheekbone_prominence_score):
        - Altura y proyección de los pómulos
        - Definición de la estructura malar
        - Armonía con la estructura ósea
        - Creación de contornos atractivos
        - Balance con otros rasgos

        10. COMPOSICIÓN FACIAL GENERAL (facial_composition_score):
        - Balance visual general del rostro
        - Distribución armónica de rasgos
        - Atractivo compositivo total
        - Impacto visual y memorabilidad
        - Coherencia estética integral

        ANÁLISIS ADICIONAL REQUERIDO:
        - Evalúa la composición facial general y balance visual
        - Considera el impacto de la iluminación y ángulo en la percepción
        - Analiza la expresión facial y su efecto en atractivo
        - Identifica fortalezas específicas únicas del rostro
        - Detecta áreas de mejora sin ser negativo

        REQUISITOS PARA EXPLICACIÓN CIENTÍFICA (300-500 palabras):
        - Menciona 4-5 estudios científicos específicos con autores y años
        - Explica hallazgos específicos observados en esta imagen
        - Usa terminología antropométrica precisa
        - Incluye datos cuantitativos cuando sea posible
        - Conecta características físicas con teorías evolutivas
        - Menciona variaciones culturales en percepción de belleza

        REQUISITOS PARA RECOMENDACIONES (200-350 palabras):
        - Consejos específicos basados en el análisis individual
        - Técnicas de maquillaje personalizadas para resaltar fortalezas
        - Sugerencias de peinado que complementen la estructura facial
        - Rutinas de cuidado de piel específicas
        - Técnicas fotográficas para maximizar atractivo
        - Consejos de expresión y postura
        - Recomendaciones de colores que favorezcan el tono de piel
        - NO sugerir cirugía, mantener enfoque en mejora natural

        EVALUACIÓN DEL ESTADO DE LA IMAGEN (CRÍTICO):
        Antes de realizar cualquier análisis, evalúa la imagen y determina el status:

        1. "denied" - USA CUANDO:
        - La imagen NO contiene un rostro humano claro
        - Es un objeto, paisaje, animal, caricatura o dibujo
        - El rostro está completamente oculto o no es reconocible
        - La imagen está corrupta, muy borrosa o ilegible
        - Hay múltiples rostros sin uno claramente dominante

        2. "improvable" - USA CUANDO:
        - SÍ hay un rostro pero la calidad es insuficiente para análisis preciso
        - Iluminación muy pobre (demasiado oscuro/claro)
        - Rostro parcialmente oculto (más del 30%)
        - Resolución muy baja o pixelada
        - Ángulo extremo que distorsiona las proporciones
        - Sombras fuertes que ocultan rasgos importantes

        3. "feasible" - USA CUANDO:
        - Rostro humano claramente visible y reconocible
        - Calidad suficiente para análisis detallado
        - Iluminación aceptable (puede no ser perfecta)
        - La mayoría de rasgos faciales son distinguibles
        - Ángulo reasonable (frontal o 3/4)

        IMPORTANTE SOBRE PUNTUACIONES:
        - Si status es "denied": Todas las puntuaciones deben ser 0.0
        - Si status es "improvable": Puntuaciones pueden ser bajas (1-4) reflejando la limitación
        - Si status es "feasible": Puntuaciones normales basadas en análisis real (1-10)

        IMPORTANTE:
        - Sé honesto pero constructivo en el análisis
        - Cada rostro tiene características únicas valiosas
        - El atractivo es subjetivo y culturalmente variable
        - Los resultados son educativos, no definen valor personal
        - Enfócate en potenciar la belleza natural existente
        - El campo "status" es OBLIGATORIO y debe estar siempre presente
        """

    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parsea la respuesta de la IA y extrae los datos estructurados
        """
        try:
            # Limpiar el texto de respuesta
            cleaned_text = response_text.strip()

            # Buscar el JSON en la respuesta
            json_match = re.search(r'\{.*\}', cleaned_text, re.DOTALL)

            if not json_match:
                raise ValueError("No se encontró JSON en la respuesta de IA")

            json_str = json_match.group()

            # Intentar parsear JSON
            try:
                parsed_data = json.loads(json_str)
            except json.JSONDecodeError as e:
                # Intentar limpiar y reparar JSON común
                json_str = self._repair_json(json_str)
                parsed_data = json.loads(json_str)

            # Validar estructura
            required_keys = [
                'status', 'overall_score', 'symmetry_score', 'proportion_score',
                'skin_quality_score', 'features_harmony_score',
                'scientific_explanation', 'recommendations'
            ]

            for key in required_keys:
                if key not in parsed_data:
                    raise ValueError(
                        f"Clave requerida '{key}' no encontrada en la respuesta")

            # Validar y normalizar status
            valid_statuses = ['denied', 'improvable', 'feasible']
            if parsed_data['status'] not in valid_statuses:
                logger.warning(f"Status inválido: {parsed_data['status']}, usando 'feasible'")
                parsed_data['status'] = 'feasible'

            # Normalizar y validar puntuaciones
            score_keys = [
                'overall_score', 'symmetry_score', 'proportion_score',
                'skin_quality_score', 'features_harmony_score'
            ]

            for key in score_keys:
                score = parsed_data[key]
                if isinstance(score, str):
                    # Convertir strings a float
                    score = float(score.replace(',', '.'))

                # Validar rango
                if not isinstance(score, (int, float)):
                    raise ValueError(f"Puntuación {key} debe ser numérica")

                if not 0 <= score <= 10:
                    logger.warning(f"Puntuación {key} fuera de rango: {score}")
                    score = max(0, min(10, score))  # Clamp to 0-10

                parsed_data[key] = round(float(score), 1)

            # Validar textos
            if len(parsed_data['scientific_explanation'].strip()) < 50:
                raise ValueError("Explicación científica demasiado corta")

            if len(parsed_data['recommendations'].strip()) < 50:
                raise ValueError("Recomendaciones demasiado cortas")

            return parsed_data

        except Exception as e:
            logger.error(f"❌ Error parseando respuesta de IA: {str(e)}")
            raise ValueError(f"Error procesando respuesta de IA: {str(e)}")

    def _repair_json(self, json_str: str) -> str:
        """
        Intenta reparar JSON malformado común
        """
        # Reemplazar comas decimales por puntos
        json_str = re.sub(r'(\d),(\d)', r'\1.\2', json_str)

        # Escapar comillas dentro de strings
        json_str = re.sub(r'(?<=["\w])"(?=["\w])', r'\"', json_str)

        # Remover trailing commas
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)

        return json_str

    def _validate_analysis_result(self, result: Dict[str, Any]) -> None:
        """
        Valida que el resultado del análisis sea coherente
        """
        scores = [
            result['symmetry_score'],
            result['proportion_score'],
            result['skin_quality_score'],
            result['features_harmony_score']
        ]

        # Verificar que el overall_score sea coherente con los scores individuales
        average_score = sum(scores) / len(scores)
        overall_score = result['overall_score']

        # Permitir desviación de hasta 1.5 puntos
        if abs(overall_score - average_score) > 1.5:
            logger.warning(
                f"Overall score ({overall_score}) difiere mucho del promedio ({average_score:.1f})")
            # Ajustar overall_score al promedio
            result['overall_score'] = round(average_score, 1)

    def _get_default_analysis_result(self, error_message: str) -> Dict[str, Any]:
        """
        Devuelve un resultado por defecto en caso de error
        """
        return {
            "status": "improvable",
            "overall_score": 5.0,
            "symmetry_score": 5.0,
            "proportion_score": 5.0,
            "skin_quality_score": 5.0,
            "features_harmony_score": 5.0,
            "scientific_explanation": f"❌ Error técnico en el análisis: {error_message}. El sistema utiliza criterios científicos establecidos basados en investigación antropométrica y psicología de la percepción. Los parámetros incluyen análisis de simetría facial (Langlois & Roggman, 1990), proporciones faciales según la secuencia de Fibonacci y ratios áureos (Marquardt, 2005), evaluación de calidad dérmica como indicador de salud (Fink et al., 2006), y análisis de armonía entre rasgos faciales (Rhodes et al., 2001). Para un análisis exitoso, se requiere una imagen de alta calidad con iluminación uniforme y el rostro completamente visible.",
            "recommendations": "Para obtener un análisis preciso y completo, considera estos factores técnicos: 1) Iluminación: Usa luz natural suave o iluminación frontal uniforme, evita sombras duras que distorsionen la percepción facial. 2) Composición: El rostro debe ocupar 60-80% del encuadre, estar centrado y en ángulo frontal (0-15°). 3) Calidad técnica: Resolución mínima de 800x800 píxeles, formato JPEG o PNG sin compresión excesiva. 4) Expresión: Mantén una expresión neutra o ligeramente positiva para un análisis objetivo. Adicionalmente, para potenciar tu apariencia natural: mantén una rutina de cuidado facial consistente, hidrátate adecuadamente, y asegúrate de descansar lo suficiente para una piel radiante.",
            "processing_time": 0.1,
            "ai_model": settings.AI_MODEL_NAME,
            "attempt": 1,
            "error": True
        }
