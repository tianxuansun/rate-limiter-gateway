from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.metrics import HTTP_REQUEST_LATENCY_SECONDS, HTTP_REQUESTS_TOTAL, monotonic_s


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        start = monotonic_s()
        response = await call_next(request)
        elapsed = monotonic_s() - start

        # Prefer route template path (low cardinality), fallback to raw path
        route = request.scope.get("route")
        if route and getattr(route, "path", None):
            path_label = route.path
        else:
            path_label = request.url.path

        method = request.method
        status = str(response.status_code)

        HTTP_REQUESTS_TOTAL.labels(method=method, path=path_label, status=status).inc()
        HTTP_REQUEST_LATENCY_SECONDS.labels(method=method, path=path_label).observe(elapsed)

        return response
