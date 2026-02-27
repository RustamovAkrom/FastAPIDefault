from __future__ import annotations

import sys
from pathlib import Path

import loguru
from loguru import logger

from core.settings import get_settings


def configure_logger() -> loguru.Logger:
    """
    Configure the logger for the application.
    """
    settings = get_settings()

    # Remove the default logger
    logger.remove()

    # Log level
    level = "DEBUG" if settings.debug else "INFO"

    # Console logger
    logger.add(
        sys.stdout,
        level=level,
        colorize=settings.debug,
        backtrace=settings.debug,
        diagnose=settings.debug,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> "
            "- <level>{message}</level>"
        ),
    )

    # File logger
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # general logs
    logger.add(
        log_dir / "app.log",
        rotation="10 MB",
        retention="10 days",
        enqueue=True,
        serialize=not settings.debug,  # JSON in prod
    )

    # error logs only
    logger.add(
        log_dir / "errors.log",
        level="ERROR",
        rotation="5 MB",
        retention="30 days",
        compression="zip",
        enqueue=True,
        backtrace=True,
        diagnose=True,
        serialize=True,
    )

    return loguru.logger
