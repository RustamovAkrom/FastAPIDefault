![banner](/assets/banner.png)

# FastAPI Default - Production-Ready FastAPI Template
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

- [FastAPI](https://fastapi.tiangolo.com)
- [SQLAlchemy](https://www.sqlalchemy.org)
- [Alembic](https://alembic.sqlalchemy.org)
- [PostgreSQL](https://www.postgresql.org)
- [Docker](https://www.docker.com)
- [Prometheus](https://prometheus.io)
- [Grafana](https://grafana.com)
- [Loki](https://grafana.com/oss/loki)
- [Sentry](https://sentry.io)
- [SQLAdmin](https://github.com/long2ice/sqladmin)
- [python-jose](https://github.com/mpdavis/python-jose)
- [passlib](https://passlib.readthedocs.io)

---

# 📋 Требования

Установить если у вас их нет:

- [Python **3.11+**](https://www.python.org/downloads/)
- [Docker](https://docs.docker.com/engine/install/)
- [Task (Taskfile runner)](https://taskfile.dev/installation/
)
- [UV (Package Manager)](https://docs.astral.sh/uv/getting-started/installation/)

---

# 📁 Структура проекта

```
FastAPI-Default/
├─ deployments/
│  ├─ compose/
│  │  └─ backend/
│  │     ├─ Dockerfile
│  │     ├─ entrypoint
│  │     ├─ start
│  │     └─ celery/
│  │        ├─ worker
│  │        ├─ beat
│  │        └─ flower
│  ├─ grafana/
│  │  ├─ dashboards/
│  │  │  ├─ fastapi.json
│  │  │  └─ node-exporter.json
│  │  └─ provisioning/
│  │     ├─ dashboards/dashboard.yml
│  │     └─ datasources/datasource.yml
│  ├─ loki/
│  │  └─ promtail.yml
│  └─ prometheus/
│     └─ prometheus.yml
├─ scripts/
│  └─ create_admin.py
├─ src/
│  ├─ admin/
│  │  ├─ user.py
│  │  ├─ dummy.py
│  │  └─ __init__.py
│  ├─ api/
│  │  ├─ api_v1/
│  │  │  ├─ dummy.py
│  │  │  └─ __init__.py
│  │  ├─ router.py
│  │  └─ __init__.py
│  ├─ core/
│  │  ├─ admin.py
│  │  ├─ admin_permissions.py
│  │  ├─ database.py
│  │  ├─ exceptions.py
│  │  ├─ lifespan.py
│  │  ├─ logger.py
│  │  ├─ monitoring.py
│  │  ├─ prometheus.py
│  │  ├─ requests.py
│  │  ├─ security.py
│  │  ├─ sentry.py
│  │  ├─ settings.py
│  │  └─ __init__.py
│  ├─ db/
│  │  ├─ crud/
│  │  │  ├─ dummy.py
│  │  │  └─ __init__.py
│  │  ├─ migrations/
│  │  │  ├─ versions/
│  │  │  ├─ env.py
│  │  │  ├─ script.py.mako
│  │  │  └─ README
│  │  ├─ models/
│  │  │  ├─ user.py
│  │  │  ├─ dummy.py
│  │  │  └─ __init__.py
│  │  ├─ base.py
│  │  ├─ dependencies.py
│  │  └─ meta.py
│  ├─ logs/
│  │  ├─ app.log
│  │  └─ errors.log
│  ├─ middlewares/
│  ├─ schemas/
│  │  ├─ base.py
│  │  ├─ dummy.py
│  │  └─ __init__.py
│  ├─ services/
│  │  └─ __init__.py
│  ├─ alembic.ini
│  ├─ app.py
│  ├─ dev.py
│  └─ main.py
├─ tests/
│  ├─ conftest.py
│  ├─ test_dummy.py
│  └─ __init__.py
├─ .dockerignore
├─ .env
├─ .env.ci
├─ .env.example
├─ .env.local
├─ .env.test
├─ .gitignore
├─ .gitlab-ci.yml
├─ .pre-commit-config.yaml
├─ README.md
├─ Taskfile.yml
├─ docker-compose.yml
├─ pyproject.toml
└─ uv.lock

```

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
