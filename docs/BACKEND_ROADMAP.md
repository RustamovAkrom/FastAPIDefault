# 🗺 Backend Roadmap — дорожная карта развития

Короткая дорожная карта с приоритетами и практическими шагами.

---

## Этап 1 — Foundation (DONE)

- FastAPI core
- Async SQLAlchemy
- Alembic
- Docker + docker-compose
- Taskfile (локальные задачи)
- Admin panel + RBAC

---

## Этап 2 — Observability (DONE)

- Prometheus (метрики)
- Grafana (дашборды)
- Sentry (ошибки)
- Middleware для метрик

---

## Этап 3 — Performance Optimization (план)

- Redis caching (сценарии и TTL для ключей)
- DB query metrics и оптимизация горячих запросов
- Настройка pgbouncer для connection pooling
- Нормализация endpoint-ов и кеширование

---

## Этап 4 — Background Processing

- Celery + брокер (RabbitMQ/Redis)
- Политики retry и dead-letter
- Метрики выполнения задач и мониторинг (Flower / Prometheus)

---

## Этап 5 — Advanced Observability

- OpenTelemetry для распределённой трассировки
- Интеграция трассировок с Grafana/Jaeger
- Централизованное логирование (например, Loki/Elasticsearch)

---

## Этап 6 — Security

- Rate limiting (API gateway / middleware)
- Audit logs для критичных операций
- JWT rotation и token revocation lists
- Политики rotating secrets

---

## Этап 7 — Scalability

- Горизонтальное масштабирование сервисов
- Load balancer + healthchecks
- Kubernetes + Helm charts (deployment manifests)

---

## Этап 8 — Enterprise

- Multi-tenant architecture (по необходимости)
- Feature flags и постепенные релизы
- Blue/green / Canary deploy
- SLA мониторинг и runbooks

---

Если хотите — разложу конкретный план на 3 месяца с задачами и приоритетами
для команды (issues и примеры конфигураций для Redis/pgbouncer/Celery).
