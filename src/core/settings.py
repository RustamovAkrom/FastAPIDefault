import os
from functools import cache
from typing import Literal

from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict
from yarl import URL

ENV_FILE_PATH = (
    {
        "local": ".env",
        "dev": ".env.dev",
        "test": ".env.test",
        "ci": ".env.ci",
        "prod": ".env",
    }
).get(os.getenv("ENV", "local"), ".env")


class Settings(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

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

    env: Literal["local", "test", "ci", "dev", "prod"] = "local"

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

    # Admin panel settings
    admin_enabled: bool = False
    admin_user: str | None = None
    admin_password: str | None = None
    admin_path: str = "/admin"

    # Observability
    prometheus_enabled: bool = True
    prometheus_metrics_key: str | None = None

    # Loki
    loki_enabled: bool = True
    loki_url: str = "http://loki:3100"

    # Grafana
    grafana_url: str = "http://grafana:3000"

    # Sentry
    sentry_dsn: str | None = None
    sentry_traces_sample_rate: float = 1.0

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_json: bool = False
    log_to_file: bool = False
    log_file_path: str = "logs/app.log"

    # Security
    allowed_hosts: list[str] = ["*"]

    # Build helpers
    @property
    def is_prod(self) -> bool:
        return self.env == "prod"
    
    @property
    def is_dev(self) -> bool:
        return self.env in ("local", "dev")
    
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


# Settings singleton
@cache
def get_settings() -> Settings:
    return Settings()
