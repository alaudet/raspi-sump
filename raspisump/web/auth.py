"""Admin authentication helpers."""

from functools import wraps


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
        except Exception:
            return False  # malformed hash or other unexpected error
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
