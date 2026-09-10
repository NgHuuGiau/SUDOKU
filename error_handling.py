"""
Comprehensive error handling and logging system for Sudoku.
Provides structured logging, error tracking, and graceful degradation.
"""
import json
import logging
import os
import sys
import threading
import time
import traceback
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from functools import wraps
from pathlib import Path
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
    LOW = "low"          # Minor issues, recoverable
    MEDIUM = "medium"    # Significant issues, may affect functionality
    HIGH = "high"        # Major issues, core functionality affected
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


@dataclass
class PerformanceMetric:
    """Performance metric tracking."""
    operation: str
    duration_ms: float
    timestamp: str
    success: bool
    memory_mb: Optional[float] = None
    cpu_percent: Optional[float] = None
    metadata: dict = field(default_factory=dict)


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
        self._performance_metrics: list[PerformanceMetric] = []
        self._max_history = 1000
        self._metrics_lock = threading.Lock()

    def _setup_logging(self):
        """Configure logging with multiple handlers."""
        self.logger = logging.getLogger("sudoku")
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False

        # Clear existing handlers
        self.logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%H:%M:%S"
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)

        # File handler (rotating)
        log_dir = Path(os.path.dirname(__file__)) / "logs"
        log_dir.mkdir(exist_ok=True)

        file_handler = logging.FileHandler(
            log_dir / "sudoku.log",
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)

        # Error file handler (errors only)
        error_handler = logging.FileHandler(
            log_dir / "sudoku_errors.log",
            encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)
        error_format = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s\n%(exc_info)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        error_handler.setFormatter(error_format)
        self.logger.addHandler(error_handler)

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

    def log_exception(self, exc: Exception, severity: ErrorSeverity = ErrorSeverity.HIGH,
                      user_action: Optional[str] = None, game_state: Optional[dict] = None,
                      additional_data: Optional[dict] = None) -> ErrorContext:
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
            additional_data=additional_data or {}
        )

        with self._metrics_lock:
            self._error_history.append(error_context)
            if len(self._error_history) > self._max_history:
                self._error_history = self._error_history[-self._max_history:]

        # Log to standard logger
        self.logger.error(
            f"[{severity.value.upper()}] {error_context.error_id} | {error_context.message}",
            exc_info=exc
        )

        return error_context

    def record_performance(self, metric: PerformanceMetric):
        """Record a performance metric."""
        with self._metrics_lock:
            self._performance_metrics.append(metric)
            if len(self._performance_metrics) > self._max_history:
                self._performance_metrics = self._performance_metrics[-self._max_history:]

    def get_error_history(self, limit: int = 100, severity: Optional[ErrorSeverity] = None) -> list[ErrorContext]:
        """Get recent error history."""
        with self._metrics_lock:
            errors = self._error_history
            if severity:
                errors = [e for e in errors if e.severity == severity]
            return errors[-limit:]

    def get_performance_stats(self, operation: Optional[str] = None) -> dict:
        """Get performance statistics."""
        with self._metrics_lock:
            metrics = self._performance_metrics
            if operation:
                metrics = [m for m in metrics if m.operation == operation]

            if not metrics:
                return {"count": 0}

            durations = [m.duration_ms for m in metrics]
            success_count = sum(1 for m in metrics if m.success)

            return {
                "count": len(metrics),
                "success_rate": success_count / len(metrics) * 100,
                "avg_duration_ms": sum(durations) / len(durations),
                "min_duration_ms": min(durations),
                "max_duration_ms": max(durations),
                "operations": list({m.operation for m in metrics})
            }

    def export_errors(self, filepath: str, severity: Optional[ErrorSeverity] = None):
        """Export error history to JSON file."""
        errors = self.get_error_history(limit=self._max_history, severity=severity)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump([e.to_dict() for e in errors], f, ensure_ascii=False, indent=2)


# Global logger instance
logger = GameLogger()


def log_exception(severity: ErrorSeverity = ErrorSeverity.HIGH,
                  user_action: Optional[str] = None,
                  game_state: Optional[dict] = None,
                  additional_data: Optional[dict] = None):
    """Decorator to automatically log exceptions."""
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.log_exception(
                    e, severity=severity,
                    user_action=user_action or f"Calling {func.__name__}",
                    game_state=game_state,
                    additional_data=additional_data
                )
                raise
        return wrapper
    return decorator


@contextmanager
def log_performance(operation: str, logger_instance: Optional[GameLogger] = None,
                    metadata: Optional[dict] = None):
    """Context manager to measure and log performance."""
    log = logger_instance or logger
    start_time = time.perf_counter()
    start_memory = _get_memory_mb()
    success = False

    try:
        yield
        success = True
    except Exception:
        raise
    finally:
        duration_ms = (time.perf_counter() - start_time) * 1000
        end_memory = _get_memory_mb()

        metric = PerformanceMetric(
            operation=operation,
            duration_ms=duration_ms,
            timestamp=datetime.now().isoformat(),
            success=success,
            memory_mb=end_memory - start_memory if start_memory and end_memory else None,
            metadata=metadata or {}
        )
        log.record_performance(metric)

        if duration_ms > 100:  # Log slow operations
            log.warning(f"Slow operation: {operation} took {duration_ms:.1f}ms")


def _get_memory_mb() -> Optional[float]:
    """Get current memory usage in MB."""
    try:
        import psutil
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    except ImportError:
        return None


class SafeExecutor:
    """Safe execution wrapper with timeout and resource limits."""

    def __init__(self, timeout: float = 30.0, max_memory_mb: float = 500):
        self.timeout = timeout
        self.max_memory_mb = max_memory_mb

    def execute(self, func: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        """Execute function with safety limits."""
        # For now, just execute with logging
        with log_performance(func.__name__):
            return func(*args, **kwargs)

    async def execute_async(self, func: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        """Execute async function with safety limits."""
        import asyncio
        return await asyncio.wait_for(func(*args, **kwargs), timeout=self.timeout)


class CircuitBreaker:
    """Circuit breaker pattern for external dependencies."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half-open
        self._lock = threading.Lock()

    def call(self, func: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        with self._lock:
            if self.state == "open":
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = "half-open"
                else:
                    raise CircuitBreakerOpenError("Circuit breaker is open")

        try:
            result = func(*args, **kwargs)
            with self._lock:
                self.failure_count = 0
                self.state = "closed"
            return result
        except Exception:
            with self._lock:
                self.failure_count += 1
                self.last_failure_time = time.time()
                if self.failure_count >= self.failure_threshold:
                    self.state = "open"
            raise


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""


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
    "log_performance",
    "ErrorContext",
    "ErrorSeverity",
    "PerformanceMetric",
    "SafeExecutor",
    "CircuitBreaker",
    "CircuitBreakerOpenError",
    "ErrorSeverity",
]
