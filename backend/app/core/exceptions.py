"""
Excepciones custom con mapeo a HTTP y handler RFC 7807.
Cada excepción se traduce automáticamente a una respuesta
Problem Details (application/problem+json).
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


# ── Excepciones base ─────────────────────────────────────────────────


class AppError(Exception):
    """Excepción base de la aplicación."""

    def __init__(self, detail: str, status_code: int = 500) -> None:
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class NotFoundError(AppError):
    """Recurso no encontrado (404)."""

    def __init__(self, detail: str = "Recurso no encontrado") -> None:
        super().__init__(detail=detail, status_code=404)


class ValidationError(AppError):
    """Error de validación de datos (422)."""

    def __init__(self, detail: str = "Datos inválidos") -> None:
        super().__init__(detail=detail, status_code=422)


class UnauthorizedError(AppError):
    """No autenticado o token inválido (401)."""

    def __init__(self, detail: str = "No autenticado") -> None:
        super().__init__(detail=detail, status_code=401)


class ForbiddenError(AppError):
    """Sin permisos suficientes (403)."""

    def __init__(self, detail: str = "Acceso denegado") -> None:
        super().__init__(detail=detail, status_code=403)


class ConflictError(AppError):
    """Conflicto de estado o duplicado (409)."""

    def __init__(self, detail: str = "Conflicto") -> None:
        super().__init__(detail=detail, status_code=409)


class RateLimitError(AppError):
    """Demasiadas solicitudes (429)."""

    def __init__(self, detail: str = "Demasiadas solicitudes") -> None:
        super().__init__(detail=detail, status_code=429)


# ── Mapeo de status codes a títulos RFC 7807 ─────────────────────────

HTTP_STATUS_TITLES: dict[int, str] = {
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    409: "Conflict",
    422: "Unprocessable Entity",
    429: "Too Many Requests",
    500: "Internal Server Error",
}


# ── Builders de respuesta ────────────────────────────────────────────


def _problem_response(
    status: int,
    detail: str,
    instance: str = "",
) -> JSONResponse:
    """Construye una respuesta RFC 7807 (Problem Details)."""
    return JSONResponse(
        status_code=status,
        content={
            "type": "about:blank",
            "title": HTTP_STATUS_TITLES.get(status, "Error"),
            "status": status,
            "detail": detail,
            "instance": instance,
        },
        media_type="application/problem+json",
    )


# ── Handlers ─────────────────────────────────────────────────────────


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Handler para excepciones custom de la aplicación."""
    return _problem_response(
        status=exc.status_code,
        detail=exc.detail,
        instance=str(request.url.path),
    )


async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Handler para errores de validación de Pydantic."""
    errors = [
        {
            "field": ".".join(str(loc) for loc in err["loc"]),
            "message": err["msg"],
        }
        for err in exc.errors()
    ]
    return _problem_response(
        status=422,
        detail=str(errors),
        instance=str(request.url.path),
    )


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler catch-all para errores no manejados. No expone internals."""
    logger.exception("Error interno no manejado: %s", exc)
    return _problem_response(
        status=500,
        detail="Error interno del servidor",
        instance=str(request.url.path),
    )


# ── Registro de handlers ─────────────────────────────────────────────


def register_exception_handlers(app: FastAPI) -> None:
    """Registra todos los handlers de excepciones en la app FastAPI."""
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, generic_error_handler)
