"""
Dependencias de FastAPI para autenticación y autorización.
get_current_user: extrae y valida JWT del header Authorization.
require_role: factory que verifica roles del usuario autenticado.
"""

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.core.database import get_session
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_access_token
from app.modules.usuarios.model import Usuario, UsuarioRol

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> Usuario:
    """
    Extrae el JWT del header Authorization, valida firma y expiración,
    y retorna el usuario autenticado con sus roles cargados.

    Raises:
        UnauthorizedError: Si el token es inválido, expirado o el usuario no existe.
    """
    try:
        payload = decode_access_token(token)
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise UnauthorizedError("Token inválido: sin identificador de usuario")
    except JWTError as e:
        raise UnauthorizedError(f"Token inválido: {e}") from e

    # Cargar usuario con roles en un solo query
    stmt = (
        select(Usuario)
        .options(selectinload(Usuario.usuario_roles).selectinload(UsuarioRol.rol))
        .where(Usuario.id == int(user_id))
        .where(Usuario.eliminado_en.is_(None))
    )
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise UnauthorizedError("Usuario no encontrado o desactivado")

    return user


def require_role(allowed_roles: list[str]):
    """
    Factory de dependencia que verifica que el usuario tenga
    al menos uno de los roles especificados.

    Uso:
        @router.get("/admin", dependencies=[Depends(require_role(["ADMIN"]))])
        async def admin_endpoint(): ...

    Args:
        allowed_roles: Lista de códigos de rol permitidos (ej: ["ADMIN", "STOCK"]).

    Returns:
        Dependency checker que retorna el usuario si tiene el rol.

    Raises:
        ForbiddenError: Si el usuario no tiene ninguno de los roles permitidos.
    """

    async def role_checker(
        current_user: Usuario = Depends(get_current_user),
    ) -> Usuario:
        user_roles = {ur.rol_codigo for ur in current_user.usuario_roles}
        if not user_roles.intersection(allowed_roles):
            raise ForbiddenError(
                f"Se requiere uno de los roles: {', '.join(allowed_roles)}"
            )
        return current_user

    return role_checker
