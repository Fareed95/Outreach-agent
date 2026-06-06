"""
utils/retry.py
---------------
Async retry decorator using tenacity.
Default: 3 attempts, exponential backoff (2s → 4s → 8s).
"""

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
    retry_if_exception_type,
)
from utils.logger import logger
import logging

async_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=8),
    retry=retry_if_exception_type(Exception),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)