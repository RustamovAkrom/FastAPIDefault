 # 🚀 FastAPI Default — Production-Ready Template

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-16-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/docker-compose-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Полнофункциональный, масштабируемый и production-ready шаблон для создания современных REST API на FastAPI с учётом best practices.**

> Включает всё, что вам нужно для быстрого старта: async SQLAlchemy, миграции Alembic, мониторинг Prometheus/Grafana, интеграция Sentry, админ-панель SQLAdmin и Docker для production-деплоя.

---

## ✨ Основные возможности

- **🔥 FastAPI + Uvicorn** — асинхронный ASGI сервер для высокой производительности
- **🗄️ SQLAlchemy 2.x Async** — асинхронная работа с БД с type hints
- **📦 Alembic** — управление миграциями БД
- **🐘 PostgreSQL** — надежная реляционная БД (с поддержкой локального Docker)
- **📊 Prometheus + Grafana** — полный мониторинг приложения и инфраструктуры
- **🔔 Sentry** — track ошибок и performance monitoring
- **🛡️ SQLAdmin** — встроённая админ-панель с RBAC
- **🔐 Security Best Practices** — non-root контейнеры, resource limits, capability dropping
- **🐳 Docker + Docker Compose** — готовые конфигурации для dev и production
- **⚡ Taskfile** — удобные команды для разработки (`init`, `run`, `test`, `upgrade-db`)
- **🧪 Pytest** — готовая структура для тестирования

---

## 📋 Требования

- **Python 3.11+**
- **Docker & Docker Compose** (если используете контейнеры)
- **PostgreSQL 16** (если не используете Docker)

---

<!-- ## 📦 Установка через pip

Самый быстрый способ начать работу:

```bash
# Установите пакет
pip install fastapi-default

# Создайте новый проект на основе шаблона
fastapi-default create my-api
cd my-api

# Запустите приложение
docker compose up -d
```

📚 Полная документация по публикации на PyPI: [PUBLISHING.md](PUBLISHING.md) -->

## 🚀 Быстрый старт (Docker) — рекомендуется

### 1️⃣ Клонируйте репозиторий

```bash
git clone https://github.com/yourusername/fastapi-default.git
cd fastapi-default
```

### 2️⃣ Настройте переменные окружения

```bash
cp .env.example .env
# Отредактируйте .env по необходимости
```

### 3️⃣ Запустите приложение

```bash
docker compose up -d --build
```

### 4️⃣ Проверьте, что всё работает

```bash
# Основное API
curl http://localhost:8001/healthcheck

# Метрики Prometheus
curl http://localhost:8001/metrics

# Grafana dashboard
open http://localhost:3000
```

✅ **Готово!** Приложение работает на http://localhost:8001

---

## 🏃 Локальная разработка (без контейнеров)

### 1️⃣ Создайте виртуальное окружение

```bash
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Linux/Mac
source .venv/bin/activate
```

### 2️⃣ Установите зависимости

```bash
pip install -e ".[dev,test]"
```

### 3️⃣ Настройте БД

```bash
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=yourpassword
export POSTGRES_DB=fastapi_default
```

### 4️⃣ Запустите миграции

```bash
alembic upgrade head
```

### 5️⃣ Запустите приложение

```bash
uvicorn app:create_app --factory --reload
```

---

## 📁 Структура проекта

```
fastapi-default/
├── src/
│   ├── app.py                  # Фабрика приложения
│   ├── main.py                 # Точка входа
│   ├── api/                    # API роутеры (версионированные)
│   ├── core/                   # Конфигурация и инструменты
│   │   ├── settings.py         # Переменные окружения
│   │   ├── database.py         # SQLAlchemy engine
│   │   ├── security.py         # Bcrypt хеширование
│   │   ├── logger.py           # Loguru конфигурация
│   │   ├── monitoring.py       # Health endpoints
│   │   ├── prometheus.py       # Metrics middleware
│   │   └── sentry.py           # Sentry error tracking
│   ├── db/
│   │   ├── models/             # ORM модели (User, Product и т.д.)
│   │   ├── crud/               # CRUD операции
│   │   ├── migrations/         # Alembic DB миграции
│   │   └── dependencies.py     # Dependency injection
│   ├── admin/                  # Admin panel (SQLAdmin)
│   ├── schemas/                # Pydantic DTO модели
│   └── services/               # Внешние интеграции (Redis, RabbitMQ и т.д.)
├── tests/                      # Pytest тесты с фикстурами
├── deployments/
│   ├── compose/                # Docker Compose конфигурации
│   ├── prometheus/             # Prometheus скрейпинг конфиг
│   ├── grafana/                # Grafana dashboards и provisioning
│   └── loki/                   # Loki логирование (promtail конфиг)
├── docs/                       # Подробная документация
│   ├── ARCHITECTURE.md         # Архитектура и структура
│   ├── DEPLOYMENT.md           # Гайд по production деплою
│   ├── OBSERVABILITY.md        # Мониторинг и tracking
│   └── BACKEND_ROADMAP.md      # План развития проекта
├── docker-compose.yml          # Docker Compose stack (dev + tools)
├── Dockerfile                  # Production-ready Dockerfile
├── pyproject.toml              # Конфигурация проекта (зависимости)
├── Taskfile.yml                # Команды для разработки (task init, task run и т.д.)
└── README.md                   # Этот файл
```

---

## ⚙️ Конфигурация

### Переменные окружения (`.env`)

**Минимально обязательные:**

```env
ENV=dev                         # local | dev | test | prod
DEBUG=true

POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changeme
POSTGRES_DB=fastapi_db
```

