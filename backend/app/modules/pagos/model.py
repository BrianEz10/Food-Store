"""
Modelos del dominio Pagos: FormaPago, Pago.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.pedidos.model import Pedido


# ── FormaPago ────────────────────────────────────────────────────────


class FormaPago(SQLModel, table=True):
    """
    Forma de pago con PK semántica.
    Valores: MERCADOPAGO, EFECTIVO, TRANSFERENCIA.
    """

    __tablename__ = "formas_pago"

    codigo: str = Field(
        sa_column=sa.Column(sa.String(20), primary_key=True),
    )
    nombre: str = Field(
        sa_column=sa.Column(sa.String(100), nullable=False),
    )
    habilitado: bool = Field(
        default=True,
        sa_column=sa.Column(sa.Boolean, nullable=False, server_default=sa.text("true")),
    )

    # Relaciones
    pedidos: list["Pedido"] = Relationship(back_populates="forma_pago")


# ── Pago ─────────────────────────────────────────────────────────────


class Pago(SQLModel, table=True):
    """
    Registro de pago asociado a un pedido.
    Relación 1:N (un pedido puede tener múltiples intentos de pago).
    idempotency_key garantiza que no se dupliquen pagos.
    """

    __tablename__ = "pagos"

    id: int | None = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedidos.id", nullable=False)
    monto: float = Field(
        sa_column=sa.Column(sa.Numeric(10, 2), nullable=False),
    )
    mp_payment_id: int | None = Field(
        default=None,
        sa_column=sa.Column(sa.BigInteger, unique=True, nullable=True),
    )
    mp_status: str = Field(
        sa_column=sa.Column(sa.String(30), nullable=False),
    )
    external_reference: str = Field(
        sa_column=sa.Column(sa.String(100), unique=True, nullable=False),
    )
    idempotency_key: str = Field(
        sa_column=sa.Column(sa.String(100), unique=True, nullable=False),
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
    pedido: Optional["Pedido"] = Relationship(back_populates="pagos")
