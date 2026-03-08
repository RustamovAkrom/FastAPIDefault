# 🚀 FastAPI Default — Production-Ready FastAPI Template

Репозиторий:  
https://github.com/RustamovAkrom/FastAPIDefault

**FastAPI Default** — production-ready шаблон backend-сервиса на **FastAPI**, включающий:

- Async SQLAlchemy
- Alembic migrations
- PostgreSQL
- Prometheus / Grafana / Loki monitoring
- Sentry error tracking
- SQLAdmin admin panel
- Docker + Docker Compose
- Taskfile automation
- Production-ready конфигурацию

Проект предназначен для **быстрого старта production backend сервиса** с соблюдением современных best practices.

---

# 📦 Основные технологии

- FastAPI — https://fastapi.tiangolo.com  
- SQLAlchemy — https://www.sqlalchemy.org  
- Alembic — https://alembic.sqlalchemy.org  
- PostgreSQL — https://www.postgresql.org  
- Docker — https://www.docker.com  
- Prometheus — https://prometheus.io  
- Grafana — https://grafana.com  
- Loki — https://grafana.com/oss/loki  
- Sentry — https://sentry.io  
- SQLAdmin — https://github.com/long2ice/sqladmin  
- python-jose — https://github.com/mpdavis/python-jose  
- passlib — https://passlib.readthedocs.io  

---

# 📋 Требования

Перед запуском проекта установите:

- Python **3.11+**
- Docker
- Docker Compose
- Task (Taskfile runner)

Установить **Task** можно с официального сайта:

https://taskfile.dev/installation/

---

# 📁 Структура проекта

```

FastAPIDefault
│
├─ src
│  ├─ api
│  ├─ admin
│  ├─ core
│  ├─ db
│  │  ├─ models
│  │  └─ migrations
│  ├─ schemas
│  └─ services
│
├─ deployments
│  ├─ compose
│  │  └─ backend
│  │     └─ Dockerfile
│  ├─ grafana
│  ├─ loki
│  └─ prometheus
│
├─ tests
├─ docker-compose.yml
├─ Taskfile.yml
├─ pyproject.toml
└─ README.md

````

---

# ⚙️ Переменные окружения

Проект использует **Pydantic Settings**.

Файл `.env` выбирается автоматически по переменной `ENV`.

| ENV | используемый файл |
|----|----|
| local | `.env.local` |
| test | `.env.test` |
| ci | `.env.ci` |
| prod | `.env` |

---

# 🧾 Минимальный `.env.local`

Создайте файл `.env.local`.

Пример конфигурации:

```env
ENV=local
APP_TITLE="FastAPI Default"
APP_NAME=fastapidefault
DEBUG=true
SECRET_KEY="your-secret-key-minimum-32-chars-change-this-in-production"

POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=fastapi_default
POSTGRES_TIMEOUT=30

API_V1_STR=/api/v1
PROJECT_NAME=FastAPI Default

ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

CORS_ORIGINS=["http://localhost:3000","http://localhost:8001","http://localhost:9090"]
CORS_ALLOW_CREDENTIALS=true

DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_RECYCLE=3600
DB_POOL_PRE_PING=true

LOG_LEVEL=INFO

SENTRY_DSN=
SENTRY_ENVIRONMENT=prod
SENTRY_TRACES_SAMPLE_RATE=0.1

PROMETHEUS_ENABLED=true
PROMETHEUS_METRICS_KEY=

ADMIN_ENABLED=true
ADMIN_USER=
ADMIN_PASSWORD=
ADMIN_PATH=/admin

COMPOSE_PROJECT_NAME=fastapi-default
WORKERS=2
````

---

# 🚀 Быстрый старт

### 1. Клонировать репозиторий

```bash
git clone https://github.com/RustamovAkrom/FastAPIDefault.git
cd FastAPIDefault
```

---

### 2. Создать `.env.local`

```
cp .env.example .env.local
```

или создать вручную.

---

### 3. Инициализация проекта

```
task init
```

Команда выполнит:

* установку зависимостей
* запуск PostgreSQL
* применение миграций
* остановку контейнеров

---

### 4. Запуск проекта (dev режим)

```
task run
```

или

```
task dev
```

Приложение будет доступно:

```
http://localhost:8001
```

---

# 🐳 Production запуск (Docker)

```
docker compose up -d --build
```

После запуска API будет доступен:

```
http://localhost:8001
```

Контейнер внутри Docker использует порт **8000**,
но наружу он пробрасывается как **8001**.

```
ports:
  - 8001:8000
```

---

# 📊 Monitoring

Запустить monitoring stack:

```
task obs
```

Доступные сервисы:

| сервис     | адрес                                          |
| ---------- | ---------------------------------------------- |
| Prometheus | [http://localhost:9090](http://localhost:9090) |
| Grafana    | [http://localhost:3000](http://localhost:3000) |
| Loki       | [http://localhost:3100](http://localhost:3100) |

Метрики приложения:

```
http://localhost:8001/metrics
```

Healthcheck:

```
http://localhost:8001/healthcheck
```

---

# 🧾 Команды Taskfile

Все основные операции выполняются через **Taskfile**.

---

## Development

```
task init
```

Инициализация проекта.

```
task run
```

Запуск FastAPI dev server.

```
task dev
```

Запуск uvicorn с hot reload.

```
task stack
```

Запуск полного стека (DB + monitoring + migrations).

---

## Docker

```
task up
```

Запуск postgres.

```
task down
```

Остановить контейнеры.

```
task restart
```

Перезапуск инфраструктуры.

```
task logs
```

Просмотр логов.

---

## Database

Создать миграцию:

```
task db-revision MSG="add new table"
```

Создает новую Alembic миграцию.

```
task db-migrate
```

Применяет все миграции базы данных.

```
task db-reset
```

⚠ **ОПАСНО:** удаляет Docker volumes и полностью **стирает базу данных**.
Команда выполняет `docker compose down -v`.
Использовать **только в development**.

```
task db-shell
```

Открывает PostgreSQL shell внутри контейнера.

---

## Admin

```
task admin-create
```

Создает администратора.

Админ панель доступна:

```
http://localhost:8001/admin
```

---

## Monitoring

```
task obs
```

Запускает Prometheus, Grafana и Loki.

```
task obs-down
```

Останавливает monitoring stack.

---

## Code Quality

```
task lint
```

Запуск Ruff линтера.

```
task format
```

Форматирование кода.

```
task deps
```

Проверка зависимостей.

```
task typecheck
```

Проверка типов (MyPy).

---

## Тесты

```
task test
```

Запуск unit тестов.

```
task test-cov
```

Запуск тестов с покрытием.

---

# 🧪 Проверка после запуска

```
curl http://localhost:8001/healthcheck
```

```
curl http://localhost:8001/metrics
```

---

# 📄 Лицензия

#### [MIT License](/LICENSE)
