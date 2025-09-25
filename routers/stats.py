from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import logging

from models import AnalysisResult
from middleware.api_key_auth import require_api_key
from dependencies import get_db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/stats",
    tags=["estadísticas"],
    dependencies=[Depends(require_api_key)]
)


@router.get("/")
async def get_statistics(db: Session = Depends(get_db)):
    """
    Obtiene estadísticas generales de análisis
    """
    try:
        total_analyses = db.query(AnalysisResult).count()

        if total_analyses == 0:
            return {
                "total_analyses": 0,
                "average_score": 0,
                "score_distribution": {}
            }

        analyses = db.query(AnalysisResult).all()
        average_score = sum(a.overall_score for a in analyses) / len(analyses)

        score_ranges = {
            "0-2": 0, "2-4": 0, "4-6": 0,
            "6-8": 0, "8-10": 0
        }

        for analysis in analyses:
            score = analysis.overall_score
            if score < 2:
                score_ranges["0-2"] += 1
            elif score < 4:
                score_ranges["2-4"] += 1
            elif score < 6:
                score_ranges["4-6"] += 1
            elif score < 8:
                score_ranges["6-8"] += 1
            else:
                score_ranges["8-10"] += 1

        return {
            "total_analyses": total_analyses,
            "average_score": round(average_score, 2),
            "score_distribution": score_ranges
        }

    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error obteniendo estadísticas"
        )