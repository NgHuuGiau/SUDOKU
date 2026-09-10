"""
Security hardening module for Sudoku.
Provides input validation, sanitization, and security utilities.
"""
import hashlib
import hmac
import html
import json
import logging
import re
import secrets
import threading
import time
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

logger = logging.getLogger("sudoku.security")


class SecurityError(Exception):
    """Base security exception."""


class ValidationError(SecurityError):
    """Input validation error."""


class InjectionError(SecurityError):
    """Injection attempt detected."""


class PathTraversalError(SecurityError):
    """Path traversal attempt detected."""


class RateLimitError(SecurityError):
    """Rate limit exceeded."""


class InputValidator:
    """Comprehensive input validation."""

    # Regex patterns for validation
    SUDOKU_BOARD_PATTERN = re.compile(r'^[0-9]{81}$')
    SUDOKU_CELL_PATTERN = re.compile(r'^[0-9]$')
    FILENAME_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\.]+$')
    ALPHANUMERIC_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\s]+$')
    USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_\-]{3,20}$')

    # Dangerous patterns to detect
    SQL_INJECTION_PATTERNS = [
        re.compile(r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|CREATE)\b)', re.IGNORECASE),
        re.compile(r'(\b(OR|AND)\s+\d+\s*=\s*\d+)', re.IGNORECASE),
        re.compile(r'(--|;|\/\*|\*\/)', re.IGNORECASE),
    ]

    XSS_PATTERNS = [
        re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
        re.compile(r'javascript:', re.IGNORECASE),
        re.compile(r'on\w+\s*=', re.IGNORECASE),
        re.compile(r'<iframe', re.IGNORECASE),
    ]

    PATH_TRAVERSAL_PATTERNS = [
        re.compile(r'\.\./'),
        re.compile(r'\.\.\\'),
        re.compile(r'%2e%2e%2f', re.IGNORECASE),
        re.compile(r'%2e%2e%5c', re.IGNORECASE),
    ]

    @classmethod
    def validate_sudoku_board(cls, board_str: str) -> str:
        """Validate and sanitize Sudoku board string."""
        if not isinstance(board_str, str):
            raise ValidationError("Board must be a string")

        board_str = board_str.strip()

        if not cls.SUDOKU_BOARD_PATTERN.match(board_str):
            raise ValidationError("Invalid board format: must be 81 digits (0-9)")

        return board_str

    @classmethod
    def validate_cell_value(cls, value: Union[str, int]) -> int:
        """Validate a single cell value."""
        if isinstance(value, int):
            if 0 <= value <= 9:
                return value
            raise ValidationError(f"Cell value must be 0-9, got {value}")

        if isinstance(value, str):
            if cls.SUDOKU_CELL_PATTERN.match(value):
                return int(value)
            raise ValidationError(f"Invalid cell value: {value}")

        raise ValidationError(f"Cell value must be int or str, got {type(value)}")

    @classmethod
    def validate_filename(cls, filename: str) -> str:
        """Validate filename to prevent path traversal."""
        if not isinstance(filename, str):
            raise ValidationError("Filename must be a string")

        filename = filename.strip()

        if not filename:
            raise ValidationError("Filename cannot be empty")

        if not cls.FILENAME_PATTERN.match(filename):
            raise ValidationError("Filename contains invalid characters")

        # Check for path traversal
        for pattern in cls.PATH_TRAVERSAL_PATTERNS:
            if pattern.search(filename):
                raise PathTraversalError(f"Path traversal attempt detected: {filename}")

        return filename

    @classmethod
    def validate_username(cls, username: str) -> str:
        """Validate username."""
        if not isinstance(username, str):
            raise ValidationError("Username must be a string")

        username = username.strip()

        if not cls.USERNAME_PATTERN.match(username):
            raise ValidationError("Username must be 3-20 alphanumeric characters, underscore or hyphen")

        return username

    @classmethod
    def sanitize_html(cls, text: str) -> str:
        """Sanitize HTML to prevent XSS."""
        if not isinstance(text, str):
            return str(text)

        # HTML escape
        text = html.escape(text, quote=True)

        # Additional XSS pattern removal
        for pattern in cls.XSS_PATTERNS:
            text = pattern.sub('', text)

        return text

    @classmethod
    def sanitize_sql(cls, text: str) -> str:
        """Sanitize input to prevent SQL injection."""
        if not isinstance(text, str):
            return str(text)

        # Check for SQL injection patterns
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if pattern.search(text):
                logger.warning(f"Potential SQL injection attempt detected: {text[:100]}")
                raise InjectionError("Potential SQL injection detected")

        return text

    @classmethod
    def validate_json(cls, data: str, max_size: int = 1024 * 1024) -> dict:
        """Validate and parse JSON with size limit."""
        if not isinstance(data, str):
            raise ValidationError("JSON data must be a string")

        if len(data) > max_size:
            raise ValidationError(f"JSON data exceeds maximum size of {max_size} bytes")

        try:
            import json
            parsed = json.loads(data)
            if not isinstance(parsed, dict):
                raise ValidationError("JSON must be an object")
            return parsed
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON: {e}") from e


