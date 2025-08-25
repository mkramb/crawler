import sys

from loguru import logger


def configure_logging(default_level: str = "INFO"):
    logger.remove()
    logger.add(
        sys.stdout,
        level=default_level,
        backtrace=False,
        diagnose=False,
    )
