"""
Modelos del dominio Identidad y Acceso: Rol, Usuario, UsuarioRol.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.direcciones.model import DireccionEntrega
    from app.modules.pedidos.model import HistorialEstadoPedido, Pedido
    from app.modules.refreshtokens.model import RefreshToken


# ── Rol ──────────────────────────────────────────────────────────────


class Rol(SQLModel, table=True):
    """
    Rol del sistema con PK semántica.
    Valores: ADMIN, STOCK, PEDIDOS, CLIENT.
    """

    __tablename__ = "roles"

    codigo: str = Field(
        sa_column=sa.Column(sa.String(20), primary_key=True),
    )
    descripcion: str = Field(
        sa_column=sa.Column(sa.String(100), nullable=False),
    )

    # Relaciones
    usuario_roles: list["UsuarioRol"] = Relationship(back_populates="rol")


# ── Usuario ──────────────────────────────────────────────────────────


class Usuario(SQLModel, table=True):
    """
    Usuario del sistema.
    Soporta soft delete via eliminado_en.
    """

    __tablename__ = "usuarios"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(sa_column=sa.Column(sa.String(100), nullable=False))
    apellido: str = Field(sa_column=sa.Column(sa.String(100), nullable=False))
    email: str = Field(
        sa_column=sa.Column(sa.String(254), unique=True, nullable=False, index=True),
    )
    password_hash: str = Field(
        sa_column=sa.Column(sa.String(60), nullable=False),
    )
    telefono: str | None = Field(
        default=None,
        sa_column=sa.Column(sa.String(20), nullable=True),
    )

    # Soft delete
    eliminado_en: datetime | None = Field(
        default=None,
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=True),
    )

    # Auditoría
    creado_en: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=sa.Column(
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    actualizado_en: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=sa.Column(
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
            onupdate=sa.text("now()"),
        ),
    )

    # Relaciones
    usuario_roles: list["UsuarioRol"] = Relationship(
        back_populates="usuario",
        sa_relationship_kwargs={"foreign_keys": "UsuarioRol.usuario_id"},
    )
    refresh_tokens: list["RefreshToken"] = Relationship(back_populates="usuario")
    direcciones: list["DireccionEntrega"] = Relationship(back_populates="usuario")
    pedidos: list["Pedido"] = Relationship(back_populates="usuario")
    historial_acciones: list["HistorialEstadoPedido"] = Relationship(
        back_populates="usuario",
        sa_relationship_kwargs={"foreign_keys": "HistorialEstadoPedido.usuario_id"},
    )


# ── UsuarioRol ───────────────────────────────────────────────────────


class UsuarioRol(SQLModel, table=True):
    """
    Tabla pivote usuario-rol (M:N).
    PK compuesta (usuario_id, rol_codigo).
    """

    __tablename__ = "usuarios_roles"

    usuario_id: int = Field(
        foreign_key="usuarios.id",
        primary_key=True,
    )
    rol_codigo: str = Field(
        sa_column=sa.Column(
            sa.String(20),
            sa.ForeignKey("roles.codigo"),
            primary_key=True,
        ),
    )
    asignado_por_id: int | None = Field(
        default=None,
        foreign_key="usuarios.id",
    )
    creado_en: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=sa.Column(
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # Relaciones
    usuario: Optional["Usuario"] = Relationship(
        back_populates="usuario_roles",
        sa_relationship_kwargs={"foreign_keys": "[UsuarioRol.usuario_id]"},
    )
    rol: Optional["Rol"] = Relationship(back_populates="usuario_roles")
