"""
Comprehensive error handling and logging system for Sudoku.
Provides structured logging, error tracking, and graceful degradation.
"""

import json
import logging
import sys
import threading
import time
import traceback
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from functools import wraps
from logging.handlers import RotatingFileHandler
from typing import Callable, Optional, ParamSpec, TypeVar

# Type variables for decorators
P = ParamSpec("P")
R = TypeVar("R")


class LogLevel(Enum):
    """Log levels matching standard logging module."""

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class ErrorSeverity(Enum):
    """Error severity for categorization."""

    LOW = "low"  # Minor issues, recoverable
    MEDIUM = "medium"  # Significant issues, may affect functionality
    HIGH = "high"  # Major issues, core functionality affected
    CRITICAL = "critical"  # System-threatening, immediate attention needed


@dataclass
class ErrorContext:
    """Context information for errors."""

    error_id: str
    timestamp: str
    severity: ErrorSeverity
    message: str
    exception_type: str
    traceback_str: str
    module: str
    function: str
    line_number: int
    user_action: Optional[str] = None
    game_state: Optional[dict] = None
    additional_data: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class GameLogger:
    """Centralized logging system for the Sudoku game."""

    _instance: Optional["GameLogger"] = None
    _lock = threading.Lock()
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._setup_logging()
        self._error_history: list[ErrorContext] = []
        self._max_history = 1000
        self._metrics_lock = threading.Lock()

    def _setup_logging(self):
        """Configure logging with multiple handlers."""
        self.logger = logging.getLogger("sudoku")
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False

        # Close existing handlers before replacing them (e.g. during reconfiguration).
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
            handler.close()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s", datefmt="%H:%M:%S"
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)

        try:
            from persistence import get_data_dir

            log_dir = get_data_dir() / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            file_format = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            error_format = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s\n%(exc_info)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler = RotatingFileHandler(
                log_dir / "sudoku.log", maxBytes=2_000_000, backupCount=3, encoding="utf-8"
            )
            error_handler = RotatingFileHandler(
                log_dir / "sudoku_errors.log",
                maxBytes=2_000_000,
                backupCount=3,
                encoding="utf-8",
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(file_format)
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(error_format)
            self.logger.addHandler(file_handler)
            self.logger.addHandler(error_handler)
        except OSError as exc:
            self.logger.warning("File logging is unavailable: %s", exc)

    def debug(self, message: str, **kwargs):
        self.logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs):
        self.logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs):
        self.logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs):
        self.logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs):
        self.logger.critical(message, **kwargs)

    def log_exception(
        self,
        exc: Exception,
        severity: ErrorSeverity = ErrorSeverity.HIGH,
        user_action: Optional[str] = None,
        game_state: Optional[dict] = None,
        additional_data: Optional[dict] = None,
    ) -> ErrorContext:
        """Log an exception with full context."""
        tb = traceback.extract_tb(exc.__traceback__)
        last_frame = tb[-1] if tb else None

        error_context = ErrorContext(
            error_id=f"ERR-{int(time.time() * 1000)}",
            timestamp=datetime.now().isoformat(),
            severity=severity,
            message=str(exc),
            exception_type=type(exc).__name__,
            traceback_str="".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
            module=last_frame.filename if last_frame else "unknown",
            function=last_frame.name if last_frame else "unknown",
            line_number=last_frame.lineno if last_frame and last_frame.lineno is not None else 0,
            user_action=user_action,
            game_state=game_state,
            additional_data=additional_data or {},
        )

        with self._metrics_lock:
            self._error_history.append(error_context)
            if len(self._error_history) > self._max_history:
                self._error_history = self._error_history[-self._max_history :]

        # Log to standard logger
        self.logger.error(
            f"[{severity.value.upper()}] {error_context.error_id} | {error_context.message}",
            exc_info=exc,
        )

        return error_context

    def get_error_history(
        self, limit: int = 100, severity: Optional[ErrorSeverity] = None
    ) -> list[ErrorContext]:
        """Get recent error history."""
        with self._metrics_lock:
            errors = self._error_history
            if severity:
                errors = [e for e in errors if e.severity == severity]
            return errors[-limit:]

    def export_errors(self, filepath: str, severity: Optional[ErrorSeverity] = None):
        """Export error history to JSON file."""
        errors = self.get_error_history(limit=self._max_history, severity=severity)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump([e.to_dict() for e in errors], f, ensure_ascii=False, indent=2)


# Global logger instance
logger = GameLogger()


def log_exception(
    severity: ErrorSeverity = ErrorSeverity.HIGH,
    user_action: Optional[str] = None,
    game_state: Optional[dict] = None,
    additional_data: Optional[dict] = None,
):
    """Decorator to automatically log exceptions."""

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.log_exception(
                    e,
                    severity=severity,
                    user_action=user_action or f"Calling {func.__name__}",
                    game_state=game_state,
                    additional_data=additional_data,
                )
                raise

        return wrapper

    return decorator


# Convenience functions
def get_logger() -> GameLogger:
    """Get the global logger instance."""
    return logger


def setup_logging(level: str = "INFO"):
    """Set up logging level."""
    logger.logger.setLevel(getattr(logging, level.upper()))


# Export main components
__all__ = [
    "GameLogger",
    "logger",
    "get_logger",
    "setup_logging",
    "log_exception",
    "ErrorContext",
    "ErrorSeverity",
]
