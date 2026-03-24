from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
from src.config import Config
from fastapi.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
import time
import logging

logger = logging.getLogger("bookly.requests")
logger.setLevel(Config.LOG_LEVEL)


def register_middlewares(app: FastAPI):
    app.add_middleware(LoggingMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=Config.ALLOWED_ORIGINS,
        allow_methods=["PUT", "GET", "POST", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=Config.ALLOWED_HOSTS,
    )

    # @app.middleware('http')
    # async def authorization(request: Request, call_next):
    #     if "Authorization" not in request.headers:
    #         return JSONResponse(
    #             content={
    #                 "message": "Not authenticated",
    #                 "resolution": "Please provide the right credentials to proceed"
    #             },
    #             status_code=status.HTTP_401_UNAUTHORIZED
    #         )
    #     response = await call_next(request)
    #     return response


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.perf_counter()
        response = await call_next(request)
        client_ip = request.client.host if request.client else "unknown"
        query_params = str(
            request.query_params) if request.query_params else ""
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            f"{client_ip} - {request.method} - {request.url.path} - {query_params} - {duration_ms:.2f}ms")
        return response
