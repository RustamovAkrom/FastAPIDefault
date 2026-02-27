# 🏗 Архитектура FastAPI Default

Подробное описание архитектурных решений, структуры проекта и порядка инициализации приложения.

---

## 📐 Общая архитектура

FastAPI Default использует **трёхслойную архитектуру**:

```
┌─────────────────────────────────────────────────────────┐
│                     Client (Web/Mobile)                  │
└────────────────────────┬────────────────────────────────┘
                         │
                    HTTP(S) Request
                         │
┌────────────────────────▼────────────────────────────────┐
│                    FastAPI Handler                       │
│   (Request validation, routing, exception handling)      │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                  Business Logic Layer                    │
│     (Services, CRUD operations, validations)            │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                   Database Layer                         │
│    (SQLAlchemy ORM, PostgreSQL, Migrations)             │
└─────────────────────────────────────────────────────────┘
```

**Дополнительные компоненты:**
- 📊 **Observability:** Prometheus, Grafana, Sentry
- 🛡️ **Security:** JWT, RBAC, Password hashing
- 🔧 **Infrastructure:** Docker, Alembic миграции, Taskfile

---

## 📁 Структура проекта

### Корень приложения: `src/`

```
src/
├── app.py                      # Фабрика приложения FastAPI
├── main.py                     # Точка входа (uvicorn)
│
├── api/                        # REST API endpoints
│   ├── router.py              # Главный router (версионирование)
│   └── api_v1/                # API версия 1
│       ├── dummy.py           # Example endpoint
│       └── ...
│
├── core/                       # Конфигурация и инструменты
│   ├── settings.py            # Переменные окружения (Pydantic Settings)
│   ├── database.py            # SQLAlchemy engine и сессии
│   ├── security.py            # Bcrypt, password operations
│   ├── logger.py              # Loguru конфигурация
│   ├── lifespan.py            # FastAPI lifespan (startup/shutdown)
│   ├── exceptions.py          # Exception handlers
│   ├── monitoring.py          # Health, status, version endpoints
│   ├── prometheus.py          # Prometheus metrics middleware
│   ├── sentry.py              # Sentry error tracking
│   └── requests.py            # HTTP client configuration
│
├── db/                         # Database layer
│   ├── base.py                # SQLAlchemy Base (DeclarativeBase)
│   ├── meta.py                # Metadata для миграций
│   ├── dependencies.py        # Dependency injection (get_db_session)
│   │
│   ├── models/                # ORM модели
│   │   ├── __init__.py
│   │   ├── user.py            # User модель с RBAC
│   │   ├── dummy.py           # Example модель
│   │   └── ...
│   │
│   ├── crud/                  # CRUD операции
│   │   ├── __init__.py
│   │   ├── dummy.py           # Example CRUD класс
│   │   └── ...
│   │
│   └── migrations/            # Alembic миграции
│       ├── env.py             # Alembic конфигурация
│       ├── script.py.mako     # Шаблон миграций
│       └── versions/          # DB миграции (по дате)
│           ├── 2026-02-22_initial.py
│           └── ...
│
├── admin/                      # Admin panel (SQLAdmin)
│   ├── __init__.py            # Models loader
│   ├── auth.py                # Admin authentication
│   ├── user.py                # User admin с RBAC
│   ├── dummy.py               # Example admin
│   └── ...
│
├── schemas/                    # Pydantic DTO модели
│   ├── __init__.py
│   ├── base.py                # BaseSchema с конфигурацией
│   ├── dummy.py               # Example schemas
│   └── ...
│
├── services/                   # Внешние интеграции
│   ├── __init__.py
│   └── ...                     # Redis, RabbitMQ, email и т.д.
│
└── logs/                       # Логи приложения
    ├── app.log
    └── errors.log
```

---

## 🔄 Жизненный цикл приложения

### 1️⃣ Инициализация

```python
# src/main.py
if __name__ == "__main__":
    uvicorn.run(
        "app:create_app",      # Фабрика приложения
        app_dir="src",
        host="0.0.0.0",
        port=8000,
        reload=True             # Development mode
    )
```

### 2️⃣ Создание приложения (Application Factory)

```python
# src/app.py - create_app()
1. configure_logger()           # Конфигурация Loguru
2. get_settings()               # Загрузка переменных окружения
3. init_sentry()                # Sentry инициализация (если SENTRY_DSN)
4. app = FastAPI(...)           # Создание FastAPI инстанса
5. app.add_middleware(...)      # Middleware регистрация
   - MetricsMiddleware
   - CORSMiddleware
6. app.include_router(...)      # Router регистрация
7. register_exception_handlers() # Exception handlers
8. init_admin(app)              # Admin панель инициализация
9. return app
```

### 3️⃣ Обработка запроса

```
Request → Middleware chain → Router → Handler (business logic) → Database → Response
```

### 4️⃣ Graceful Shutdown

```python
# lifespan context manager
async def lifespan(app: FastAPI):
    # Startup (yield до этой линии)
    yield
    # Shutdown (код после yield)
    await db_engine.dispose()
    await http_transport.aclose()
```

---

## 💾 Работа с базой данных

### Архитектура

```
src/core/database.py (engine, session_factory)
        ↓
src/db/models/* (ORM классы)
        ↓
src/db/crud/* (CRUD операции)
        ↓
src/api/* (Endpoints)
```

###流程 миграций

```
1. Изменить ORM модель (добавить поле, новую таблицу и т.д.)
2. alembic revision --autogenerate -m "описание"
3. Проверить сгенерированную миграцию (src/db/migrations/versions/)
4. alembic upgrade head (применить миграцию)
```

### Асинхронность

- Все операции в `src/db/crud/` используют `async def`
- SQLAlchemy 2.x с `AsyncSession` для неблокирующих запросов
- Зависимость `get_db_session` в endpoints для внедрения сессии

