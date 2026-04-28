## Why

El proyecto Food Store no tiene código implementado — solo existe la estructura base del repositorio con `.gitkeep` y `.env.example`. Antes de que cualquier módulo funcional (auth, productos, pedidos) pueda existir, se necesita la infraestructura completa del backend: el framework FastAPI configurado, la base de datos PostgreSQL con todas las tablas del ERD v5, los datos semilla obligatorios, y los patrones de arquitectura (BaseRepository, Unit of Work, dependencias de seguridad) sobre los que se construirá todo lo demás.

Sin este change, ningún otro change del proyecto puede comenzar.

## What Changes

- **Scaffolding del backend FastAPI** con estructura feature-first (módulos por dominio)
- **Módulo `core/`** con configuración, conexión a BD, seguridad JWT, Unit of Work y BaseRepository genérico
- **16 modelos SQLModel** correspondientes al ERD v5 completo (3 dominios: Identidad y Acceso, Catálogo, Ventas/Pagos/Trazabilidad)
- **Migraciones Alembic** que crean todas las tablas desde cero
- **Script de seed idempotente** que carga: 4 roles, 6 estados de pedido, formas de pago, usuario administrador
- **Middleware de errores RFC 7807** para respuestas de error estandarizadas
- **Rate limiting global** con slowapi
- **CORS middleware** configurado para desarrollo
- **Validación y sanitización** de inputs mediante Pydantic v2
- **Dependencias de FastAPI**: `get_current_user` y `require_role` (infraestructura, sin endpoints de auth aún)

## Capabilities

### New Capabilities
- `database-models`: Todos los modelos SQLModel del ERD v5, migraciones Alembic y seed data
- `backend-patterns`: BaseRepository[T] genérico, Unit of Work con context manager, dependencias de seguridad (get_current_user, require_role)
- `error-handling`: Middleware de errores RFC 7807, clases de excepción custom, validación de inputs

### Modified Capabilities
_(ninguna — es el primer change del proyecto)_

## Impact

- **Código**: Creación de toda la estructura `backend/` con módulos `core/`, `app/modules/`, `app/db/`
- **Base de datos**: PostgreSQL con 16 tablas, restricciones de integridad, índices, campos de auditoría y soft delete
- **Dependencias**: FastAPI, SQLModel, Alembic, Passlib[bcrypt], python-jose, slowapi, mercadopago, uvicorn, pydantic[email-validator], httpx
- **APIs**: Solo `/docs` y `/redoc` (Swagger UI). Los endpoints funcionales vendrán en changes posteriores
- **Configuración**: `requirements.txt` (o pyproject.toml), `.env.example`, `alembic.ini`
