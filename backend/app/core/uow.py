"""
Unit of Work — async context manager que gestiona transacciones.

El UoW es el ÚNICO lugar que hace commit/rollback.
Los services nunca tocan la sesión directamente.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.modules.categorias.repository import CategoriaRepository
from app.modules.direcciones.repository import DireccionRepository
from app.modules.pagos.repository import PagoRepository
from app.modules.pedidos.repository import PedidoRepository
from app.modules.productos.repository import IngredienteRepository, ProductoRepository
from app.modules.refreshtokens.repository import RefreshTokenRepository
from app.modules.usuarios.repository import UsuarioRepository


class UnitOfWork:
    """
    Async context manager para transacciones atómicas.

    Uso:
        async with UnitOfWork() as uow:
            user = await uow.usuarios.get_by_id(1)
            user.nombre = "Nuevo"
            await uow.usuarios.update(user)
            # commit automático al salir del bloque
    """

    session: AsyncSession

    # Repositorios
    usuarios: UsuarioRepository
    refresh_tokens: RefreshTokenRepository
    direcciones: DireccionRepository
    categorias: CategoriaRepository
    productos: ProductoRepository
    ingredientes: IngredienteRepository
    pedidos: PedidoRepository
    pagos: PagoRepository

    async def __aenter__(self) -> "UnitOfWork":
        self.session = async_session_factory()

        # Inicializar todos los repositorios con la misma sesión
        self.usuarios = UsuarioRepository(self.session)
        self.refresh_tokens = RefreshTokenRepository(self.session)
        self.direcciones = DireccionRepository(self.session)
        self.categorias = CategoriaRepository(self.session)
        self.productos = ProductoRepository(self.session)
        self.ingredientes = IngredienteRepository(self.session)
        self.pedidos = PedidoRepository(self.session)
        self.pagos = PagoRepository(self.session)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            await self.session.rollback()
        else:
            await self.session.commit()
        await self.session.close()

    async def rollback(self) -> None:
        """Rollback explícito (para uso manual cuando se necesita)."""
        await self.session.rollback()
