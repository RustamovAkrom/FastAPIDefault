from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.database import get_db_engine
from core.logger import configure_logger
from core.requests import get_http_transport
from modules import loaded_modules


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    db_engine = get_db_engine()
    http_transport = get_http_transport()
    logger = configure_logger()

    yield

    # module shutdown hooks
    for module in loaded_modules:
        try:
            module.shutdown()
        except Exception as ex:
            logger.error(f"Lifespan error: module shutdown function failed: {ex}")

    await db_engine.dispose()
    await http_transport.aclose()
