# Protocolo de Colaboración y Skills — Food Store

Este documento define las reglas de comportamiento, el contexto del stack tecnológico, los patrones de arquitectura y las capacidades (skills) que los agentes de IA deben utilizar para desarrollar el proyecto **Food Store** — un e-commerce de alimentos.

---

## 1. Reglas Críticas de Comportamiento

> [!IMPORTANT]
> **Spec-Driven Development (OPSX):** Este proyecto utiliza el workflow OPSX. Antes de implementar código, se debe tener un change con sus artefactos (proposal, design, tasks) aprobados. Consultá `openspec status` antes de escribir código.

> [!IMPORTANT]
> **Memoria Persistente (Engram):** Al completar cualquier tarea significativa (decisión de arquitectura, bug fix, descubrimiento, patrón establecido), el agente DEBE guardar la información en Engram con `mem_save`. Al iniciar sesión, DEBE consultar `mem_context` y `mem_search` para recuperar contexto previo.

### Reglas Generales

- **Trazabilidad:** Toda sugerencia debe alinearse con las Historias de Usuario (US-000 a US-076) y las Reglas de Negocio (RN-XX) documentadas en `docs/Historias_de_usuario.txt`.
- **Seguridad:** Priorizar siempre la validación JWT con `get_current_user` y `require_role`, y el hashing de contraseñas con bcrypt en todo diseño de autenticación.
- **Atomicidad:** Las operaciones multi-tabla (especialmente creación de pedidos) DEBEN usar el patrón Unit of Work para garantizar transacciones atómicas.
- **Inmutabilidad:** Los pedidos SIEMPRE usan snapshots de precios y direcciones. Nunca referenciar datos mutables directamente.
- **Errores RFC 7807:** Todos los errores de la API siguen el estándar Problem Details (`type`, `title`, `status`, `detail`, `instance`).
- **Soft Delete:** Nunca borrar registros físicamente (excepto refresh tokens expirados). Usar el campo `eliminado_en`.
- **PCI Compliance:** Los datos de tarjetas NUNCA pasan por el servidor de Food Store. La tokenización ocurre en el browser vía SDK de MercadoPago.

---

## 2. Stack Tecnológico

### Backend

| Tecnología | Uso |
|---|---|
| **Python 3.12+** | Lenguaje principal |
| **FastAPI** | Framework web (ASGI, async, OpenAPI automático) |
| **SQLModel** | ORM (combina SQLAlchemy + Pydantic) |
| **PostgreSQL** | Base de datos relacional |
| **Alembic** | Migraciones de base de datos |
| **Passlib + bcrypt** | Hashing de contraseñas (pin: `bcrypt==4.0.1`) |
| **python-jose** | Generación/verificación de JWT (HS256) |
| **slowapi** | Rate limiting en endpoints sensibles |
| **Pydantic v2 + BaseSettings** | Validación de datos y configuración |
| **MercadoPago SDK** | Integración de pagos |
| **uvicorn** | Servidor ASGI |

### Frontend

| Tecnología | Uso |
|---|---|
| **React 18+** | Librería UI |
| **TypeScript** | Tipado estricto (`strict: true`) |
| **Vite** | Bundler y dev server |
| **Tailwind CSS** | Framework de estilos (utilidades) |
| **Zustand** | Estado del cliente (4 stores: auth, cart, payment, ui) |
| **TanStack Query** | Estado del servidor (cache, fetching, sync) |
| **TanStack Form** | Gestión de formularios |
| **Axios** | Cliente HTTP con interceptores JWT |
| **React Router** | Navegación SPA |
| **recharts** | Gráficos del dashboard |
| **MercadoPago.js** | Tokenización PCI SAQ-A en browser |

### Herramientas

| Herramienta | Uso |
|---|---|
| **OPSX (openspec CLI)** | Spec-Driven Development workflow |
| **Engram** | Memoria persistente para agentes de IA |
| **Git** | Control de versiones con conventional commits |

---

## 3. Arquitectura

### Backend — Capas (flujo unidireccional)

```
Request HTTP → Router → Service → Unit of Work → Repository → Model → PostgreSQL
```

- **Router:** Recibe HTTP, valida con Pydantic, delega al Service. Sin lógica de negocio.
- **Service:** Lógica de negocio. Coordina repositories vía UoW.
- **Unit of Work (UoW):** Context manager async. Commit en éxito, rollback en error. Expone repos como atributos.
- **Repository:** Acceso a datos. `BaseRepository[T]` genérico + repos especializados.
- **Model:** Clases SQLModel que mapean a tablas PostgreSQL.

### Backend — Estructura (feature-first)

