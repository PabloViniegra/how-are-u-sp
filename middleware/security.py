from fastapi import Request
from fastapi.responses import JSONResponse
import re


class SecurityMiddleware:
    """Middleware de seguridad básica"""

    # Patrones de ataques comunes
    MALICIOUS_PATTERNS = {
        r'<script[^>]*>.*?</script>',  # XSS
        r'javascript:',               # JavaScript URL
        r'on\w+\s*=',                # Event handlers
        r'(union|select|insert|delete|update|drop)\s+',  # SQL injection
        r'\.\./',                     # Path traversal
        r'<iframe[^>]*>',            # iframe injection
    }

    def __init__(self):
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE)
                                  for pattern in self.MALICIOUS_PATTERNS]

    async def __call__(self, request: Request, call_next):
        # Verificar user agent
        user_agent = request.headers.get('user-agent', '').lower()
        if self._is_bot_or_malicious(user_agent):
            return JSONResponse(
                status_code=403,
                content={"detail": "Acceso prohibido"}
            )

        # Verificar parámetros de query
        for key, value in request.query_params.items():
            if self._contains_malicious_content(str(value)):
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Contenido malicioso detectado"}
                )

        response = await call_next(request)

        # Agregar headers de seguridad
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        for header, value in security_headers.items():
            response.headers[header] = value

        return response

    def _is_bot_or_malicious(self, user_agent: str) -> bool:
        """Detecta bots maliciosos (muy básico)"""
        malicious_bots = {
            'sqlmap', 'nikto', 'nmap', 'masscan', 'zap',
            'acunetix', 'netsparker', 'burp', 'w3af'
        }

        return any(bot in user_agent for bot in malicious_bots)

    def _contains_malicious_content(self, content: str) -> bool:
        """Verifica contenido malicioso"""
        return any(pattern.search(content) for pattern in self.compiled_patterns)
