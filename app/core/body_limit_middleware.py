from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class BodyLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, max_body_bytes: int, path_prefix: str = "/api"):
        super().__init__(app)
        self.max_body_bytes = max_body_bytes
        self.path_prefix = path_prefix

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if self.max_body_bytes <= 0:
            return await call_next(request)

        if not request.url.path.startswith(self.path_prefix):
            return await call_next(request)

        # Fast-path: Content-Length header
        cl = request.headers.get("content-length")
        if cl is not None:
            try:
                if int(cl) > self.max_body_bytes:
                    return JSONResponse({"detail": "Payload too large"}, status_code=413)
            except ValueError:
                pass

        # Safe-path: measure actual body
        body = await request.body()
        if len(body) > self.max_body_bytes:
            return JSONResponse({"detail": "Payload too large"}, status_code=413)

        return await call_next(request)
