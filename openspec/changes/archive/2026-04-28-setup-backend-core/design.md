## Context

Food Store es un e-commerce de alimentos con stack React + TypeScript + FastAPI + PostgreSQL. El repositorio existe pero está vacío — solo tiene `.gitkeep` y `.env.example` en `backend/` y `frontend/`. Este change establece toda la infraestructura del backend sobre la cual se construirán los 12 changes restantes.

El backend debe seguir una **arquitectura en capas con flujo unidireccional**: Router → Service → Unit of Work → Repository → Model. La organización es **feature-first** (módulos por dominio, no por tipo técnico). El modelo de datos sigue el ERD v5 con 16 tablas en 3 dominios, aplicando soft delete, campos de auditoría y snapshot pattern.

**Restricciones clave del proyecto:**
- Python con FastAPI (no Django, Flask ni otro framework)
- SQLModel como ORM (combina SQLAlchemy + Pydantic)
- PostgreSQL como base de datos (requerido por INTEGER[], CTE recursivos)
- Alembic para migraciones versionadas
- Pydantic v2 para schemas de validación
- Los IDs de seed data son estables y se referencian en el código

## Goals / Non-Goals

**Goals:**
- Estructura de carpetas feature-first del backend completa
- `main.py` funcional con FastAPI, CORS, rate limiting y middleware de errores
- Los 16 modelos SQLModel del ERD v5 definidos con tipos correctos, restricciones y relaciones
- Migraciones Alembic que crean todas las tablas sin errores (`alembic upgrade head`)
- Script de seed idempotente con roles, estados de pedido, formas de pago y usuario admin
- `BaseRepository[T]` genérico con operaciones CRUD + soft delete
- `UnitOfWork` como async context manager con commit/rollback automático
- Dependencias `get_current_user` y `require_role` listas para usar
- Middleware de errores RFC 7807
- Servidor arrancable con `uvicorn` y Swagger accesible en `/docs`

**Non-Goals:**
- Endpoints funcionales de ningún módulo (auth, productos, pedidos, etc.) — eso viene en changes posteriores
- Frontend — eso es Change 02
- Tests automatizados — se agregarán como bonus
- Deploy a producción — configuración local únicamente
- Routers con lógica — solo se crean los archivos vacíos como placeholder

## Decisions

### D1: Estructura de carpetas feature-first

```
backend/
├── alembic/                    # Migraciones
│   ├── versions/
│   └── env.py
├── alembic.ini
├── requirements.txt
├── .env.example
└── app/
    ├── main.py                 # FastAPI app, CORS, rate limiting, routers
    ├── core/
    │   ├── __init__.py
    │   ├── config.py           # Settings con Pydantic BaseSettings
    │   ├── database.py         # Engine, SessionLocal, get_session
    │   ├── security.py         # JWT encode/decode, bcrypt hash/verify
    │   ├── uow.py              # UnitOfWork context manager
    │   ├── base_repository.py  # BaseRepository[T] genérico
    │   ├── exceptions.py       # Excepciones custom + handler RFC 7807
    │   └── dependencies.py     # get_current_user, require_role
    ├── db/
    │   ├── __init__.py
    │   └── seed.py             # Script de seed idempotente
    └── modules/
        ├── auth/
        │   ├── __init__.py
        │   ├── model.py        # (vacío, importa de usuarios/refreshtokens)
        │   ├── schemas.py
        │   ├── repository.py
        │   ├── service.py
        │   └── router.py
        ├── refreshtokens/
        │   ├── __init__.py
        │   ├── model.py        # RefreshToken
        │   └── repository.py
        ├── usuarios/
        │   ├── __init__.py
        │   ├── model.py        # Usuario, Rol, UsuarioRol
        │   ├── schemas.py
        │   ├── repository.py
        │   ├── service.py
        │   └── router.py
        ├── direcciones/
        │   ├── __init__.py
        │   ├── model.py        # DireccionEntrega
        │   ├── schemas.py
        │   ├── repository.py
        │   ├── service.py
        │   └── router.py
        ├── categorias/
        │   ├── __init__.py
        │   ├── model.py        # Categoria
        │   ├── schemas.py
        │   ├── repository.py
        │   ├── service.py
        │   └── router.py
        ├── productos/
        │   ├── __init__.py
        │   ├── model.py        # Producto, Ingrediente, ProductoCategoria, ProductoIngrediente
        │   ├── schemas.py
        │   ├── repository.py
        │   ├── service.py
        │   └── router.py
        ├── pedidos/
        │   ├── __init__.py
        │   ├── model.py        # EstadoPedido, Pedido, DetallePedido, HistorialEstadoPedido
        │   ├── schemas.py
        │   ├── repository.py
        │   ├── service.py
        │   └── router.py
        ├── pagos/
        │   ├── __init__.py
        │   ├── model.py        # Pago, FormaPago
        │   ├── schemas.py
        │   ├── repository.py
        │   ├── service.py
        │   └── router.py
        └── admin/
            ├── __init__.py
            ├── schemas.py
            ├── service.py
            └── router.py
```

