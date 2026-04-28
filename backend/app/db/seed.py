"""
Script de seed idempotente.
Carga datos catálogo necesarios para que la aplicación funcione:
- 4 Roles (ADMIN, STOCK, PEDIDOS, CLIENT)
- 6 Estados de Pedido (con es_terminal y orden)
- 3 Formas de Pago
- 1 Usuario admin con rol ADMIN
"""

import asyncio
import logging

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import async_session_factory, engine
from app.core.security import hash_password

# Importar TODOS los modelos para que SQLAlchemy resuelva relaciones
import app.modules.categorias.model  # noqa: F401
import app.modules.direcciones.model  # noqa: F401
import app.modules.productos.model  # noqa: F401
import app.modules.refreshtokens.model  # noqa: F401

from app.modules.pagos.model import FormaPago
from app.modules.pedidos.model import EstadoPedido
from app.modules.usuarios.model import Rol, Usuario, UsuarioRol

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


# ── Datos semilla ────────────────────────────────────────────────────

ROLES = [
    {"codigo": "ADMIN", "descripcion": "Administrador del sistema"},
    {"codigo": "STOCK", "descripcion": "Gestor de stock y catálogo"},
    {"codigo": "PEDIDOS", "descripcion": "Gestor de pedidos"},
    {"codigo": "CLIENT", "descripcion": "Cliente registrado"},
]

ESTADOS_PEDIDO = [
    {"codigo": "PENDIENTE", "descripcion": "Pedido creado, esperando pago", "orden": 1, "es_terminal": False},
    {"codigo": "CONFIRMADO", "descripcion": "Pago aprobado, listo para preparar", "orden": 2, "es_terminal": False},
    {"codigo": "EN_PREP", "descripcion": "En preparación", "orden": 3, "es_terminal": False},
    {"codigo": "EN_CAMINO", "descripcion": "En camino al cliente", "orden": 4, "es_terminal": False},
    {"codigo": "ENTREGADO", "descripcion": "Entregado al cliente", "orden": 5, "es_terminal": True},
    {"codigo": "CANCELADO", "descripcion": "Pedido cancelado", "orden": 6, "es_terminal": True},
]

FORMAS_PAGO = [
    {"codigo": "MERCADOPAGO", "nombre": "MercadoPago", "habilitado": True},
    {"codigo": "EFECTIVO", "nombre": "Efectivo al recibir", "habilitado": True},
    {"codigo": "TRANSFERENCIA", "nombre": "Transferencia bancaria", "habilitado": True},
]


# ── Funciones de seed ────────────────────────────────────────────────


async def seed_roles(session: AsyncSession) -> None:
    """Inserta roles si no existen."""
    for role_data in ROLES:
        existing = await session.execute(
            select(Rol).where(Rol.codigo == role_data["codigo"])
        )
        if existing.scalar_one_or_none() is None:
            session.add(Rol(**role_data))
            logger.info("  ✓ Rol '%s' creado", role_data["codigo"])
        else:
            logger.info("  · Rol '%s' ya existe, omitido", role_data["codigo"])


async def seed_estados_pedido(session: AsyncSession) -> None:
    """Inserta estados de pedido si no existen."""
    for estado_data in ESTADOS_PEDIDO:
        existing = await session.execute(
            select(EstadoPedido).where(EstadoPedido.codigo == estado_data["codigo"])
        )
        if existing.scalar_one_or_none() is None:
            session.add(EstadoPedido(**estado_data))
            logger.info("  ✓ Estado '%s' creado", estado_data["codigo"])
        else:
            logger.info("  · Estado '%s' ya existe, omitido", estado_data["codigo"])


async def seed_formas_pago(session: AsyncSession) -> None:
    """Inserta formas de pago si no existen."""
    for fp_data in FORMAS_PAGO:
        existing = await session.execute(
            select(FormaPago).where(FormaPago.codigo == fp_data["codigo"])
        )
        if existing.scalar_one_or_none() is None:
            session.add(FormaPago(**fp_data))
            logger.info("  ✓ FormaPago '%s' creada", fp_data["codigo"])
        else:
            logger.info("  · FormaPago '%s' ya existe, omitida", fp_data["codigo"])


async def seed_admin_user(session: AsyncSession) -> None:
    """Crea el usuario admin con rol ADMIN si no existe."""
    existing = await session.execute(
        select(Usuario).where(Usuario.email == settings.ADMIN_EMAIL)
    )
    admin = existing.scalar_one_or_none()

    if admin is None:
        admin = Usuario(
            nombre="Admin",
            apellido="FoodStore",
            email=settings.ADMIN_EMAIL,
            password_hash=hash_password(settings.ADMIN_PASSWORD),
        )
        session.add(admin)
        await session.flush()

        # Asignar rol ADMIN
        session.add(UsuarioRol(usuario_id=admin.id, rol_codigo="ADMIN"))
        logger.info("  ✓ Usuario admin '%s' creado con rol ADMIN", settings.ADMIN_EMAIL)
    else:
        logger.info("  · Usuario admin '%s' ya existe, omitido", settings.ADMIN_EMAIL)


# ── Main ─────────────────────────────────────────────────────────────


async def run_seed() -> None:
    """Ejecuta todas las funciones de seed en orden."""
    logger.info("═" * 50)
    logger.info("🌱 Iniciando seed de Food Store...")
    logger.info("═" * 50)

    async with async_session_factory() as session:
        async with session.begin():
            logger.info("\n📋 Roles:")
            await seed_roles(session)

            logger.info("\n📦 Estados de Pedido:")
            await seed_estados_pedido(session)

            logger.info("\n💳 Formas de Pago:")
            await seed_formas_pago(session)

            logger.info("\n👤 Usuario Admin:")
            await seed_admin_user(session)

    logger.info("\n" + "═" * 50)
    logger.info("✅ Seed completado exitosamente!")
    logger.info("═" * 50)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run_seed())
