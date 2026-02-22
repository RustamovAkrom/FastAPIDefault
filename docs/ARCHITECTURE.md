# 🏗 Architecture Overview — fastapi-default

This document describes the architectural design of the project.

---

# 1. High-Level Architecture

The project follows a layered backend architecture:

```

Client → FastAPI → Service Layer → Database (PostgreSQL)
↓
Observability Stack
(Prometheus, Grafana, Sentry)

```

Core principles:

- Clean modular structure
- Async-first (SQLAlchemy async)
- Infrastructure as code (Docker + Taskfile)
- Observability-first backend
- Production-ready defaults

---

# 2. Project Structure

```

src/
├── api/              # API routers
├── admin/            # SQLAdmin configuration
├── core/             # Infrastructure core (db, settings, logging, sentry)
├── db/               # Database models and base
├── scripts/          # CLI utilities (create_admin)
├── app.py            # Application factory
└── dev.py            # Development entrypoint

````

---

# 3. Application Lifecycle

Application is created via factory pattern:

```python
def create_app() -> FastAPI:
````

Initialization order:

1. Load settings
2. Configure logger
3. Initialize Sentry (optional)
4. Register middleware
5. Register routers
6. Initialize admin panel

---

# 4. Database Layer

* PostgreSQL (Docker)
* SQLAlchemy 2.x (async)
* Alembic migrations

Key components:

* `core.database` → engine + async session
* `db.base.Base` → declarative base
* `db.models` → ORM models

Migration flow:

```
Models → Alembic autogenerate → Migration → Upgrade head
```

---

# 5. Admin Layer

Admin is powered by:

* SQLAdmin
* Custom RBAC logic
* Role protection (SUPERADMIN cannot be modified)

Admin is initialized in:

```
core/admin.py
```

---

# 6. Observability Layer

* Prometheus → metrics
* Grafana → dashboards
* Sentry → error tracking

All configured via Docker + middleware.

---

# 7. Orchestration

Taskfile is the single control interface.

```
task run
task db-up
task create_admin
task test
```

Everything is automated through tasks.

````

---

# 📁 docs/ADMIN_GUIDE.md

```md
# 🛡 Admin Panel Guide

Admin panel is powered by SQLAdmin and provides secure RBAC management.

---

# 1. Roles

Defined in:

````

db/models/user.py

```

Roles:

- superadmin
- admin
- moderator
- user

---

# 2. Access Rules

Security rules:

- SUPERADMIN cannot be edited
- SUPERADMIN cannot be deleted
- Admin cannot assign SUPERADMIN
- User cannot modify own role
- Admin cannot delete another admin

These rules are enforced inside:

```

admin/user.py

```

---

# 3. Creating Admin

Command:

```

task create_admin

```

This runs:

```

python -m scripts.create_admin

```

Creates superadmin user in DB.

---

# 4. Password Handling

- Passwords are hashed before insert
- Password updates only if provided
- Plain text is never stored

---

# 5. Admin Actions

Custom actions:

- Deactivate selected users
- Bulk operations supported

---

# 6. URL

```

[http://localhost:8000/admin](http://localhost:8000/admin)

```

Login uses DB users.

---

# 7. Extending Admin

To add a new model:

1. Create ModelView
2. Register with @register_admin
3. Define filters, columns, rules

Admin auto-loads via:

```

admin.loader.load_admin_modules()
