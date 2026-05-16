import logging
import sys
from logging.config import dictConfig
from typing import Optional


def configure_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    handlers: dict[str, dict] = {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "default",
            "level": level,
        },
    }
    root_handlers = ["console"]

    if log_file:
        handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": log_file,
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "encoding": "utf-8",
            "formatter": "default",
            "level": level,
        }
        root_handlers.append("file")

    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": handlers,
        "root": {
            "level": level,
            "handlers": root_handlers,
        },
        "loggers": {
            "werkzeug": {"level": "WARNING"},
            "sqlalchemy.engine": {"level": "WARNING"},
        },
    })
    logging.captureWarnings(True)
