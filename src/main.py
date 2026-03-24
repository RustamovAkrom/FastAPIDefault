"""
Run FastAPI app with uvicorn.

    uv run src/main.py
"""

import uvicorn

from core.settings import get_settings


def main() -> None:
    settings = get_settings()

    uvicorn.run(
        "app:create_app",
        app_dir="src",
        host=settings.app_host,
        port=settings.app_port,
        reload=True,
    )


if __name__ == "__main__":
    main()
