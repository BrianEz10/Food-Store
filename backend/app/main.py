"""
Food Store API — Punto de entrada de la aplicación FastAPI.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers

settings = get_settings()


# ── Rate Limiter ─────────────────────────────────────────────────────

limiter = Limiter(key_func=get_remote_address)


# ── Lifespan ─────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup y shutdown hooks."""
    # Startup: importar modelos para que SQLModel los registre
    import app.modules.categorias.model  # noqa: F401
    import app.modules.direcciones.model  # noqa: F401
    import app.modules.pagos.model  # noqa: F401
    import app.modules.pedidos.model  # noqa: F401
    import app.modules.productos.model  # noqa: F401
    import app.modules.refreshtokens.model  # noqa: F401
    import app.modules.usuarios.model  # noqa: F401

    yield
    # Shutdown


# ── App ──────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API del sistema de e-commerce Food Store",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers RFC 7807
register_exception_handlers(app)


# ── Health check ─────────────────────────────────────────────────────


@app.get("/api/v1/health", tags=["health"])
async def health_check():
    """Endpoint de verificación de salud."""
    return {"status": "ok", "version": settings.APP_VERSION}
