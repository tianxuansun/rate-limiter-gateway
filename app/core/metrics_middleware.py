from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from typing import Callable

from app.metrics import HTTP_REQUESTS_TOTAL, HTTP_REQUEST_LATENCY_SECONDS, monotonic_s


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        start = monotonic_s()
        response = await call_next(request)
        elapsed = monotonic_s() - start

        # Use raw path (avoid high-cardinality labels)
        path = request.url.path
        method = request.method
        status = str(response.status_code)

        HTTP_REQUESTS_TOTAL.labels(method=method, path=path, status=status).inc()
        HTTP_REQUEST_LATENCY_SECONDS.labels(method=method, path=path).observe(elapsed)

        return response