**Опциональные (для дополнительного функционала):**

```env
# Sentry (ошибки и performance)
SENTRY_DSN=https://...@sentry.io/...

# Admin panel
ADMIN_ENABLED=true
ADMIN_USER=admin
ADMIN_PASSWORD=adminpass

# Prometheus security
PROMETHEUS_ENABLED=true
PROMETHEUS_METRICS_KEY=your-secret-key

# Логирование
LOG_LEVEL=DEBUG
LOG_JSON=false
LOG_TO_FILE=true
```

Подробный список см. в [src/core/settings.py](src/core/settings.py)

---

## 📦 Команды для разработки

Используйте **Taskfile** (или запускайте вручную):

```bash
# Инициализация проекта (БД + миграции)
task init

# Запустить приложение (dev mode с hot-reload)
task run

# Запустить тесты с покрытием
task test

# Применить миграции БД
task upgrade-db

# Создать новую миграцию
task make-migration DESC="Add new field"

# Просмотр логов Docker контейнеров
task logs

# Остановить все контейнеры
task down
```

---

## 🗄️ Работа с базой данных

### Применить миграции

```bash
# В Docker
docker compose exec web alembic upgrade head

# Локально
alembic upgrade head
```

### Создать новую миграцию

```bash
# Автогенерируемая миграция (нужно изменить модели)
alembic revision --autogenerate -m "Add user table"

# Пустая миграция
alembic revision -m "Custom migration"
```

### Откатить миграцию

```bash
alembic downgrade -1
```

---

## 🧪 Тестирование

```bash
# Все тесты
task test

# С покрытием
pytest --cov=src tests/

# Конкретный тест
pytest tests/test_dummy.py::test_something -v
```

---

## 📊 Мониторинг

### Prometheus Metrics

**http://localhost:8001/metrics**

Доступные метрики:
- `fastapi_requests_total` — всего запросов
- `fastapi_request_duration_seconds` — время ответа
- `fastapi_request_errors_total` — ошибки
- `fastapi_requests_in_progress` — запросов в процессе

### Grafana Dashboards

**http://localhost:3000**
- **Пользователь:** admin
- **Пароль:** admin

Включены готовые dashboards для мониторинга приложения и инфраструктуры.

### Sentry Error Tracking

Настроить через переменную `SENTRY_DSN`. Все ошибки в production будут автоматически трекироваться.

Подробнее см. [docs/OBSERVABILITY.md](docs/OBSERVABILITY.md)

---

## 🔐 Security бест-практики

✅ **Non-root контейнеры** — приложение работает от пользователя `appuser`  
✅ **Ограниченные capabilities** — удалены ненужные Docker permissions  
✅ **Resource limits** — CPU и memory лимиты для каждого сервиса  
✅ **Bcrypt hashing** — безопасное хранение паролей  
✅ **SQL injection protection** — параметризованные SQLAlchemy запросы  
✅ **CORS настройка** — контролируемые cross-origin запросы  

---

## 📚 Подробная документация

| Документ | Описание |
|----------|----------|
| [**ARCHITECTURE.md**](docs/ARCHITECTURE.md) | Архитектура, структура проекта, инициализация |
| [**DEPLOYMENT.md**](docs/DEPLOYMENT.md) | Production деплой (AWS, GCP, VPS, Kubernetes) |
| [**OBSERVABILITY.md**](docs/OBSERVABILITY.md) | Prometheus, Grafana, Sentry, health checks |
| [**BACKEND_ROADMAP.md**](docs/BACKEND_ROADMAP.md) | План развития, новые фичи, todo |

---

## 🐛 Часто задаваемые вопросы

**Q: Как добавить новый endpoint?**

Создайте файл в `src/api/api_v1/` и зарегистрируйте router в `src/api/router.py`

**Q: Как добавить новую модель БД?**

Создайте класс в `src/db/models/`, затем запустите `task make-migration`

**Q: Где хранятся логи приложения?**

В контейнере: `/var/log/app.log`. Локально: `logs/app.log`

**Q: Как изменить port приложения?**

Используйте переменную окружения `PORT` в `.env` или отредактируйте `docker-compose.yml`

**Q: Как использовать Redis для кеша?**

Redis уже включен в конфиге Docker Compose (закомментирован). Раскомментируйте и используйте `aioredis`

Из других вопросов см. [docs/](docs/)

---

## 💡 Примеры кода

### Создать новый API endpoint

```python
# src/api/api_v1/products.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.dependencies import get_db_session
from schemas.product import ProductSchema

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=list[ProductSchema])
async def list_products(session: AsyncSession = Depends(get_db_session)):
    return {"products": []}
```

### Написать CRUD операции

```python
# src/db/crud/product.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.product import Product

class ProductCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_all(self):
        result = await self.session.execute(select(Product))
        return result.scalars().all()
```

---

## 📦 Установка (PyPI)

**Coming soon!** Скоро будет возможность установить как pip пакет:

```bash
pip install fastapi-default

# Создать новый проект
fastapi-default create my-api
cd my-api
task init
task run
```

---

## 🤝 Contributing

Приветствуются contributions! Пожалуйста:

1. Fork репозиторий
2. Создайте branch: `git checkout -b feature/your-feature`
3. Commit: `git commit -am 'Add feature'`
4. Push: `git push origin feature/your-feature`
5. Pull Request

---

## 📄 Лицензия

MIT License. Подробнее см. [LICENSE](LICENSE)

---

## 🙏 Аккредиты

Спасибо FastAPI сообществу и open-source контрибьютерам за вдохновение!

**Используйте FastAPI Default для создания масштабируемых API!** ⭐
