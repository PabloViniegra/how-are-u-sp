from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import uuid
import logging
from datetime import datetime

from models import AnalysisResult, AnalysisStatus
from schemas import AnalysisResponse, AnalysisListItem
from services.ai_service import FacialAnalysisService
from services.image_service import ImageProcessingService
from middleware.api_key_auth import require_api_key
from dependencies import get_db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/analysis",
    tags=["análisis"],
    dependencies=[Depends(require_api_key)]
)

facial_analysis_service = FacialAnalysisService()
image_processing_service = ImageProcessingService()


@router.post("/", response_model=AnalysisResponse)
async def create_analysis(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Analiza el atractivo facial de una imagen subida
    """
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400, detail="El archivo debe ser una imagen")

        image_bytes = await file.read()

        # Validate that the file is actually an image before processing
        if not image_processing_service.validate_image(image_bytes):
            raise HTTPException(
                status_code=400, detail="El archivo no es una imagen válida")

        processed_image = image_processing_service.process_image(image_bytes)
        analysis_result = await facial_analysis_service.analyze_facial_attractiveness(
            processed_image
        )

        analysis_id = str(uuid.uuid4())

        db_analysis = AnalysisResult(
            id=analysis_id,
            filename=file.filename,
            analysis_status=AnalysisStatus(analysis_result["status"]),
            overall_score=analysis_result["overall_score"],
            symmetry_score=analysis_result["symmetry_score"],
            proportion_score=analysis_result["proportion_score"],
            skin_quality_score=analysis_result["skin_quality_score"],
            features_harmony_score=analysis_result["features_harmony_score"],
            eye_appeal_score=analysis_result.get("eye_appeal_score"),
            nose_harmony_score=analysis_result.get("nose_harmony_score"),
            lip_aesthetics_score=analysis_result.get("lip_aesthetics_score"),
            jawline_definition_score=analysis_result.get("jawline_definition_score"),
            cheekbone_prominence_score=analysis_result.get("cheekbone_prominence_score"),
            facial_composition_score=analysis_result.get("facial_composition_score"),
            scientific_explanation=analysis_result["scientific_explanation"],
            recommendations=analysis_result["recommendations"],
            created_at=datetime.utcnow()
        )

        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)

        # Preparar puntuaciones adicionales
        additional_scores = {}
        for score_key in ["eye_appeal_score", "nose_harmony_score", "lip_aesthetics_score",
                         "jawline_definition_score", "cheekbone_prominence_score", "facial_composition_score"]:
            if analysis_result.get(score_key) is not None:
                # Mapear a nombres más cortos para la respuesta
                response_key = score_key.replace("_score", "")
                additional_scores[response_key] = analysis_result[score_key]

        return AnalysisResponse(
            id=analysis_id,
            status=analysis_result["status"],
            overall_score=analysis_result["overall_score"],
            detailed_scores={
                "symmetry": analysis_result["symmetry_score"],
                "proportions": analysis_result["proportion_score"],
                "skin_quality": analysis_result["skin_quality_score"],
                "features_harmony": analysis_result["features_harmony_score"]
            },
            additional_scores=additional_scores if additional_scores else None,
            scientific_explanation=analysis_result["scientific_explanation"],
            recommendations=analysis_result["recommendations"],
            analysis_date=db_analysis.created_at
        )

    except HTTPException:
        # Re-raise HTTPExceptions (like validation errors) as-is
        raise
    except Exception as e:
        logger.error(f"❌ Error procesando análisis: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error procesando la imagen: {str(e)}")


@router.get("/", response_model=List[AnalysisListItem])
async def get_all_analyses(db: Session = Depends(get_db)):
    """
    Obtiene todos los análisis de la base de datos con id, overall_score y analysis_date
    """
    try:
        analyses = db.query(AnalysisResult).order_by(AnalysisResult.created_at.desc()).all()

        return [
            AnalysisListItem(
                id=analysis.id,
                overall_score=analysis.overall_score,
                analysis_date=analysis.created_at
            )
            for analysis in analyses
        ]

    except Exception as e:
        logger.error(f"❌ Error obteniendo lista de análisis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error obteniendo lista de análisis"
        )


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtiene un análisis previo por ID
    """
    analysis = db.query(AnalysisResult).filter(
        AnalysisResult.id == analysis_id).first()

    if not analysis:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")

    # Preparar puntuaciones adicionales para análisis existente
    additional_scores = {}
    score_mapping = {
        "eye_appeal_score": "eye_appeal",
        "nose_harmony_score": "nose_harmony",
        "lip_aesthetics_score": "lip_aesthetics",
        "jawline_definition_score": "jawline_definition",
        "cheekbone_prominence_score": "cheekbone_prominence",
        "facial_composition_score": "facial_composition"
    }

    for db_field, response_field in score_mapping.items():
        score_value = getattr(analysis, db_field, None)
        if score_value is not None:
            additional_scores[response_field] = score_value

    return AnalysisResponse(
        id=analysis.id,
        status=analysis.analysis_status.value if analysis.analysis_status else "feasible",
        overall_score=analysis.overall_score,
        detailed_scores={
            "symmetry": analysis.symmetry_score,
            "proportions": analysis.proportion_score,
            "skin_quality": analysis.skin_quality_score,
            "features_harmony": analysis.features_harmony_score
        },
        additional_scores=additional_scores if additional_scores else None,
        scientific_explanation=analysis.scientific_explanation,
        recommendations=analysis.recommendations,
        analysis_date=analysis.created_at
    )


@router.delete("/{analysis_id}")
async def delete_analysis(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """
    Elimina un análisis por ID
    """
    try:
        analysis = db.query(AnalysisResult).filter(
            AnalysisResult.id == analysis_id).first()

        if not analysis:
            raise HTTPException(status_code=404, detail="Análisis no encontrado")

        db.delete(analysis)
        db.commit()

        logger.info(f"Análisis eliminado: {analysis_id}")
        return {"message": "Análisis eliminado correctamente", "id": analysis_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error eliminando análisis {analysis_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error eliminando análisis"
        )