**Rationale:** Feature-first agrupa todo lo relacionado a un dominio en una carpeta. Esto hace que sea claro dónde buscar y agregar código. La alternativa (layer-first: carpetas `models/`, `services/`, `routers/`) escala peor y genera archivos con nombres ambiguos.

### D2: Modelos SQLModel — Decisiones de tipado

| Decisión | Elección | Alternativa descartada | Razón |
|---|---|---|---|
| PKs semánticas vs numéricas | `Rol.codigo VARCHAR(20)` como PK, `EstadoPedido.codigo VARCHAR(20)` como PK | BIGSERIAL con lookup | Evita JOINs innecesarios; el código en Python referencia directamente `"ADMIN"`, `"PENDIENTE"`, etc. |
| Precios | `DECIMAL(10,2)` con `CHECK >= 0` | FLOAT | Precisión fija obligatoria para dinero — float genera errores de redondeo |
| Personalización | `INTEGER[]` (array PostgreSQL) | Tabla pivote | Dato inmutable que se lee como un todo; simplifica queries y modelo |
| Soft delete | Campo `eliminado_en TIMESTAMPTZ` nullable | Flag booleano | El timestamp da información extra (cuándo se eliminó) sin costo adicional |
| Auditoría | `creado_en` (default NOW) + `actualizado_en` (auto-update) | Sin auditoría | Requerido por la rúbrica y buena práctica |
| RefreshToken | Almacena `token_hash` (SHA-256), no el token en texto plano | Token plano en BD | Si la BD se compromete, los tokens hasheados no son usables |

### D3: BaseRepository[T] — Diseño genérico

```python
class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: type[T]):
        self.session = session
        self.model = model

    async def get_by_id(self, entity_id: int) -> T | None
    async def list_all(self, skip: int = 0, limit: int = 100) -> list[T]
    async def count(self) -> int
    async def create(self, entity: T) -> T
    async def update(self, entity: T) -> T
    async def soft_delete(self, entity: T) -> None
    async def hard_delete(self, entity: T) -> None
```

**Rationale:** Un repositorio genérico tipado evita duplicar CRUD para cada entidad. Los repositorios especializados heredan y agregan métodos de dominio. `get_by_id` y `list_all` filtran `eliminado_en IS NULL` automáticamente para entidades con soft delete.

### D4: Unit of Work — async context manager

```python
class UnitOfWork:
    async def __aenter__(self) -> "UnitOfWork":
        self.session = async_session_factory()
        self.usuarios = UsuarioRepository(self.session)
        self.productos = ProductoRepository(self.session)
        self.pedidos = PedidoRepository(self.session)
        # ... todos los repos
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.session.rollback()
        else:
            await self.session.commit()
        await self.session.close()
```

**Rationale:** El UoW es el único lugar que hace commit/rollback. Los services nunca tocan la sesión directamente. Esto garantiza atomicidad — si un service lanza una excepción en cualquier punto, todo se revierte automáticamente.

### D5: Dependencias de seguridad — sin endpoints aún

`get_current_user` y `require_role` se implementan como dependencias de FastAPI (`Depends()`), pero no se conectan a endpoints en este change. Quedan listas para que Change 03 (auth) las use directamente.

```python
async def get_current_user(token: str = Depends(oauth2_scheme)) -> Usuario:
    # Decodifica JWT, valida firma y expiración, retorna Usuario
    ...

def require_role(allowed_roles: list[str]):
    async def role_checker(user: Usuario = Depends(get_current_user)):
        # Verifica que el usuario tenga al menos uno de los roles
        ...
    return role_checker
```

### D6: Configuración con Pydantic BaseSettings

```python
class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    MP_ACCESS_TOKEN: str = ""
    MP_PUBLIC_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env")
```

**Rationale:** Pydantic BaseSettings carga automáticamente variables de `.env` con validación de tipos. Si falta una variable requerida, la app falla al arrancar con un mensaje claro.

### D7: Middleware de errores RFC 7807

Todas las excepciones se capturan por un handler global que retorna:

```json
{
  "type": "about:blank",
  "title": "Not Found",
  "status": 404,
  "detail": "Producto con id 99 no encontrado",
  "instance": "/api/v1/productos/99"
}
```

Se definen excepciones custom: `NotFoundError`, `ValidationError`, `UnauthorizedError`, `ForbiddenError`, `ConflictError`. Cada una mapea a un status code HTTP específico.

## Risks / Trade-offs

| Riesgo | Mitigación |
|---|---|
| Modelos SQLModel cambian en changes posteriores | Los modelos se definen completos desde el ERD v5. Cambios menores se manejan con migraciones Alembic incrementales |
| AsyncSession agrega complejidad | FastAPI es async-first. Usar sync sessions sería nadar contra la corriente. SQLModel soporta async via SQLAlchemy |
| Seed data con IDs hardcodeados | Es requerimiento del proyecto. Los IDs de roles y estados son estables por diseño. El script es idempotente (`ON CONFLICT DO NOTHING`) |
| BaseRepository genérico puede no cubrir queries complejas | Los repos especializados agregan métodos propios. El genérico solo cubre CRUD básico |
| 16 modelos en una sola migración | Para el primer change es aceptable. En producción se harían migraciones incrementales, pero este es un proyecto desde cero |
