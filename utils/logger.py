"""
utils/logger.py
----------------
Structured logging with loguru.
Console + rotating file handler.
"""

import sys
from loguru import logger
from config.settings import settings

logger.remove()

logger.add(
    sys.stdout,
    level=settings.LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:<8}</level> | <cyan>{name}:{line}</cyan> | {message}",
    colorize=True,
)

logger.add(
    settings.LOG_FILE,
    level=settings.LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{line} | {message}",
    rotation="10 MB",
    retention="7 days",
    compression="zip",
)