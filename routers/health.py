from fastapi import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["salud"]
)


@router.get("/")
async def health_check():
    """
    Endpoint para verificar que la API está funcionando
    """
    return {"status": "ok", "message": "API funcionando correctamente"}