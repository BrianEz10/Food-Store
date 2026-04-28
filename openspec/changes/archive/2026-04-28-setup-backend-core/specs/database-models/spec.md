## ADDED Requirements

### Requirement: Modelos SQLModel del ERD v5
El sistema SHALL definir 16 modelos SQLModel correspondientes al ERD v5 organizados en 3 dominios: Identidad y Acceso, Catálogo de Productos, y Ventas/Pagos/Trazabilidad. Cada modelo MUST mapear directamente a una tabla de PostgreSQL con los tipos de datos, restricciones y relaciones definidos en la especificación.

#### Scenario: Dominio 1 — Identidad y Acceso
- **WHEN** se definen los modelos de identidad
- **THEN** existen las entidades: `Usuario` (id BIGSERIAL PK, nombre, apellido, email VARCHAR(254) UNIQUE NOT NULL, password_hash CHAR(60) NOT NULL, telefono nullable, eliminado_en nullable, creado_en, actualizado_en), `Rol` (codigo VARCHAR(20) PK semántica: ADMIN|STOCK|PEDIDOS|CLIENT, descripcion), `UsuarioRol` (usuario_id + rol_codigo PK compuesta, asignado_por_id), `RefreshToken` (id, token_hash CHAR(64) UNIQUE NOT NULL, usuario_id FK, expires_at TIMESTAMPTZ NOT NULL, revoked_at TIMESTAMPTZ nullable, creado_en), `DireccionEntrega` (id, usuario_id FK, alias nullable, linea1 TEXT NOT NULL, linea2, ciudad, codigo_postal, es_principal BOOLEAN default false, eliminado_en, creado_en, actualizado_en)

#### Scenario: Dominio 2 — Catálogo de Productos
- **WHEN** se definen los modelos de catálogo
- **THEN** existen las entidades: `Categoria` (id, nombre, descripcion, imagen_url, padre_id FK self-ref nullable, eliminado_en, creado_en, actualizado_en), `Producto` (id, nombre, descripcion, imagen_url, precio_base DECIMAL(10,2) CHECK>=0, stock_cantidad INTEGER CHECK>=0 default 0, disponible BOOLEAN default true, eliminado_en, creado_en, actualizado_en), `Ingrediente` (id, nombre VARCHAR(100) UNIQUE NOT NULL, es_alergeno BOOLEAN default false, eliminado_en, creado_en, actualizado_en), `ProductoCategoria` (producto_id + categoria_id PK compuesta, es_principal BOOLEAN), `ProductoIngrediente` (producto_id + ingrediente_id PK compuesta, es_removible BOOLEAN NOT NULL), `FormaPago` (codigo VARCHAR(20) PK semántica, nombre, habilitado BOOLEAN default true)

#### Scenario: Dominio 3 — Ventas, Pagos y Trazabilidad
- **WHEN** se definen los modelos de ventas
- **THEN** existen las entidades: `EstadoPedido` (codigo VARCHAR(20) PK semántica, descripcion, orden INTEGER, es_terminal BOOLEAN NOT NULL), `Pedido` (id, usuario_id FK, estado_codigo FK→EstadoPedido, direccion_id FK nullable, forma_pago_codigo FK→FormaPago, total DECIMAL(10,2) CHECK>=0, costo_envio DECIMAL(10,2) default 50.00, direccion_snapshot JSONB nullable, notas nullable, eliminado_en, creado_en, actualizado_en), `DetallePedido` (id, pedido_id FK, producto_id FK, nombre_snapshot VARCHAR(200) NOT NULL, precio_snapshot DECIMAL(10,2) NOT NULL, cantidad INTEGER CHECK>=1, subtotal DECIMAL(10,2), personalizacion INTEGER[] nullable, creado_en), `HistorialEstadoPedido` (id, pedido_id FK, estado_desde VARCHAR(20) FK nullable, estado_hasta VARCHAR(20) FK NOT NULL, usuario_id FK nullable, motivo TEXT nullable, creado_en TIMESTAMPTZ NOT NULL — SOLO creado_en, NUNCA actualizado_en), `Pago` (id, pedido_id FK, monto DECIMAL(10,2), mp_payment_id BIGINT UNIQUE nullable, mp_status VARCHAR(30) NOT NULL, external_reference VARCHAR(100) UNIQUE NOT NULL, idempotency_key VARCHAR(100) UNIQUE NOT NULL, creado_en, actualizado_en)

### Requirement: Campos de auditoría en todas las tablas principales
Todas las tablas principales del sistema SHALL incluir campos de auditoría `creado_en` y `actualizado_en` de tipo TIMESTAMPTZ, excepto `HistorialEstadoPedido` que solo tiene `creado_en` (append-only).

#### Scenario: Creación de registro con auditoría
- **WHEN** se crea un nuevo registro en cualquier tabla principal
- **THEN** `creado_en` se establece automáticamente con el timestamp actual (default NOW)

#### Scenario: Actualización de registro con auditoría
- **WHEN** se modifica un registro existente
- **THEN** `actualizado_en` se actualiza automáticamente al timestamp actual

### Requirement: Soft delete en entidades de negocio
Las entidades que manejan datos de negocio SHALL implementar soft delete mediante un campo `eliminado_en` de tipo TIMESTAMPTZ nullable. Un registro con `eliminado_en IS NOT NULL` se considera eliminado lógicamente.

#### Scenario: Entidades con soft delete
- **WHEN** se consulta qué entidades soportan soft delete
- **THEN** las entidades son: Usuario, Categoria, Producto, Ingrediente, DireccionEntrega, Pedido

#### Scenario: Soft delete no borra físicamente
- **WHEN** se ejecuta un soft delete sobre un registro
- **THEN** se establece `eliminado_en` con el timestamp actual y el registro permanece en la base de datos

### Requirement: Migraciones Alembic completas
El sistema SHALL incluir migraciones Alembic que crean todas las 16 tablas del ERD v5 desde una base de datos vacía.

#### Scenario: Migración inicial exitosa
- **WHEN** se ejecuta `alembic upgrade head` contra una base de datos PostgreSQL vacía
- **THEN** se crean todas las tablas sin errores, con tipos, constraints, FKs e índices correctos

#### Scenario: Migración reversible
- **WHEN** se ejecuta `alembic downgrade -1` después de la migración inicial
- **THEN** las tablas se eliminan sin errores

### Requirement: Seed data obligatorio
El sistema SHALL incluir un script de seed que carga los datos catálogo necesarios para que la aplicación funcione.

#### Scenario: Ejecución del seed
- **WHEN** se ejecuta `python -m app.db.seed` después de las migraciones
- **THEN** se insertan: 4 roles (ADMIN, STOCK, PEDIDOS, CLIENT), 6 estados de pedido (PENDIENTE, CONFIRMADO, EN_PREP, EN_CAMINO, ENTREGADO, CANCELADO con es_terminal correspondiente), formas de pago (MERCADOPAGO, EFECTIVO, TRANSFERENCIA habilitadas), 1 usuario admin con rol ADMIN

#### Scenario: Seed idempotente
- **WHEN** se ejecuta el script de seed múltiples veces
- **THEN** no se duplican datos (usa INSERT ... ON CONFLICT DO NOTHING o equivalente)