```
backend/
├── app/
│   ├── core/          # config, database, security, uow, exceptions
│   ├── modules/
│   │   ├── auth/      # login, register, refresh, logout
│   │   ├── usuarios/  # CRUD, roles
│   │   ├── direcciones/
│   │   ├── categorias/
│   │   ├── productos/
│   │   ├── pedidos/   # creación, FSM, historial
│   │   ├── pagos/     # MercadoPago, webhooks
│   │   └── admin/     # métricas, configuración
│   └── db/
│       ├── seed.py
│       └── base.py
├── alembic/
├── main.py
└── requirements.txt
```

### Frontend — Feature-Sliced Design (FSD)

```
frontend/src/
├── app/        # Providers, routing, estilos globales
├── pages/      # Páginas (1 por ruta)
├── widgets/    # Bloques de UI compuestos
├── features/   # Interacciones: "agregar al carrito", "filtrar", "pagar"
├── entities/   # Modelos de dominio + API base
└── shared/     # UI genérica, Axios, stores, tipos, utils
```

### Base de Datos — ERD v5 (16 tablas, 3 dominios)

| Dominio | Tablas |
|---|---|
| **Identidad y Acceso** | usuarios, roles, usuarios_roles, refresh_tokens, direcciones_entrega |
| **Catálogo** | categorias, productos, ingredientes, productos_categorias, productos_ingredientes, formas_pago |
| **Ventas/Pagos/Trazabilidad** | estados_pedido, pedidos, detalles_pedido, historial_estados_pedido, pagos |

---

## 4. Patrones Clave

| Patrón | Dónde se aplica | Descripción |
|---|---|---|
| **Unit of Work** | Creación de pedidos, transacciones multi-tabla | Commit/rollback atómico via context manager |
| **Repository** | Toda entidad | `BaseRepository[T]` con CRUD + soft delete automático |
| **Snapshot** | `precio_snapshot`, `direccion_snapshot` en pedidos | Copia inmutable de datos al momento de crear el pedido |
| **Soft Delete** | Usuarios, categorías, productos, ingredientes, direcciones, pedidos | Campo `eliminado_en` en lugar de DELETE físico |
| **Audit Trail** | `historial_estados_pedido` | Append-only: solo INSERT, nunca UPDATE ni DELETE |
| **FSM** | Estado del pedido (6 estados) | Transiciones estrictas validadas en capa de servicio |
| **Idempotencia** | Webhooks de MercadoPago | `idempotency_key` previene procesamiento duplicado |
| **FSD** | Frontend | Capas horizontales con dependencia unidireccional |

### Máquina de Estados del Pedido (FSM)

```
PENDIENTE ──(pago aprobado)──→ CONFIRMADO ──→ EN_PREPARACIÓN ──→ EN_CAMINO ──→ ENTREGADO
    │                              │                │
    └──────── CANCELADO ←──────────┘────────────────┘
```

- `PENDIENTE → CONFIRMADO`: Automática (webhook pago aprobado) + decremento stock
- `CONFIRMADO → EN_PREPARACIÓN → EN_CAMINO → ENTREGADO`: Manual (Gestor de Pedidos)
- Cancelación restaura stock si el pedido ya fue confirmado
- `ENTREGADO` y `CANCELADO` son terminales

---

## 5. Skills Disponibles

Las skills están instaladas en `.agents/skills/` y proveen guías especializadas:

| Skill | Descripción |
|---|---|
| [fastapi-expert](skills/fastapi-expert/SKILL.md) | Patrones avanzados de FastAPI: endpoints async, Pydantic v2, dependency injection, JWT, WebSocket |
| [fastapi-templates](skills/fastapi-templates/SKILL.md) | Scaffolding de proyectos FastAPI con patrones de producción |
| [find-skills](skills/find-skills/SKILL.md) | Descubrimiento e instalación de nuevas skills |
| [jwt-security](skills/jwt-security/SKILL.md) | Implementación segura de JWT: creación, validación, almacenamiento, rotación de tokens |
| [mercadopago-integration](skills/mercadopago-integration/SKILL.md) | Arquitectura de checkout con interfaces agnósticas y mock adapters (modo seguro, sin ejecución real) |
| [playwright-cli](skills/playwright-cli/SKILL.md) | Tests end-to-end con Playwright: automatización de browser, testing de flujos |
| [supabase-postgres-best-practices](skills/supabase-postgres-best-practices/SKILL.md) | Optimización de PostgreSQL: queries, schemas, índices, configuración |
| [ui-ux-pro-max](skills/ui-ux-pro-max/SKILL.md) | Diseño UI/UX premium: 50+ estilos, paletas de color, font pairings, componentes por stack |
| [vercel-react-best-practices](skills/vercel-react-best-practices/SKILL.md) | Performance en React/Next.js: rendering, re-renders, bundles, async, server components |

---

## 6. Mapa de Changes (Prioridades de Implementación)

