---
id: 6
type: architecture
project: brian-palacios
scope: project
topic_key: opsx/setup-backend-core/apply
session_id: manual-save-brian-palacios
created_at: "2026-04-28 21:26:33"
updated_at: "2026-04-28 21:26:33"
revision_count: 1
tags:
  - brian-palacios
  - architecture
aliases:
  - "OPSX: apply completed for setup-backend-core"
---

# OPSX: apply completed for setup-backend-core

**What**: Completé apply de setup-backend-core — 35/35 tareas implementadas y verificadas
**Why**: Primer change del mapa para establecer toda la infraestructura backend
**Where**: backend/ — 16 modelos, BaseRepository, UoW, exceptions RFC 7807, main.py, alembic, seed
**Learned**: 
- passlib 1.7.4 es incompatible con bcrypt>=4.1 — pin bcrypt==4.0.1
- psql -c con múltiples sentencias las ejecuta en transacción, CREATE DATABASE falla en transacción — usar createdb separado
- SQLAlchemy necesita TODOS los modelos importados para resolver Relationship() cross-module — agregar imports explícitos
- UsuarioRol con 2 FKs a usuarios requiere foreign_keys explícito en la Relationship del lado inverso

---
*Session*: [[session-manual-save-brian-palacios]]
*Topic*: [[topic-opsx--setup-backend-core]]
