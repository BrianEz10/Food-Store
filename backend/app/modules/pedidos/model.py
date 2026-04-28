"""
Modelos del dominio Ventas: EstadoPedido, Pedido, DetallePedido, HistorialEstadoPedido.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.pagos.model import Pago
    from app.modules.productos.model import Producto
    from app.modules.usuarios.model import Usuario


# ── EstadoPedido ─────────────────────────────────────────────────────


class EstadoPedido(SQLModel, table=True):
    """
    Estado del pedido con PK semántica.
    Valores: PENDIENTE, CONFIRMADO, EN_PREP, EN_CAMINO, ENTREGADO, CANCELADO.
    """

    __tablename__ = "estados_pedido"

    codigo: str = Field(
        sa_column=sa.Column(sa.String(20), primary_key=True),
    )
    descripcion: str = Field(
        sa_column=sa.Column(sa.String(100), nullable=False),
    )
    orden: int = Field(
        sa_column=sa.Column(sa.Integer, nullable=False),
    )
    es_terminal: bool = Field(
        sa_column=sa.Column(sa.Boolean, nullable=False),
    )

    # Relaciones
    pedidos: list["Pedido"] = Relationship(back_populates="estado")


# ── Pedido ───────────────────────────────────────────────────────────


class Pedido(SQLModel, table=True):
    """
    Pedido del cliente.
    Almacena snapshot de dirección en JSONB para inmutabilidad.
    """

    __tablename__ = "pedidos"

    id: int | None = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuarios.id", nullable=False)
    estado_codigo: str = Field(
        sa_column=sa.Column(
            sa.String(20),
            sa.ForeignKey("estados_pedido.codigo"),
            nullable=False,
        ),
    )
    direccion_id: int | None = Field(
        default=None,
        foreign_key="direcciones_entrega.id",
    )
    forma_pago_codigo: str | None = Field(
        default=None,
        sa_column=sa.Column(
            sa.String(20),
            sa.ForeignKey("formas_pago.codigo"),
            nullable=True,
        ),
    )
    total: float = Field(
        sa_column=sa.Column(
            sa.Numeric(10, 2),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
    costo_envio: float = Field(
        default=50.00,
        sa_column=sa.Column(
            sa.Numeric(10, 2),
            nullable=False,
            server_default=sa.text("50.00"),
        ),
    )
    direccion_snapshot: dict | None = Field(
        default=None,
        sa_column=sa.Column(JSONB, nullable=True),
    )
    notas: str | None = Field(
        default=None,
        sa_column=sa.Column(sa.Text, nullable=True),
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

    # Check constraints
    __table_args__ = (
        sa.CheckConstraint("total >= 0", name="ck_pedido_total_positivo"),
        sa.CheckConstraint("costo_envio >= 0", name="ck_pedido_envio_positivo"),
    )

    # Relaciones
    usuario: Optional["Usuario"] = Relationship(back_populates="pedidos")
    estado: Optional["EstadoPedido"] = Relationship(back_populates="pedidos")
    forma_pago: Optional["FormaPago"] = Relationship(back_populates="pedidos")
    detalles: list["DetallePedido"] = Relationship(back_populates="pedido")
    historial_estados: list["HistorialEstadoPedido"] = Relationship(
        back_populates="pedido",
    )
    pagos: list["Pago"] = Relationship(back_populates="pedido")


# ── DetallePedido ────────────────────────────────────────────────────


class DetallePedido(SQLModel, table=True):
    """
    Línea de detalle de un pedido.
    Almacena snapshot del precio y nombre del producto.
    personalizacion es un INTEGER[] con IDs de ingredientes excluidos.
    """

    __tablename__ = "detalles_pedido"

    id: int | None = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedidos.id", nullable=False)
    producto_id: int = Field(foreign_key="productos.id", nullable=False)
    nombre_snapshot: str = Field(
        sa_column=sa.Column(sa.String(200), nullable=False),
    )
    precio_snapshot: float = Field(
        sa_column=sa.Column(sa.Numeric(10, 2), nullable=False),
    )
    cantidad: int = Field(
        sa_column=sa.Column(sa.Integer, nullable=False),
    )
    subtotal: float = Field(
        sa_column=sa.Column(sa.Numeric(10, 2), nullable=False),
    )
    personalizacion: list[int] | None = Field(
        default=None,
        sa_column=sa.Column(ARRAY(sa.Integer), nullable=True),
    )

    # Solo creado_en (inmutable)
    creado_en: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=sa.Column(
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # Check constraints
    __table_args__ = (
        sa.CheckConstraint("cantidad >= 1", name="ck_detalle_cantidad_minima"),
    )

    # Relaciones
    pedido: Optional["Pedido"] = Relationship(back_populates="detalles")
    producto: Optional["Producto"] = Relationship(back_populates="detalles_pedido")


# ── HistorialEstadoPedido ────────────────────────────────────────────


class HistorialEstadoPedido(SQLModel, table=True):
    """
    Registro append-only del historial de estados de un pedido.
    NUNCA tiene actualizado_en — solo creado_en.
    NUNCA se hace UPDATE ni DELETE sobre esta tabla.
    """

    __tablename__ = "historial_estados_pedido"

    id: int | None = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedidos.id", nullable=False)
    estado_desde: str | None = Field(
        default=None,
        sa_column=sa.Column(
            sa.String(20),
            sa.ForeignKey("estados_pedido.codigo"),
            nullable=True,
        ),
    )
    estado_hasta: str = Field(
        sa_column=sa.Column(
            sa.String(20),
            sa.ForeignKey("estados_pedido.codigo"),
            nullable=False,
        ),
    )
    usuario_id: int | None = Field(
        default=None,
        foreign_key="usuarios.id",
    )
    motivo: str | None = Field(
        default=None,
        sa_column=sa.Column(sa.Text, nullable=True),
    )

    # SOLO creado_en — append-only
    creado_en: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=sa.Column(
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # Relaciones
    pedido: Optional["Pedido"] = Relationship(back_populates="historial_estados")
    usuario: Optional["Usuario"] = Relationship(back_populates="historial_acciones")
