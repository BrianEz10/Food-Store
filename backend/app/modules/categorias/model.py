"""
Modelo Categoria con jerarquía auto-referenciada (padre_id).
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.productos.model import ProductoCategoria


class Categoria(SQLModel, table=True):
    """
    Categoría de productos con soporte de jerarquía.
    padre_id nullable permite categorías raíz y subcategorías.
    Se usa CTE recursivo para obtener el árbol completo.
    """

    __tablename__ = "categorias"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(
        sa_column=sa.Column(sa.String(100), nullable=False),
    )
    descripcion: str | None = Field(
        default=None,
        sa_column=sa.Column(sa.Text, nullable=True),
    )
    imagen_url: str | None = Field(
        default=None,
        sa_column=sa.Column(sa.String(500), nullable=True),
    )
    padre_id: int | None = Field(
        default=None,
        foreign_key="categorias.id",
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
    padre: Optional["Categoria"] = Relationship(
        back_populates="hijos",
        sa_relationship_kwargs={"remote_side": "Categoria.id"},
    )
    hijos: list["Categoria"] = Relationship(back_populates="padre")
    producto_categorias: list["ProductoCategoria"] = Relationship(
        back_populates="categoria",
    )