```python
async def get_users(session: AsyncSession = Depends(get_db_session)):
    # session уже создана и подготовлена
    result = await session.execute(select(User))
    return result.scalars().all()
```

---

## 🔐 Admin Panel & RBAC

### Структура RBAC

```
UserRole (Enum):
  - SUPERADMIN (полный доступ, защищён от удаления)
  - ADMIN (может управлять обычными пользователями)
  - MODERATOR (pode moderiros контента)
  - USER (обычный пользователь)
```

### Admin Panel Features

- SQLAdmin автоматически генерирует CRUD интерфейс для моделей
- В `src/admin/user.py` реализованы правила RBAC:
  - SUPERADMIN не может быть изменён/удалён
  - ADMIN может назначать роли ниже его уровня
  - Пользователь не может менять свою роль

---

## 📊 Observability Stack

### Prometheus

- **Middleware:** `src/core/prometheus.py` автоматически собирает метрики
- **Endpoint:** `/metrics` для скрейпинга Prometheus
- **Метрики:**
  - `fastapi_requests_total` — всего запросов
  - `fastapi_request_duration_seconds` — latency
  - `fastapi_request_errors_total` — ошибки
  - `fastapi_requests_in_progress` — concurrent requests

### Grafana

- Dashboard автоматически подключается к Prometheus
- Визуализация метрик приложения и инфраструктуры в реальном времени

### Sentry

- Автоматическое tracking ошибок при `SENTRY_DSN`
- Performance monitoring включен (сэмплирование запросов)
- Интеграция с логированием

### Логирование

- **Loguru** вместо стандартного logging
- **Структурированные логи** для production
- Логи в файлы: `logs/app.log` и `logs/errors.log`

---

## 🐳 Docker & Deployment

### Multi-stage Dockerfile

```dockerfile
Stage 1: Builder
  ├── Копирует pyproject.toml
  ├── Устанавливает зависимости через uv
  └── Создаёт виртуальное окружение

Stage 2: Runtime
  ├── Копирует виртуальное окружение
  ├── Копирует исходный код
  ├── Создаёт non-root пользователя (appuser)
  └── Запускает entrypoint
```

### Docker Compose Stack

```yaml
services:
  postgres              # PostgreSQL БД
  postgres-test         # Тестовая БД (isolated)
  web                   # FastAPI приложение
  prometheus            # Метрики скрейпинг
  grafana              # Dashboard
  loki                 # Логирование
  promtail             # Log collection
```

---

## 🔀 Поток запроса (Request Flow)

```
1. Client → HTTP Request
2. Uvicorn → ReceiveRequest
3. MetricsMiddleware.dispatch()
   ├── IN_PROGRESS.inc()
   └── Start timer
4. CORSMiddleware (если нужно)
5. FastAPI Router matching
6. Handler function (async def endpoint(...))
   ├── Validate request
   ├── Inject dependencies (session, auth и т.д.)
   ├── Business logic
   └── Query database
7. MetricsMiddleware.dispatch()
   ├── Record duration
   ├── IN_PROGRESS.dec()
   ├── REQUEST_TOTAL.inc()
   └── REQUEST_DURATION.observe()
8. Response serialization (ORJSONResponse)
9. Send response to client
10. (Optional) Sentry track if error
```

---

## 🎯 Best Practices используемые в проекте

✅ **Async-first:** Все I/O операции неблокирующие  
✅ **Type Hints:** PEP 604 Python 3.11+ style (`str | None` вместо `Optional[str]`)  
✅ **Dependency Injection:** FastAPI `Depends()` для инъекции зависимостей  
✅ **Settings Management:** Pydantic BaseSettings для конфигурации  
✅ **Database Migrations:** Alembic версионирование схемы  
✅ **RBAC:** Role-based access control в админ-панели  
✅ **Observability:** Prometheus + Grafana + Sentry  
✅ **Security:** Non-root контейнеры, capability dropping, bcrypt hashing  
✅ **Error Handling:** Centralized exception handlers  
✅ **Logging:** Structured logging с Loguru  

---

## 📈 Масштабирование

### Горизонтальное масштабирование

```
Load Balancer
    ↓
┌─────────────────────────────────┐
│ FastAPI Instance 1              │
│ FastAPI Instance 2              │
│ FastAPI Instance 3              │
└────────────┬────────────────────┘
             ↓
        PostgreSQL (shared)
```

- Используйте `docker compose scale web=3` для локального тестирования
- На production используйте Kubernetes или load balancer (nginx, HAProxy)
- Используйте Redis для сессий и кеша (если несколько инстансов)

### Вертикальное масштабирование

- Увеличьте `WORKERS` в `start` скрипте
- Увеличьте resource limits в docker-compose.yml
- Оптимизируйте database queries (индексы, explain plan)

---

## 💡 Где смотреть код для быстрого погружения

| Что хотите понять | Куда смотреть |
|------------------|--------------|
| Как всё инициализируется | `src/app.py` (create_app) |
| REST endpoints | `src/api/` и `src/api/api_v1/*` |
| Как работает БД | `src/core/database.py` и `src/db/crud/` |
| Admin panel | `src/admin/` |
| Мониторинг | `src/core/prometheus.py` и `src/core/monitoring.py` |
| Конфигурация | `src/core/settings.py` |
| Бизнес-логика | `src/db/crud/` и `src/services/` |

---

## 🔗 Связанная документация

- [**DEPLOYMENT.md**](DEPLOYMENT.md) — Production деплой
- [**OBSERVABILITY.md**](OBSERVABILITY.md) — Мониторинг и tracking
- [**BACKEND_ROADMAP.md**](BACKEND_ROADMAP.md) — План развития
