import logging
import sys

from backend.config import settings


def setup_logging() -> None:
    level_name = (
        settings.LOG_LEVEL.upper()
        if settings.LOG_LEVEL
        else ("INFO" if settings.APP_ENV == "prod" else "DEBUG")
    )
    level = getattr(logging, level_name, logging.INFO)

    logging.basicConfig(
        level=level,
        stream=sys.stdout,
        format="%(levelname)s %(name)s %(message)s",
        force=True,
    )

    for name in ("uvicorn", "uvicorn.access"):
        logging.getLogger(name).setLevel(level)
