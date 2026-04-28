"""
Modelo RefreshToken para gestión de sesiones con rotación de tokens.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.usuarios.model import Usuario


class RefreshToken(SQLModel, table=True):
    """
    Token de refresco almacenado como hash SHA-256.
    Nunca se almacena el token en texto plano.
    """

    __tablename__ = "refresh_tokens"

    id: int | None = Field(default=None, primary_key=True)
    token_hash: str = Field(
        sa_column=sa.Column(sa.String(64), unique=True, nullable=False, index=True),
    )
    usuario_id: int = Field(foreign_key="usuarios.id", nullable=False)
    expires_at: datetime = Field(
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False),
    )
    revoked_at: datetime | None = Field(
        default=None,
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=True),
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
    usuario: Optional["Usuario"] = Relationship(back_populates="refresh_tokens")
