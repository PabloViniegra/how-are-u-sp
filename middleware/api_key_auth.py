from fastapi import HTTPException, Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging
from config import settings

logger = logging.getLogger(__name__)

# Esquema de autenticación Bearer
security = HTTPBearer(auto_error=False)


class APIKeyAuth:
    """
    Middleware de autenticación por API Key
    """

    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """
        Valida si la API key es válida
        """
        if not api_key:
            return False

        # Verificar si la API key está en la lista de keys válidas
        valid_keys = settings.get_api_keys_list()
        return api_key in valid_keys

    @staticmethod
    def get_api_key_from_header(x_api_key: Optional[str] = Header(None)) -> str:
        """
        Obtiene la API key desde el header X-API-Key
        """
        if not x_api_key:
            logger.warning("API key no proporcionada en header X-API-Key")
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "API key required",
                    "message": "Se requiere una API key válida en el header X-API-Key",
                    "code": "MISSING_API_KEY"
                }
            )

        if not APIKeyAuth.validate_api_key(x_api_key):
            logger.warning(f"API key inválida utilizada: {x_api_key[:10]}...")
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "Invalid API key",
                    "message": "La API key proporcionada no es válida",
                    "code": "INVALID_API_KEY"
                }
            )

        logger.info(f"API key válida utilizada: {x_api_key[:10]}...")
        return x_api_key

    @staticmethod
    def get_api_key_from_bearer(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
        """
        Obtiene la API key desde el Bearer token
        """
        if not credentials:
            logger.warning("Bearer token no proporcionado")
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "API key required",
                    "message": "Se requiere una API key válida como Bearer token",
                    "code": "MISSING_BEARER_TOKEN"
                }
            )

        api_key = credentials.credentials

        if not APIKeyAuth.validate_api_key(api_key):
            logger.warning(f"Bearer token inválido: {api_key[:10]}...")
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "Invalid API key",
                    "message": "El Bearer token proporcionado no es válido",
                    "code": "INVALID_BEARER_TOKEN"
                }
            )

        logger.info(f"Bearer token válido utilizado: {api_key[:10]}...")
        return api_key


# Dependency para validar API key (acepta tanto header como Bearer)
def require_api_key(
    x_api_key: Optional[str] = Header(None),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Dependency que requiere API key válida.
    Acepta tanto X-API-Key header como Bearer token.
    """

    # Primero intentar con X-API-Key header
    if x_api_key:
        if APIKeyAuth.validate_api_key(x_api_key):
            logger.info(f"Autenticación exitosa con X-API-Key: {x_api_key[:10]}...")
            return x_api_key
        else:
            logger.warning(f"X-API-Key inválida: {x_api_key[:10]}...")
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "Invalid API key",
                    "message": "La API key en el header X-API-Key no es válida",
                    "code": "INVALID_X_API_KEY"
                }
            )

    # Si no hay X-API-Key, intentar con Bearer token
    if credentials:
        api_key = credentials.credentials
        if APIKeyAuth.validate_api_key(api_key):
            logger.info(f"Autenticación exitosa con Bearer: {api_key[:10]}...")
            return api_key
        else:
            logger.warning(f"Bearer token inválido: {api_key[:10]}...")
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "Invalid API key",
                    "message": "El Bearer token proporcionado no es válido",
                    "code": "INVALID_BEARER_TOKEN"
                }
            )

    # Si no se proporciona ningún método de autenticación
    logger.warning("No se proporcionó API key")
    raise HTTPException(
        status_code=401,
        detail={
            "error": "Authentication required",
            "message": "Se requiere autenticación. Proporciona una API key válida usando el header X-API-Key o Bearer token.",
            "code": "NO_AUTHENTICATION",
            "examples": {
                "header": "X-API-Key: your_api_key_here",
                "bearer": "Authorization: Bearer your_api_key_here"
            }
        }
    )


# Dependency simplificado solo para header X-API-Key
def require_api_key_header() -> str:
    """
    Dependency que solo acepta X-API-Key header
    """
    def _get_api_key(x_api_key: Optional[str] = Header(None)) -> str:
        return APIKeyAuth.get_api_key_from_header(x_api_key)

    return Depends(_get_api_key)


# Dependency simplificado solo para Bearer token
def require_api_key_bearer() -> str:
    """
    Dependency que solo acepta Bearer token
    """
    return Depends(APIKeyAuth.get_api_key_from_bearer)