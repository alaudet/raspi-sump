"""Admin authentication helpers."""

import time
from functools import wraps
from threading import Lock


# H-2: rate limit failed admin logins to slow down online password guessing.
# In-memory only — cleared on rsumpweb restart, which is acceptable for a
# single-process LAN appliance. Keyed by client IP (nginx X-Real-IP).
_MAX_FAILED_ATTEMPTS = 15
_WINDOW_SECONDS = 15 * 60
_FAILED_ATTEMPTS: dict = {}
_LOCK = Lock()


def client_ip(request) -> str:
    """Return the caller's IP from nginx's X-Real-IP, falling back to remote_addr."""
    return request.headers.get("X-Real-IP") or request.remote_addr or "unknown"


def _prune(ip: str, now: float) -> list:
    """Drop stale timestamps outside the sliding window. Returns the pruned list."""
    cutoff = now - _WINDOW_SECONDS
    attempts = [t for t in _FAILED_ATTEMPTS.get(ip, []) if t > cutoff]
    if attempts:
        _FAILED_ATTEMPTS[ip] = attempts
    else:
        _FAILED_ATTEMPTS.pop(ip, None)
    return attempts


def is_rate_limited(ip: str) -> bool:
    """Return True if ip has reached the failed-attempt threshold in the window."""
    with _LOCK:
        return len(_prune(ip, time.monotonic())) >= _MAX_FAILED_ATTEMPTS


def record_failed_attempt(ip: str) -> None:
    """Record a failed login. Logs a forensics event the moment the threshold is hit."""
    with _LOCK:
        now = time.monotonic()
        attempts = _prune(ip, now)
        attempts.append(now)
        _FAILED_ATTEMPTS[ip] = attempts
        if len(attempts) == _MAX_FAILED_ATTEMPTS:
            from raspisump import log
            log.log_event(
                "error_log",
                f"Rate limit triggered for {ip} after "
                f"{_MAX_FAILED_ATTEMPTS} failed login attempts.",
            )


def clear_failed_attempts(ip: str) -> None:
    """Clear the failed-attempt counter for ip (called after a successful login)."""
    with _LOCK:
        _FAILED_ATTEMPTS.pop(ip, None)


def get_admin_password():
    """Return the admin password from credentials.conf.

    Uses a fallback of 'admin' if the [web] section is missing
    (e.g. on an install that hasn't been upgraded yet).
    """
    from raspisump.config_values import config
    return config.get("web", "admin_password", fallback="admin")


def hash_password(plaintext: str) -> str:
    """Return an argon2 hash of plaintext."""
    from argon2 import PasswordHasher
    return PasswordHasher().hash(plaintext)


def _is_hashed(stored: str) -> bool:
    return stored.startswith("$argon2")


def _write_hashed_password(hashed: str) -> None:
    """Write hashed password back to credentials.conf. Best-effort — ignores I/O errors."""
    try:
        from raspisump.web.credentials_helpers import write_credentials
        write_credentials({("web", "admin_password"): hashed})
    except OSError:
        pass


def check_password(candidate: str) -> bool:
    """Return True if candidate matches the configured admin password.

    Transparently migrates a plaintext password to argon2 on first successful login.
    Rehashes automatically if argon2 parameters have been upgraded.
    """
    from argon2 import PasswordHasher
    from argon2.exceptions import VerificationError, VerifyMismatchError

    stored = get_admin_password()
    ph = PasswordHasher()

    if _is_hashed(stored):
        try:
            ph.verify(stored, candidate)
            if ph.check_needs_rehash(stored):
                _write_hashed_password(hash_password(candidate))
            return True
        except (VerifyMismatchError, VerificationError):
            return False
        except Exception as e:
            from raspisump import log
            log.log_event(
                "error_log",
                f"Admin password verification error: {type(e).__name__}: {e}. "
                "Possible corrupted hash in credentials.conf. Reset "
                "web.admin_password to 'admin' to re-trigger the setup wizard.",
            )
            return False
    else:
        # Plaintext — migrate transparently on first successful login
        if candidate == stored:
            _write_hashed_password(hash_password(candidate))
            return True
        return False


def login_required(f):
    """Decorator: redirect to login page if admin session is not set."""
    @wraps(f)
    def decorated(*args, **kwargs):
        from flask import redirect, request, session, url_for
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin.login_get", next=request.path))
        return f(*args, **kwargs)
    return decorated