class SecureFileHandler:
    """Secure file operations with path validation."""

    def __init__(self, base_dir: Union[str, Path], allowed_extensions: Optional[List[str]] = None):
        self.base_dir = Path(base_dir).resolve()
        self.allowed_extensions = allowed_extensions or ['.json', '.txt', '.png', '.jpg', '.ico']

        # Ensure base directory exists
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _validate_path(self, path: Union[str, Path]) -> Path:
        """Validate and resolve path within base directory."""
        path = Path(path)

        # Resolve to absolute path
        try:
            resolved = path.resolve()
        except Exception as e:
            raise PathTraversalError(f"Invalid path: {path}") from e

        # Ensure path is within base directory
        try:
            resolved.relative_to(self.base_dir)
        except ValueError as e:
            raise PathTraversalError(f"Path traversal attempt: {path}") from e

        return resolved

    def read_file(self, filename: str, max_size: int = 10 * 1024 * 1024) -> bytes:
        """Safely read a file."""
        filepath = self._validate_path(self.base_dir / filename)

        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filename}")

        if not filepath.is_file():
            raise ValidationError(f"Not a file: {filename}")

        # Check extension
        if filepath.suffix.lower() not in [ext.lower() for ext in self.allowed_extensions]:
            raise ValidationError(f"File extension not allowed: {filepath.suffix}")

        # Check size
        size = filepath.stat().st_size
        if size > max_size:
            raise ValidationError(f"File too large: {size} bytes (max {max_size})")

        return filepath.read_bytes()

    def write_file(self, filename: str, content: Union[str, bytes], overwrite: bool = False) -> Path:
        """Safely write a file."""
        filepath = self._validate_path(self.base_dir / filename)

        if filepath.exists() and not overwrite:
            raise ValidationError(f"File already exists: {filename}")

        # Ensure parent directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(content, str):
            filepath.write_text(content, encoding='utf-8')
        else:
            filepath.write_bytes(content)

        return filepath

    def list_files(self, extension: Optional[str] = None) -> List[Path]:
        """List files in base directory."""
        files = []
        for f in self.base_dir.iterdir():
            if f.is_file():
                if extension is None or f.suffix.lower() == extension.lower():
                    files.append(f)
        return sorted(files)


class RateLimiter:
    """Rate limiter for API calls and user actions."""

    def __init__(self):
        self._requests: Dict[str, List[float]] = {}
        self._lock = threading.Lock()

    def check_rate_limit(self, key: str, max_requests: int, window_seconds: float) -> bool:
        """Check if request is within rate limit. Returns True if allowed."""
        now = time.time()
        window_start = now - window_seconds

        with self._lock:
            if key not in self._requests:
                self._requests[key] = []

            # Clean old requests
            self._requests[key] = [t for t in self._requests[key] if t > window_start]

            if len(self._requests[key]) >= max_requests:
                return False

            self._requests[key].append(now)
            return True

    def get_remaining(self, key: str, max_requests: int, window_seconds: float) -> int:
        """Get remaining requests in current window."""
        now = time.time()
        window_start = now - window_seconds

        with self._lock:
            if key not in self._requests:
                return max_requests

            recent = [t for t in self._requests[key] if t > window_start]
            return max(0, max_requests - len(recent))

    def reset(self, key: str):
        """Reset rate limit for key."""
        with self._lock:
            if key in self._requests:
                del self._requests[key]


