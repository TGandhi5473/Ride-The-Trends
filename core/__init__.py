from .config import Config
from .database import get_neon_engine, save_to_bronze_batch, fetch_gold_prompts
from .logger import setup_logger
from .factory import ScraperFactory
from .exceptions import (
    RideTheTrendsError,
    QuotaExceededError,
    DatabaseConnectionError,
    ProviderAuthenticationError
)

# This defines what is exposed when someone does "from core import *"
__all__ = [
    "Config",
    "get_neon_engine",
    "save_to_bronze_batch",
    "fetch_gold_prompts",
    "setup_logger",
    "ScraperFactory",
    "RideTheTrendsError",
    "QuotaExceededError",
    "DatabaseConnectionError",
    "ProviderAuthenticationError"
]
