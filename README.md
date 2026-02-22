# template_project

Готовый шаблон для микросервиса бекенда

- [FastAPI](https://fastapi.tiangolo.com/) - веб-фреймворк
- [uvicorn](https://www.uvicorn.org/) - ASGI сервер
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM
- [Alembic](https://alembic.sqlalchemy.org/en/latest/) - миграции
- [PostgreSQL](https://www.postgresql.org/) - реляционная база данных
- [uv](https://docs.astral.sh/uv/) - инструмент для запуска и управления приложениями
- [pytest](https://docs.pytest.org/en/7.4.x/) - тестирование
- [ruff](https://beta.ruff.rs/docs/) - линтер и автоформатер
- [mypy](https://mypy-lang.org/) - статическая типизация
- [pre-commit](https://pre-commit.com/) - хуки для git
- [docker](https://www.docker.com/) - контейнеризация
- [task](https://taskfile.dev/) - инструмент для автоматизации задач
- [sentry](https://sentry.io/) - мониторинг ошибок
- [prometheus](https://prometheus.io/) - мониторинг метрик
- [deptry](https://deptry.com/) - tool to check for issues with dependencies

## Development

### Prerequisites

- Установить [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Установить [Docker](https://docs.docker.com/get-docker/)
- Установить [Task](https://taskfile.dev/installation/) или пользоваться `uvx --from go-task-bin task`


### Running locally

- Копируем `.example.env` в `.env` и заполняем переменные окружения
- Создаем виртуальное окружение и локальную базу данных: `task init`
- Запускаем локальный сервер: `task run`
- Если обновились миграции базы данных: `task upgrade-db`

## Environment

```bash
ENV=local|test|ci|dev|prod  # default: prod
APP_TITLE="Template Project"
APP_NAME=template_project
DEBUG=true

POSTGRES_HOST=localhost
POSTGRES_PORT=33432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=exampledb
# FastAPI Template Project

Подробная документация по этому шаблону сервиса: как проект устроен, как запускать
локально и в контейнерах, как запускать тесты и как добавлять дополнительные сервисы.

## Краткий обзор

- Фреймворк: FastAPI
- ASGI-сервер: `uvicorn` / `uv` helper
- ORM: SQLAlchemy 2 (async)
- Миграции: Alembic
- БД: PostgreSQL
- Инструменты разработки: `task` (Taskfile.yml), `ruff`, `mypy`, `pytest`

Проект расположен в папке `src/`. Точка входа для разработки — `src/main.py` и фабрика
приложения `src/app.py` (`create_app()`), которая конфигурирует middleware, роуты и
обработчики ошибок.

## Быстрый старт (локально)

1. Клонируйте репозиторий и перейдите в корень проекта.

2. Подготовьте окружение (рекомендуется virtualenv):

```bash
python -m venv .venv
# Windows PowerShell
.venv\\Scripts\\Activate.ps1
# macOS / Linux
source .venv/bin/activate

# Установите пакет и зависимости для разработки и тестов
pip install -e .[dev,test]
```

3. Скопируйте файл с переменными окружения и отредактируйте значения:

```bash
# если есть примеры - используйте их, иначе создайте .env вручную
cp .env.example .env  # или создайте .env на основе документации
cp .env.test .env.test  # для локальных тестов (если есть)
```

Минимальные переменные окружения (пример):

```text
ENV=local
APP_TITLE="FastAPI Template Project"
DEBUG=true

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=exampledb

SENTRY_DSN=
PROMETHEUS_METRICS_KEY=secret
```

4. Инициализация локальной БД и зависимостей через `task` (Taskfile.yml):

```bash
# Поднимает postgres, применяет миграции и останавливает контейнер
task init

# Запустить приложение в режиме разработки (поднимает postgres при необходимости)
task run

# Применить миграции к локальной БД
task upgrade-db
```

Если вы не используете `task`, можно использовать `docker compose` и `uv` напрямую:

```bash
# Поднять сервисы в фоне (из docker-compose.yml)
docker compose up -d --wait postgres

# Запустить миграции (если установлен alembic в окружении)
uv run alembic upgrade head

# Запустить приложение:
uv run src/main.py

# Или с uvicorn напрямую:
python -m uvicorn app:create_app --reload --app-dir src
```

## Docker / Production

В репозитории есть `docker-compose.yml` и Dockerfile для backend в
[deployments/compose/backend/Dockerfile](deployments/compose/backend/Dockerfile).

Запуск всей инфраструктуры локально (контейнеры):

```bash
docker compose up --build
```

В `docker-compose.yml` сервис `web` использует `./src` как volume в режиме разработки
(чтобы изменения отражались без пересборки). Для production рекомендуется убрать
mount и собирать артефакт-образ.

## Миграции базы данных (Alembic)

Применение миграций:

```bash
task upgrade-db
# или
docker compose up -d --wait postgres
uv run alembic upgrade head
```

Создание новой миграции (пример):

```bash
uv run alembic revision --autogenerate -m "add new field to model"
uv run alembic upgrade head
```

Если вы используете `alembic` напрямую, указывайте конфигурацию `alembic.ini` из
проекта (файл `src/alembic.ini`).

## Тестирование

Локальные тесты используют отдельный контейнер `postgres-test` из `docker-compose.yml`.

```bash
# Запуск тестов через task (ENV=test будет применен автоматически)
task test

# Или вручную
docker compose up -d --wait postgres-test
ENV=test uv run pytest -q
```

Фикстуры для тестов находятся в `tests/conftest.py`. Используется `pytest` + `httpx.AsyncClient`.

## Качество кода

- Линтинг и форматирование: `task lint`, `task format` (использует `ruff`).
- Проверка типов: `task typecheck` (использует `mypy`).
- Предкоммиты: `task pre-commit`.

## Структура проекта (основные папки и файлы)

- `src/app.py` — фабрика приложения `create_app()`.
- `src/main.py` — точка запуска для `uv`/`uvicorn`.
- `src/api/` — роуты и эндпоинты. Основной роутер в [src/api/router.py](src/api/router.py#L1).
- `src/core/` — конфигурация, логгирование, lifespan, мониторинг, sentry и т.д.
- `src/db/` — конфигурация БД, модели и миграции. Базовый класс моделей: [src/db/base.py](src/db/base.py#L1).
- `src/schemas/` — pydantic-схемы.
- `src/services/` — место для интеграции внешних сервисов (redis, rabbitmq и т.п.).
- `tests/` — тесты проекта.

## Как добавить новый сервис (например Redis или RabbitMQ)

1. Добавьте переменные окружения в `.env` (хост, порт, креды).
2. В `docker-compose.yml` раскомментируйте или добавьте блок сервиса (пример для
    `redis`/`rabbitmq`) и при необходимости настройте healthcheck.
3. Добавьте интеграцию в код: создайте модуль в `src/services/` с клиентом и
    функциями инициализации/закрытия соединения.
4. Зарегистрируйте инициализацию/закрытие в `core.lifespan` или в функции
    `startup`/`shutdown` вашей фабрики приложения (`create_app`).
5. При необходимости добавьте зависимости через DI (Depends) в эндпоинтах.
6. Обновите тесты/фикстуры и документацию.

## Логирование, мониторинг и Sentry

- Логгер конфигурируется в `src/core/logger.py`.
- Метрики Prometheus подключены через middleware `src/core/prometheus.py`.
- Sentry инициализируется при наличии `SENTRY_DSN` в настройках (`src/core/sentry.py`).

## Полезные команды (резюме)

- Инициализация локальной среды: `task init`
- Запуск в режиме разработки: `task run` или `uv run src/main.py`
- Применить миграции: `task upgrade-db` или `uv run alembic upgrade head`
- Запуск тестов: `task test`
- Линт/формат/типизация: `task lint`, `task format`, `task typecheck`
- Собрать и запустить контейнеры: `docker compose up --build`

## Инструкции по ОС (PowerShell, cmd.exe, Bash)

Ниже — удобные команды для разных оболочек. Замените значения переменных на
ваши, если нужно.

PowerShell (Windows, рекомендуемый):

```powershell
# Активировать venv
.venv\Scripts\Activate.ps1

# Скопировать env (если есть пример)
cp .env.example .env

# Поднять Postgres и запустить приложение (использует Taskfile.yml)
task init
task run

# Ручной запуск миграций из папки src (если нужно):
Set-Location .\src
$env:ENV='local'
# при необходимости установить переменные DB
$env:POSTGRES_HOST='127.0.0.1'
$env:POSTGRES_PORT='5432'
$env:POSTGRES_USER='postgres'
$env:POSTGRES_PASSWORD='postgres'
$env:POSTGRES_DB='exampledb'
.venv\Scripts\python.exe -m alembic -c alembic.ini upgrade head
```

cmd.exe (Windows):

```cmd
REM Активировать venv
.venv\Scripts\activate.bat

REM Скопировать .env
copy .env.example .env

REM Использовать task (если установлен)
task init
task run

REM Ручной запуск миграций из src:
cd src
set ENV=local
set POSTGRES_HOST=127.0.0.1
set POSTGRES_PORT=5432
set POSTGRES_USER=postgres
set POSTGRES_PASSWORD=postgres
set POSTGRES_DB=exampledb
.venv\Scripts\python.exe -m alembic -c alembic.ini upgrade head
```

Bash / Zsh (Linux, macOS, WSL, Git Bash):

```bash
# Активировать venv
source .venv/bin/activate

# Скопировать .env
cp .env.example .env

# Использовать task
task init
task run

# Ручной миграции из src:
cd src
export ENV=local
export POSTGRES_HOST=127.0.0.1
export POSTGRES_PORT=5432
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
export POSTGRES_DB=exampledb
python -m alembic -c alembic.ini upgrade head
```

## Где смотреть код

- `src/app.py` — фабрика приложения (главный стартовый файл).
- `src/main.py` — точка запуска для `uv`.
- `Taskfile.yml` — задания для повседневных задач (инициализация, тесты, миграции).
- `docker-compose.yml` — локальная инфраструктура (Postgres и тестовая БД).

## Что дальше / рекомендации

- Для production: переходите на собранные Docker-образы без монтирования `./src`.
- Ограничьте `DEBUG=false` и отключите документацию (`docs_url`) в проде.
- Добавьте CI-пайплайн, который выполняет `task all` (см. `Taskfile.yml` — цель `all`).

Если хотите — могу запустить тесты локально и/или отформатировать README под
конкретные .env файлы в репозитории. Напишите, что предпочитаете.
