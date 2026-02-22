# 🚀 Deployment Guide

This document describes how to deploy fastapi-default.

---

# 1. Requirements

- Docker
- Docker Compose
- PostgreSQL
- Environment variables configured

---

# 2. Environment Setup

Production .env must include:

```

DEBUG=false
SENTRY_DSN=...
POSTGRES_HOST=...
POSTGRES_PASSWORD=...

```

---

# 3. Build & Run

```

docker compose build
docker compose up -d

```

---

# 4. Apply Migrations

```

docker compose exec web alembic upgrade head

```

---

# 5. Create Admin

```

docker compose exec web python -m scripts.create_admin

```

---

# 6. Reverse Proxy (Recommended)

Use:

- Nginx
- Traefik

Proxy:

```

:80 → FastAPI

```

---

# 7. Production Setup

Recommended:

- Gunicorn with Uvicorn workers
- Redis caching
- pgbouncer for connection pooling
- HTTPS termination

---

# 8. Zero Downtime Strategy

- Blue/green deploy
- Health checks
- Rolling restart
```
