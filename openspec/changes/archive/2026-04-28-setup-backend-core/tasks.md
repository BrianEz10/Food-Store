## 1. Scaffolding y dependencias

- [x] 1.1 Crear estructura de carpetas feature-first del backend (`app/core/`, `app/db/`, `app/modules/{auth,refreshtokens,usuarios,direcciones,categorias,productos,pedidos,pagos,admin}/` con archivos `__init__.py`)
- [x] 1.2 Crear `requirements.txt` con todas las dependencias: FastAPI, SQLModel, Alembic, Passlib[bcrypt], python-jose[cryptography], slowapi, mercadopago, uvicorn, httpx, pydantic[email-validator], asyncpg, python-dotenv
- [x] 1.3 Crear `.env.example` con todas las variables documentadas (DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, CORS_ORIGINS, MP_ACCESS_TOKEN, MP_PUBLIC_KEY, MP_NOTIFICATION_URL)

## 2. Configuración core

- [x] 2.1 Crear `app/core/config.py` con clase `Settings(BaseSettings)` que carga variables de entorno desde `.env` con valores por defecto
- [x] 2.2 Crear `app/core/database.py` con engine async de SQLAlchemy, session factory (`async_sessionmaker`), y función `get_session`
- [x] 2.3 Crear `app/core/security.py` con funciones: `hash_password(password) -> str`, `verify_password(plain, hashed) -> bool`, `create_access_token(data, expires_delta) -> str`, `decode_access_token(token) -> dict`

## 3. Modelos SQLModel — Dominio 1: Identidad y Acceso

- [x] 3.1 Crear modelo `Rol` en `app/modules/usuarios/model.py` — PK semántica `codigo VARCHAR(20)`, campo `descripcion`
- [x] 3.2 Crear modelo `Usuario` en `app/modules/usuarios/model.py` — id BIGSERIAL, nombre, apellido, email UNIQUE, password_hash, telefono nullable, campos de auditoría y soft delete
- [x] 3.3 Crear modelo `UsuarioRol` en `app/modules/usuarios/model.py` — PK compuesta (usuario_id, rol_codigo), campo asignado_por_id FK nullable
- [x] 3.4 Crear modelo `RefreshToken` en `app/modules/refreshtokens/model.py` — token_hash CHAR(64) UNIQUE, usuario_id FK, expires_at, revoked_at nullable
- [x] 3.5 Crear modelo `DireccionEntrega` en `app/modules/direcciones/model.py` — usuario_id FK, alias, linea1, linea2, ciudad, codigo_postal, es_principal BOOLEAN, soft delete y auditoría

## 4. Modelos SQLModel — Dominio 2: Catálogo de Productos

- [x] 4.1 Crear modelo `Categoria` en `app/modules/categorias/model.py` — nombre, descripcion, imagen_url, padre_id FK self-ref nullable, soft delete y auditoría
- [x] 4.2 Crear modelo `Producto` en `app/modules/productos/model.py` — nombre, descripcion, imagen_url, precio_base DECIMAL(10,2) CHECK>=0, stock_cantidad INTEGER CHECK>=0 default 0, disponible BOOLEAN default true, soft delete y auditoría
- [x] 4.3 Crear modelo `Ingrediente` en `app/modules/productos/model.py` — nombre VARCHAR(100) UNIQUE, es_alergeno BOOLEAN default false, soft delete y auditoría
- [x] 4.4 Crear modelos `ProductoCategoria` y `ProductoIngrediente` en `app/modules/productos/model.py` — tablas pivote con PKs compuestas, es_principal y es_removible respectivamente
- [x] 4.5 Crear modelo `FormaPago` en `app/modules/pagos/model.py` — PK semántica `codigo VARCHAR(20)`, nombre, habilitado BOOLEAN default true

## 5. Modelos SQLModel — Dominio 3: Ventas, Pagos y Trazabilidad

