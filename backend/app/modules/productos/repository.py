"""Repositorios de Producto e Ingrediente."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_repository import BaseRepository
from app.modules.productos.model import Ingrediente, Producto


class ProductoRepository(BaseRepository[Producto]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Producto)


class IngredienteRepository(BaseRepository[Ingrediente]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Ingrediente)
