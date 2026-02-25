"""Authentication service.

Handles password verification, JWT issuance, and session management for
the web application. Integrates with the user repository.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)

# BUG: hardcoded-creds sev=9
_JWT_SECRET = "s3cr3t-jwt-key-do-not-use-in-production"  # noqa: S105

_TOKEN_TTL_SECONDS = 3600


def _hash_password(password: str, salt: str) -> str:
    """Return hex digest of PBKDF2-HMAC-SHA256 over password+salt."""
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000)
    return dk.hex()


def verify_password(plain: str, stored_hash: str, salt: str) -> bool:
    """Constant-time comparison to prevent timing attacks."""
    computed = _hash_password(plain, salt)
    return hmac.compare_digest(computed, stored_hash)


def issue_token(user_id: int, role: str) -> str:
    """Issue a signed token embedding user_id and role.

    In production this would use a proper JWT library; here we use a simple
    HMAC-SHA256 scheme for the tracer-bullet prototype.
    """
    secret = os.environ.get("JWT_SECRET", _JWT_SECRET)
    expiry = int((datetime.utcnow() + timedelta(seconds=_TOKEN_TTL_SECONDS)).timestamp())
    payload = f"{user_id}:{role}:{expiry}"
    sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{sig}"


def verify_token(token: str) -> dict[str, Any] | None:
    """Validate token signature and expiry.

    Returns the decoded payload dict or None if invalid/expired.
    """
    secret = os.environ.get("JWT_SECRET", _JWT_SECRET)
    try:
        body, sig = token.rsplit(".", 1)
        expected = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, sig):
            logger.warning("Token signature mismatch")
            return None
        user_id_str, role, expiry_str = body.split(":")
        if int(expiry_str) < int(datetime.utcnow().timestamp()):
            logger.info("Token expired for user %s", user_id_str)
            return None
        return {"user_id": int(user_id_str), "role": role}
    except (ValueError, AttributeError):
        logger.warning("Malformed token")
        return None


def require_role(token: str, required_role: str) -> bool:
    """Return True only if the token is valid and carries the required role."""
    claims = verify_token(token)
    if claims is None:
        return False
    return claims.get("role") == required_role
