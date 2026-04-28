## ADDED Requirements

### Requirement: BaseRepository genérico tipado
El sistema SHALL proveer un `BaseRepository[T]` genérico que implemente operaciones CRUD comunes para cualquier entidad SQLModel, evitando duplicación de código en repositorios especializados.

#### Scenario: Operaciones CRUD disponibles
- **WHEN** se instancia un BaseRepository con un tipo de modelo
- **THEN** están disponibles los métodos: `get_by_id(id) -> T | None`, `list_all(skip, limit) -> list[T]`, `count() -> int`, `create(entity) -> T`, `update(entity) -> T`, `soft_delete(entity) -> None`, `hard_delete(entity) -> None`

#### Scenario: Filtro automático de soft delete en lecturas
- **WHEN** se ejecuta `get_by_id` o `list_all` sobre una entidad que soporta soft delete
- **THEN** los registros con `eliminado_en IS NOT NULL` se excluyen automáticamente del resultado

#### Scenario: Create retorna entidad con ID
- **WHEN** se ejecuta `create(entity)`
- **THEN** la entidad se agrega a la sesión, se ejecuta `flush()` para obtener el ID asignado, y se retorna la entidad con su ID

#### Scenario: Repositorios especializados heredan de BaseRepository
- **WHEN** se necesita un repositorio con queries de dominio
- **THEN** se crea una subclase de `BaseRepository[T]` que agrega métodos específicos sin reescribir el CRUD base

### Requirement: Unit of Work como context manager
El sistema SHALL implementar un Unit of Work que gestione transacciones de base de datos como async context manager, garantizando atomicidad en operaciones multi-tabla.

#### Scenario: Commit automático en éxito
- **WHEN** un bloque `async with UnitOfWork() as uow:` se completa sin excepciones
- **THEN** el UoW ejecuta `session.commit()` automáticamente y todos los cambios se persisten

#### Scenario: Rollback automático en error
- **WHEN** se lanza una excepción dentro del bloque `async with UnitOfWork() as uow:`
- **THEN** el UoW ejecuta `session.rollback()` automáticamente y ningún cambio se persiste

#### Scenario: Acceso a repositorios vía atributos
- **WHEN** se usa el UoW dentro de un service
- **THEN** todos los repositorios están disponibles como atributos del UoW (ej: `uow.usuarios`, `uow.productos`, `uow.pedidos`)

#### Scenario: Service nunca hace commit directo
- **WHEN** un service opera sobre la base de datos
- **THEN** el service usa exclusivamente el UoW para acceder a repositorios y NUNCA ejecuta `session.commit()` ni `session.rollback()` directamente

### Requirement: Dependencia get_current_user
El sistema SHALL proveer una dependencia de FastAPI `get_current_user` que extraiga y valide el JWT del header Authorization y retorne el usuario autenticado.

#### Scenario: Token válido
- **WHEN** un request incluye header `Authorization: Bearer <token_válido>`
- **THEN** la dependencia decodifica el JWT, valida firma y expiración, y retorna el objeto Usuario correspondiente

#### Scenario: Token ausente
- **WHEN** un request no incluye header Authorization
- **THEN** la dependencia lanza HTTP 401 Unauthorized

#### Scenario: Token expirado o inválido
- **WHEN** un request incluye un token expirado o con firma inválida
- **THEN** la dependencia lanza HTTP 401 Unauthorized con detalle del error

### Requirement: Dependencia require_role
El sistema SHALL proveer una dependencia factory `require_role(allowed_roles)` que verifique que el usuario autenticado posea al menos uno de los roles requeridos.

#### Scenario: Usuario con rol permitido
- **WHEN** se invoca `require_role(["ADMIN", "STOCK"])` y el usuario tiene rol ADMIN
- **THEN** la dependencia permite el acceso y retorna el usuario

#### Scenario: Usuario sin rol permitido
- **WHEN** se invoca `require_role(["ADMIN"])` y el usuario solo tiene rol CLIENT
- **THEN** la dependencia lanza HTTP 403 Forbidden

### Requirement: Configuración con Pydantic BaseSettings
El sistema SHALL centralizar la configuración en una clase `Settings` que carga variables de entorno desde `.env` con validación de tipos.

#### Scenario: Variables requeridas presentes
- **WHEN** el archivo `.env` contiene todas las variables requeridas (DATABASE_URL, SECRET_KEY)
- **THEN** la aplicación arranca correctamente con los valores cargados

#### Scenario: Variable requerida faltante
- **WHEN** falta una variable requerida en `.env`
- **THEN** la aplicación falla al arrancar con un mensaje de error claro indicando qué variable falta

#### Scenario: Variables con valores por defecto
- **WHEN** una variable opcional no está definida en `.env`
- **THEN** se usa el valor por defecto (ej: ALGORITHM="HS256", ACCESS_TOKEN_EXPIRE_MINUTES=30)
