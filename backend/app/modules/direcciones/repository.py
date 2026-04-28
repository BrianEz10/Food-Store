"""Repositorio de DireccionEntrega."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_repository import BaseRepository
from app.modules.direcciones.model import DireccionEntrega


class DireccionRepository(BaseRepository[DireccionEntrega]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, DireccionEntrega)
