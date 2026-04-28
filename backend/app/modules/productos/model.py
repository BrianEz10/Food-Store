"""
Modelos del dominio Catálogo: Producto, Ingrediente, ProductoCategoria, ProductoIngrediente.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.categorias.model import Categoria
    from app.modules.pedidos.model import DetallePedido


# ── ProductoCategoria (tabla pivote) ─────────────────────────────────


class ProductoCategoria(SQLModel, table=True):
    """
    Relación M:N entre Producto y Categoría.
    PK compuesta (producto_id, categoria_id).
    """

    __tablename__ = "productos_categorias"

    producto_id: int = Field(
        foreign_key="productos.id",
        primary_key=True,
    )
    categoria_id: int = Field(
        foreign_key="categorias.id",
        primary_key=True,
    )
    es_principal: bool = Field(
        default=False,
        sa_column=sa.Column(sa.Boolean, nullable=False, server_default=sa.text("false")),
    )

    # Relaciones
    producto: Optional["Producto"] = Relationship(back_populates="producto_categorias")
    categoria: Optional["Categoria"] = Relationship(
        back_populates="producto_categorias",
    )


# ── ProductoIngrediente (tabla pivote) ───────────────────────────────


class ProductoIngrediente(SQLModel, table=True):
    """
    Relación M:N entre Producto e Ingrediente.
    PK compuesta (producto_id, ingrediente_id).
    """

    __tablename__ = "productos_ingredientes"

    producto_id: int = Field(
        foreign_key="productos.id",
        primary_key=True,
    )
    ingrediente_id: int = Field(
        foreign_key="ingredientes.id",
        primary_key=True,
    )
    es_removible: bool = Field(
        sa_column=sa.Column(sa.Boolean, nullable=False),
    )

    # Relaciones
    producto: Optional["Producto"] = Relationship(
        back_populates="producto_ingredientes",
    )
    ingrediente: Optional["Ingrediente"] = Relationship(
        back_populates="producto_ingredientes",
    )


# ── Ingrediente ──────────────────────────────────────────────────────


class Ingrediente(SQLModel, table=True):
    """
    Ingrediente de un producto.
    es_alergeno=True indica que es un alérgeno y debe mostrarse prominentemente.
    """

    __tablename__ = "ingredientes"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(
        sa_column=sa.Column(sa.String(100), unique=True, nullable=False),
    )
    es_alergeno: bool = Field(
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
    producto_ingredientes: list["ProductoIngrediente"] = Relationship(
        back_populates="ingrediente",
    )


# ── Producto ─────────────────────────────────────────────────────────


class Producto(SQLModel, table=True):
    """
    Producto del catálogo.
    Precio en DECIMAL(10,2), stock con CHECK >= 0.
    """

    __tablename__ = "productos"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(
        sa_column=sa.Column(sa.String(200), nullable=False),
    )
    descripcion: str | None = Field(
        default=None,
        sa_column=sa.Column(sa.Text, nullable=True),
    )
    imagen_url: str | None = Field(
        default=None,
        sa_column=sa.Column(sa.String(500), nullable=True),
    )
    precio_base: float = Field(
        sa_column=sa.Column(
            sa.Numeric(10, 2),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
    stock_cantidad: int = Field(
        default=0,
        sa_column=sa.Column(
            sa.Integer,
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
    disponible: bool = Field(
        default=True,
        sa_column=sa.Column(sa.Boolean, nullable=False, server_default=sa.text("true")),
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
        sa.CheckConstraint("precio_base >= 0", name="ck_producto_precio_positivo"),
        sa.CheckConstraint("stock_cantidad >= 0", name="ck_producto_stock_positivo"),
    )

    # Relaciones
    producto_categorias: list["ProductoCategoria"] = Relationship(
        back_populates="producto",
    )
    producto_ingredientes: list["ProductoIngrediente"] = Relationship(
        back_populates="producto",
    )
    detalles_pedido: list["DetallePedido"] = Relationship(back_populates="producto")