El proyecto se divide en **13 changes incrementales** que cubren 77 historias de usuario:

| # | Change | Estado | Complejidad | Depende de |
|---|---|---|---|---|
| 01 | `setup-backend-core` | ✅ Completado y archivado | 🔴 Alta | — |
| 02 | `setup-frontend-core` | 🔲 Pendiente (**PRÓXIMO**) | 🟡 Media | — |
| 03 | `auth-y-autorizacion` | 🔲 Pendiente | 🔴 Alta | 01, 02 |
| 04 | `categorias-e-ingredientes` | 🔲 Pendiente | 🟡 Media | 03 |
| 05 | `navegacion-layout-base` | 🔲 Pendiente | 🟡 Media | 02, 03 |
| 06 | `perfil-y-direcciones` | 🔲 Pendiente | 🟡 Media | 03 |
| 07 | `productos-y-catalogo` | 🔲 Pendiente | 🔴 Alta | 04, 05 |
| 08 | `carrito-de-compras` | 🔲 Pendiente | 🟢 Baja | 06, 07 |
| 09 | `creacion-de-pedidos` | 🔲 Pendiente | 🔴 Alta | 06, 08 |
| 10 | `pagos-mercadopago` | 🔲 Pendiente | 🔴 Alta | 09 |
| 11 | `fsm-pedidos-y-visualizacion` | 🔲 Pendiente | 🔴 Alta | 09, 10 |
| 12 | `admin-usuarios-y-catalogo` | 🔲 Pendiente | 🟡 Media | 11 |
| 13 | `dashboard-metricas` | 🔲 Pendiente | 🟡 Media | 11 |

### Ruta Crítica

```
01 → 03 → 04 → 07 → 08 → 09 → 10 → 11 → 12/13
```

### Paralelizables

- **01 y 02** — Backend y frontend setup son independientes
- **04, 05 y 06** — Se pueden hacer en paralelo tras completar 03
- **12 y 13** — Ambos dependen de 11 pero no entre sí

---

## 7. Gotchas y Descubrimientos Previos

Estos son problemas encontrados durante el desarrollo que el agente debe recordar:

| Problema | Solución |
|---|---|
| `passlib 1.7.4` incompatible con `bcrypt >= 4.1` | Pin `bcrypt==4.0.1` en requirements.txt |
| `CREATE DATABASE` falla dentro de transacciones psql | Usar `createdb` standalone en lugar de `psql -c` |
| SQLAlchemy necesita TODOS los modelos importados | Importar todos los modelos antes de resolver `Relationship()` cross-module |
| `UsuarioRol` con 2 FKs a `usuarios` | Requiere `foreign_keys` explícito en la Relationship del lado inverso |
| `HistorialEstadoPedido` FK ambiguo a `usuarios` | También necesita `foreign_keys` explícito |
| `npx skills` falla si SKILL.md no está en raíz del repo | Clonar manualmente y copiar la subcarpeta + actualizar `skills-lock.json` |

---

## 8. Instrucciones de Arranque para el Agente

Cuando el usuario inicie una nueva sesión de trabajo:

1. **Recuperar contexto:** Ejecutar `mem_context` y `mem_search(query: "food-store")` en Engram para recuperar decisiones previas.
2. **Verificar estado OPSX:** Ejecutar `openspec list --json` para ver qué changes existen y su estado.
3. **Leer este archivo:** Usar este AGENTS.md como referencia del stack, patrones y prioridades.
4. **Consultar documentación:** Los docs del proyecto están en `docs/`:
   - `Descripcion.txt` — Descripción integral del sistema (650 líneas)
   - `Historias_de_usuario.txt` — 77 HU con criterios de aceptación y reglas de negocio
   - `mapa_de_changes.md` — Grafo de dependencias y detalle de cada change
5. **Identificar el siguiente change:** Consultar la tabla de la sección 6 para determinar qué sigue.
6. **Cargar skills relevantes:** Antes de implementar, leer los SKILL.md de las skills que apliquen a la tarea.

---

## 9. Configuración del Entorno

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Configurar variables
alembic upgrade head
python -m app.db.seed
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env  # Configurar VITE_API_BASE_URL
npm run dev  # Puerto 5173
```

### Base de Datos

- **Motor:** PostgreSQL
- **Usuario:** `foodstore_user`
- **Base:** `foodstore`
- **Connection string:** `postgresql+asyncpg://foodstore_user:<password>@localhost:5432/foodstore`

---

## 10. Evaluación

El proyecto se evalúa sobre **200 puntos** con bonificaciones:

- **+10 puntos** por tests unitarios/integración
- **+10 puntos** por deploy en producción
- **-30%** si el sistema no compila o no corre

Los criterios de entrega (CE-01 a CE-14) están detallados en `docs/Descripcion.txt`, sección 15.