- [x] 5.1 Crear modelo `EstadoPedido` en `app/modules/pedidos/model.py` — PK semántica `codigo VARCHAR(20)`, descripcion, orden INTEGER, es_terminal BOOLEAN
- [x] 5.2 Crear modelo `Pedido` en `app/modules/pedidos/model.py` — usuario_id FK, estado_codigo FK, direccion_id FK nullable, forma_pago_codigo FK, total DECIMAL(10,2), costo_envio DECIMAL(10,2) default 50.00, direccion_snapshot JSONB, notas, soft delete y auditoría
- [x] 5.3 Crear modelo `DetallePedido` en `app/modules/pedidos/model.py` — pedido_id FK, producto_id FK, nombre_snapshot, precio_snapshot DECIMAL(10,2), cantidad INTEGER CHECK>=1, subtotal, personalizacion INTEGER[], solo creado_en
- [x] 5.4 Crear modelo `HistorialEstadoPedido` en `app/modules/pedidos/model.py` — pedido_id FK, estado_desde FK nullable, estado_hasta FK, usuario_id FK nullable, motivo TEXT, solo creado_en (append-only, NUNCA actualizado_en)
- [x] 5.5 Crear modelo `Pago` en `app/modules/pagos/model.py` — pedido_id FK, monto DECIMAL(10,2), mp_payment_id BIGINT UNIQUE nullable, mp_status VARCHAR(30), external_reference UNIQUE, idempotency_key UNIQUE, auditoría

## 6. Migraciones Alembic

- [x] 6.1 Inicializar Alembic (`alembic init alembic`), configurar `alembic.ini` con DATABASE_URL y `env.py` con importación de todos los modelos SQLModel
- [x] 6.2 Generar migración inicial con `alembic revision --autogenerate -m "initial_schema"` que cree las 16 tablas
- [x] 6.3 Verificar que `alembic upgrade head` ejecuta sin errores y que `alembic downgrade -1` revierte correctamente

## 7. Seed data

- [x] 7.1 Crear `app/db/seed.py` con script idempotente que inserte: 4 roles, 6 estados de pedido (con es_terminal y orden correctos), 3 formas de pago, 1 usuario admin con password hasheada y rol ADMIN asignado. Usar INSERT ... ON CONFLICT DO NOTHING

## 8. Patrones base — BaseRepository y Unit of Work

- [x] 8.1 Crear `app/core/base_repository.py` con `BaseRepository[T]` genérico: get_by_id, list_all (con filtro automático de soft delete), count, create (con flush), update, soft_delete, hard_delete
- [x] 8.2 Crear repositorios vacíos (solo heredan de BaseRepository) para cada módulo: `UsuarioRepository`, `ProductoRepository`, `PedidoRepository`, `CategoriaRepository`, `IngredienteRepository`, `DireccionRepository`, `PagoRepository`, `RefreshTokenRepository`
- [x] 8.3 Crear `app/core/uow.py` con `UnitOfWork` como async context manager: __aenter__ crea sesión e inicializa todos los repos, __aexit__ hace commit en éxito o rollback en error, cierra sesión

## 9. Dependencias de seguridad

- [x] 9.1 Crear `app/core/dependencies.py` con `get_current_user` (extrae JWT del header Authorization, decodifica, valida, retorna Usuario o lanza 401) y `require_role(allowed_roles)` (factory que retorna dependency checker, lanza 403 si no tiene rol)

## 10. Middleware de errores y main.py

- [x] 10.1 Crear `app/core/exceptions.py` con clases: `NotFoundError(404)`, `ValidationError(422)`, `UnauthorizedError(401)`, `ForbiddenError(403)`, `ConflictError(409)`, `RateLimitError(429)` y handler global que formatea errores como RFC 7807
- [x] 10.2 Crear `app/main.py` con: instancia FastAPI, CORS middleware (orígenes desde config), rate limiting con slowapi, registro del exception handler RFC 7807, prefijo `/api/v1` para futuros routers, y endpoints `/docs` y `/redoc` accesibles

## 11. Verificación final

- [x] 11.1 Verificar que `pip install -r requirements.txt` instala sin errores
- [x] 11.2 Verificar que `alembic upgrade head` crea todas las tablas
- [x] 11.3 Verificar que `python -m app.db.seed` carga los datos iniciales sin duplicar
- [x] 11.4 Verificar que `uvicorn app.main:app --reload` arranca sin errores y Swagger UI es accesible en `/docs`
