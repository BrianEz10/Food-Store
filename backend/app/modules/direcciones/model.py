"""
Modelo DireccionEntrega para direcciones de envío del cliente.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.usuarios.model import Usuario


class DireccionEntrega(SQLModel, table=True):
    """
    Dirección de entrega asociada a un usuario.
    Solo una puede ser predeterminada (es_principal=True).
    """

    __tablename__ = "direcciones_entrega"

    id: int | None = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuarios.id", nullable=False)
    alias: str | None = Field(
        default=None,
        sa_column=sa.Column(sa.String(50), nullable=True),
    )
    linea1: str = Field(
        sa_column=sa.Column(sa.Text, nullable=False),
    )
    linea2: str | None = Field(
        default=None,
        sa_column=sa.Column(sa.Text, nullable=True),
    )
    ciudad: str = Field(
        sa_column=sa.Column(sa.String(100), nullable=False),
    )
    codigo_postal: str = Field(
        sa_column=sa.Column(sa.String(10), nullable=False),
    )
    es_principal: bool = Field(
        default=False,
        sa_column=sa.Column(sa.Boolean, nullable=False, server_default=sa.text("false")),
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
    usuario: Optional["Usuario"] = Relationship(back_populates="direcciones")
