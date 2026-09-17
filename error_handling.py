"""Configure application logging and report exceptions from game actions."""

import logging
import sys
from enum import Enum
from functools import wraps
from logging.handlers import RotatingFileHandler
from typing import Callable, ParamSpec, TypeVar

# Type variables for decorators
P = ParamSpec("P")
R = TypeVar("R")


class ErrorSeverity(Enum):
    """Error severity for categorization."""

    LOW = "low"  # Minor issues, recoverable
    MEDIUM = "medium"  # Significant issues, may affect functionality
    HIGH = "high"  # Major issues, core functionality affected
    CRITICAL = "critical"  # System-threatening, immediate attention needed


logger = logging.getLogger("sudoku")
logger.setLevel(logging.DEBUG)
logger.propagate = False

if not logger.handlers:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s", "%H:%M:%S")
    )
    logger.addHandler(console_handler)

    try:
        from persistence import get_data_dir

        log_dir = get_data_dir() / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        file_format = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
        file_handler = RotatingFileHandler(
            log_dir / "sudoku.log", maxBytes=2_000_000, backupCount=3, encoding="utf-8"
        )
        error_handler = RotatingFileHandler(
            log_dir / "sudoku_errors.log", maxBytes=2_000_000, backupCount=3, encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_format)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
        logger.addHandler(error_handler)
    except OSError as exc:
        logger.warning("File logging is unavailable: %s", exc)


def log_exception(
    severity: ErrorSeverity = ErrorSeverity.HIGH,
    user_action: str | None = None,
):
    """Log a game-action exception and re-raise it."""

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                return func(*args, **kwargs)
            except Exception:
                logger.exception("[%s] %s", severity.value.upper(), user_action or func.__name__)
                raise

        return wrapper

    return decorator
