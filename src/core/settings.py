import os
from functools import cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict
from yarl import URL

ENV_FILE_PATH = (
    {
        "local": ".env.local",
        "test": ".env.test",
        "prod": ".env",
    }
).get(os.getenv("ENV", "local"), ".env")


class Settings(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        extra="allow",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return super().settings_customise_sources(
            settings_cls,
            init_settings,
            dotenv_settings,
            env_settings,
            file_secret_settings,
        )

    # APP CORE
    app_title: str = "FastAPI Template Project"
    app_name: str = "fastapidefault"
    app_version: str = "1.0.0"
    api_v1_str: str = "/api/v1"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    env: Literal["local", "test", "ci", "prod"] = "local"

    debug: bool = True
    root_path: str = ""

    secret_key: str = "change-this-secret-key-in.env-file"  # noqa:S105

    # service name for logs/traces
    service_name: str = "fastapi-backend"

    # Postgres
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = ""
    postgres_db: str = ""
    postgres_echo: bool = False

    # connection pool
    db_pool_size: int = 10
    db_max_overflow: int = 20

    # JWT tokens
    jwt_secret_key: str = secret_key
    jwt_refresh_secret_key: str = secret_key
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # Admin panel settings
    admin_enabled: bool = debug
    admin_user: str | None = None
    admin_password: str | None = None
    admin_path: str = "/admin"

    # Observability
    prometheus_enabled: bool = True
    prometheus_metrics_key: str | None = None

    # Loki
    loki_enabled: bool = False
    loki_url: str = "http://loki:3100"

    # Grafana
    grafana_enabled: bool = False
    grafana_url: str = "http://grafana:3000"

    # Sentry
    sentry_enabled: bool = False
    sentry_dsn: str | None = None
    sentry_environment: Literal["local", "test", "ci", "prod"] = env
    sentry_traces_sample_rate: float = 1.0

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_json: bool = False
    log_to_file: bool = False
    log_file_path: str = "logs/app.log"

    # Rate limiting
    rate_limit_enabled: bool = False
    rate_limit_default: str = "100/minute"
    rate_limit_storage_url: str = "memory://"

    # Security
    allowed_hosts: list[str] = ["*"]
    cors_origins: list[str] = ["http://localhost:3000"]

    # Build helpers
    @property
    def is_prod(self) -> bool:
        return self.env == "prod"

    @property
    def is_local(self) -> bool:
        return self.env in ("local",)

    # Database urls
    @property
    def postgres_url(self) -> str:
        return str(
            URL.build(
                scheme="postgresql+asyncpg",
                host=self.postgres_host,
                port=self.postgres_port,
                user=self.postgres_user,
                password=self.postgres_password,
                path=f"/{self.postgres_db}",
            )
        )

    @property
    def postgres_sync_url(self) -> str:
        return self.postgres_url.replace("+asyncpg", "")

    # static files
    static_root: str = "static"
    static_url: str = "/static"

    # Media files
    media_root: str = "media"
    media_url: str = "/media"
    max_upload_size_mb: int = 5

    allowed_image_extensions: list[str] = [
        "jpg",
        "jpeg",
        "png",
        "webp",
    ]

    # Email (SMPT)
    smpt_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    smtp_from_email: str = "noreply@example.com"
    smtp_from_name: str = "FastAPI Default"

    smtp_starttls: bool = True
    smtp_ssl: bool = False

    # Celery
    celery_enabled: bool = False

    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"

    celery_task_serializer: str = "json"
    celery_result_serializer: str = "json"
    celery_accept_content: list[str] = ["json"]

    celery_timezone: str = "UTC"


# Settings singleton
@cache
def get_settings() -> Settings:
    return Settings()
