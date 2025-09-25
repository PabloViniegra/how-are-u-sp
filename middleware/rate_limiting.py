from fastapi import Request
from fastapi.responses import JSONResponse
import time
from collections import defaultdict, deque
from typing import Dict, Deque


class RateLimiter:
    """Rate limiter simple basado en memoria"""

    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, Deque[float]] = defaultdict(deque)

    async def __call__(self, request: Request, call_next):
        # Obtener IP del cliente
        client_ip = request.client.host
        current_time = time.time()

        # Limpiar requests antiguos
        request_times = self.requests[client_ip]
        while request_times and request_times[0] < current_time - self.window_seconds:
            request_times.popleft()

        # Verificar límite
        if len(request_times) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Demasiadas requests. Intenta de nuevo en unos minutos.",
                    "retry_after": self.window_seconds
                }
            )

        # Agregar request actual
        request_times.append(current_time)

        # Continuar con la request
        response = await call_next(request)
        return response
