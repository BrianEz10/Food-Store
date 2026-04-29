---
id: 4
type: architecture
project: brian-palacios
scope: project
topic_key: opsx/change-map
session_id: manual-save-brian-palacios
created_at: "2026-04-28 18:12:51"
updated_at: "2026-04-28 18:12:51"
revision_count: 1
tags:
  - brian-palacios
  - architecture
aliases:
  - "Food Store — Mapa completo de 13 changes"
---

# Food Store — Mapa completo de 13 changes

**What**: Diseñé el mapa completo de 13 changes para desarrollar Food Store de principio a fin, cubriendo 77 historias de usuario en 19 épicas.

**Why**: El usuario pidió analizar docs/ y proponer el orden de implementación con dependencias explícitas.

**Where**: Artifact en artifacts/mapa_de_changes.md

**Learned**:
- El proyecto está VACÍO (solo .gitkeep y .env.example en backend/ y frontend/)
- 13 changes en orden: setup-backend-core → setup-frontend-core (paralelo) → auth-y-autorizacion → categorias-e-ingredientes / navegacion-layout-base / perfil-y-direcciones (paralelos) → productos-y-catalogo → carrito-de-compras → creacion-de-pedidos → pagos-mercadopago → fsm-pedidos-y-visualizacion → admin-usuarios-y-catalogo / dashboard-metricas (paralelos)
- Ruta crítica: 01→03→04→07→08→09→10→11→12/13
- Stack: React+TS+Vite+Tailwind+Zustand+TanStack Query // FastAPI+SQLModel+PostgreSQL+Alembic
- ERD v5 tiene 16 tablas en 3 dominios
- Evaluación: 200 puntos con rúbrica detallada, bonus +10 tests, +10 deploy, -30% si no corre

---
*Session*: [[session-manual-save-brian-palacios]]
*Topic*: [[topic-opsx]]
