"""Email address validation utilities.

Provides syntactic validation of email addresses using RFC 5321-style
rules. Does not perform DNS MX lookups (network-free, fast).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_LOCAL_PART_RE = re.compile(r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+$")
_DOMAIN_LABEL_RE = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$")

_MAX_EMAIL_LENGTH = 254
_MAX_LOCAL_LENGTH = 64
_MAX_DOMAIN_LENGTH = 253


@dataclass
class ValidationResult:
    valid: bool
    reason: str = ""

    def __bool__(self) -> bool:
        return self.valid


def validate_email(address: str) -> ValidationResult:
    """Return a ValidationResult for the given email address string."""
    if not address or not isinstance(address, str):
        return ValidationResult(False, "empty or non-string input")

    address = address.strip()

    if len(address) > _MAX_EMAIL_LENGTH:
        return ValidationResult(
            False, f"address too long ({len(address)} > {_MAX_EMAIL_LENGTH})"
        )

    if address.count("@") != 1:
        return ValidationResult(False, "must contain exactly one '@'")

    local, domain = address.split("@", 1)

    if not local:
        return ValidationResult(False, "local part is empty")
    if len(local) > _MAX_LOCAL_LENGTH:
        return ValidationResult(
            False, f"local part too long ({len(local)} > {_MAX_LOCAL_LENGTH})"
        )
    if not _LOCAL_PART_RE.match(local):
        return ValidationResult(False, f"invalid characters in local part: {local!r}")

    if not domain:
        return ValidationResult(False, "domain is empty")
    if len(domain) > _MAX_DOMAIN_LENGTH:
        return ValidationResult(
            False, f"domain too long ({len(domain)} > {_MAX_DOMAIN_LENGTH})"
        )

    labels = domain.split(".")
    if len(labels) < 2:
        return ValidationResult(False, "domain must have at least two labels")
    for label in labels:
        if not label:
            return ValidationResult(False, "domain contains empty label (double dot or trailing dot)")
        if not _DOMAIN_LABEL_RE.match(label):
            return ValidationResult(False, f"invalid domain label: {label!r}")

    tld = labels[-1]
    if not tld.isalpha():
        return ValidationResult(False, f"TLD must be alphabetic, got {tld!r}")

    return ValidationResult(True)


def normalize(address: str) -> str:
    """Return a lowercased, stripped email address."""
    return address.strip().lower()


def is_valid(address: str) -> bool:
    """Convenience wrapper — returns True if address passes validation."""
    return bool(validate_email(address))
