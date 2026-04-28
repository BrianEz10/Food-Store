"""
BaseRepository[T] genérico con operaciones CRUD comunes.
Filtra automáticamente registros con soft delete.
"""

from typing import Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlmodel import SQLModel

T = TypeVar("T", bound=SQLModel)


class BaseRepository(Generic[T]):
    """
    Repositorio genérico tipado con CRUD base.

    Los repositorios especializados heredan de esta clase
    y agregan métodos de dominio sin reescribir el CRUD.
    """

    def __init__(self, session: AsyncSession, model: type[T]) -> None:
        self.session = session
        self.model = model

    def _has_soft_delete(self) -> bool:
        """Verifica si el modelo soporta soft delete (tiene campo eliminado_en)."""
        return hasattr(self.model, "eliminado_en")

    def _base_query(self):
        """Query base que filtra soft-deleted automáticamente."""
        stmt = select(self.model)
        if self._has_soft_delete():
            stmt = stmt.where(self.model.eliminado_en.is_(None))  # type: ignore
        return stmt

    async def get_by_id(self, entity_id: int) -> T | None:
        """
        Obtiene una entidad por su ID.
        Excluye registros soft-deleted automáticamente.
        """
        stmt = self._base_query().where(self.model.id == entity_id)  # type: ignore
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[T]:
        """
        Lista entidades con paginación.
        Excluye registros soft-deleted automáticamente.
        """
        stmt = self._base_query().offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self) -> int:
        """Cuenta el total de entidades activas (no soft-deleted)."""
        stmt = select(func.count()).select_from(self.model)
        if self._has_soft_delete():
            stmt = stmt.where(self.model.eliminado_en.is_(None))  # type: ignore
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def create(self, entity: T) -> T:
        """
        Crea una nueva entidad.
        Ejecuta flush para obtener el ID asignado.
        """
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: T) -> T:
        """
        Actualiza una entidad existente.
        La entidad ya debe estar en la sesión.
        """
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def soft_delete(self, entity: T) -> None:
        """
        Soft delete: establece eliminado_en con el timestamp actual.
        Solo funciona en modelos que soporten soft delete.
        """
        if not self._has_soft_delete():
            msg = f"{self.model.__name__} no soporta soft delete"
            raise ValueError(msg)

        from datetime import datetime, timezone

        entity.eliminado_en = datetime.now(timezone.utc)  # type: ignore
        self.session.add(entity)
        await self.session.flush()

    async def hard_delete(self, entity: T) -> None:
        """
        Hard delete: elimina físicamente el registro.
        Usar con precaución.
        """
        await self.session.delete(entity)
        await self.session.flush()
