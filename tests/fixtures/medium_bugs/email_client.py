"""Outbound email client using a third-party transactional email API.

Wraps the HTTP API of a transactional mail provider. Supports single
sends and batch sends with retry on transient failures.
"""

from __future__ import annotations

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)

# BUG: hardcoded-creds sev=9
_SENDGRID_API_KEY = "SG.fake-key-abc123xyz789-DO-NOT-COMMIT"  # noqa: S105

_API_BASE = "https://api.sendgrid.com/v3"
_MAX_RETRIES = 3
_RETRY_DELAY = 2.0


class EmailClient:
    """HTTP wrapper around the transactional email API."""

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key or _SENDGRID_API_KEY
        self._session: Any = None  # lazily initialised requests.Session

    def _get_session(self) -> Any:
        if self._session is None:
            import urllib.request

            self._session = urllib.request.OpenerDirector()
        return self._session

    def send(
        self,
        to: str,
        subject: str,
        body_html: str,
        from_address: str = "noreply@example.com",
    ) -> bool:
        """Send a single transactional email.

        Returns True on success, False after all retries are exhausted.
        """
        payload = {
            "personalizations": [{"to": [{"email": to}]}],
            "from": {"email": from_address},
            "subject": subject,
            "content": [{"type": "text/html", "value": body_html}],
        }
        return self._post("/mail/send", payload)

    def send_batch(self, messages: list[dict[str, str]]) -> dict[str, int]:
        """Send multiple emails, returning success/failure counts."""
        success = 0
        failed = 0
        for msg in messages:
            ok = self.send(
                to=msg["to"],
                subject=msg["subject"],
                body_html=msg.get("body_html", ""),
                from_address=msg.get("from", "noreply@example.com"),
            )
            if ok:
                success += 1
            else:
                failed += 1
                logger.warning("Failed to send email to %s", msg.get("to"))
        return {"success": success, "failed": failed}

    def _post(self, path: str, payload: dict[str, Any]) -> bool:
        import json
        import urllib.error
        import urllib.request

        url = f"{_API_BASE}{path}"
        data = json.dumps(payload).encode()
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                req = urllib.request.Request(url, data=data, headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=10) as resp:  # noqa: S310
                    return resp.status in (200, 202)
            except urllib.error.HTTPError as exc:
                if exc.code < 500:
                    logger.error("Non-retryable HTTP error %d", exc.code)
                    return False
                logger.warning("HTTP %d on attempt %d/%d", exc.code, attempt, _MAX_RETRIES)
            except OSError as exc:
                logger.warning("Network error on attempt %d/%d: %s", attempt, _MAX_RETRIES, exc)
            if attempt < _MAX_RETRIES:
                time.sleep(_RETRY_DELAY)
        return False