class SecureConfig:
    """Secure configuration management with encryption."""

    def __init__(self, config_path: Union[str, Path], key: Optional[bytes] = None):
        self.config_path = Path(config_path)
        self.key = key or self._generate_key()
        self._config: Dict[str, Any] = {}
        self._load()

    def _generate_key(self) -> bytes:
        """Generate or load encryption key."""
        key_file = self.config_path.with_suffix('.key')
        if key_file.exists():
            return key_file.read_bytes()

        key = secrets.token_bytes(32)
        key_file.write_bytes(key)
        # Make key file readable only by owner
        try:
            key_file.chmod(0o600)
        except Exception:
            pass
        return key

    def _load(self):
        """Load and decrypt config."""
        if not self.config_path.exists():
            self._config = {}
            return

        try:
            encrypted = self.config_path.read_bytes()
            self._decrypt(encrypted)
            self._config = json.loads(encrypted)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            self._config = {}

    def _save(self):
        """Encrypt and save config."""
        try:
            encrypted = self._encrypt(json.dumps(self._config))
            # Write atomically
            temp_path = self.config_path.with_suffix('.tmp')
            temp_path.write_bytes(encrypted)
            temp_path.replace(self.config_path)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            raise

    def _encrypt(self, data: str) -> bytes:
        """Encrypt data using Fernet."""
        from cryptography.fernet import Fernet
        f = Fernet(self.key)
        return f.encrypt(data.encode())

    def _decrypt(self, data: bytes) -> str:
        """Decrypt data using Fernet."""
        from cryptography.fernet import Fernet
        f = Fernet(self.key)
        return f.decrypt(data).decode()

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

    def set(self, key: str, value: Any):
        self._config[key] = value
        self._save()

    def delete(self, key: str):
        if key in self._config:
            del self._config[key]
            self._save()


def generate_csrf_token() -> str:
    """Generate a secure CSRF token."""
    return secrets.token_urlsafe(32)


def verify_csrf_token(token: str, expected: str) -> bool:
    """Verify CSRF token using constant-time comparison."""
    return hmac.compare_digest(token, expected)


def hash_password(password: str, salt: Optional[bytes] = None) -> tuple[bytes, bytes]:
    """Hash password with salt using PBKDF2."""
    if salt is None:
        salt = secrets.token_bytes(16)

    # Use PBKDF2 with SHA-256, 100000 iterations
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return key, salt


def verify_password(password: str, hashed: bytes, salt: bytes) -> bool:
    """Verify password against hash."""
    key, _ = hash_password(password, salt)
    return hmac.compare_digest(key, hashed)


def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(length)


def constant_time_compare(a: str, b: str) -> bool:
    """Constant-time string comparison to prevent timing attacks."""
    return hmac.compare_digest(a, b)


# Rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(max_requests: int = 60, window_seconds: float = 60.0):
    """Decorator for rate limiting function calls."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use function name as key, or first arg if it's a user identifier
            key = f"{func.__module__}.{func.__name__}"
            if args and hasattr(args[0], 'user_id'):
                key = f"{key}:{args[0].user_id}"

            if not rate_limiter.check_rate_limit(key, max_requests, window_seconds):
                raise RateLimitError(f"Rate limit exceeded for {func.__name__}")

            return func(*args, **kwargs)
        return wrapper
    return decorator


# Global instances
secure_validator = InputValidator()
secure_file_handler = SecureFileHandler("data")
secure_config = SecureConfig("config.enc")
rate_limiter_instance = RateLimiter()

# Export main components
__all__ = [
    "SecurityError",
    "ValidationError",
    "InjectionError",
    "PathTraversalError",
    "RateLimitError",
    "InputValidator",
    "SecureFileHandler",
    "SecureConfig",
    "RateLimiter",
    "RateLimitError",
    "rate_limiter",
    "secure_validator",
    "secure_file_handler",
    "secure_config",
    "rate_limit",
    "generate_csrf_token",
    "verify_csrf_token",
    "hash_password",
    "verify_password",
    "generate_secure_token",
    "constant_time_compare",
]
