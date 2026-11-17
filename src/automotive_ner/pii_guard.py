"""Lightweight redaction for common email and phone patterns."""

import re

_EMAIL = re.compile(r"(?<![\w.+-])[\w.+-]+@[\w-]+(?:\.[\w-]+)+(?![\w.-])")
_PHONE = re.compile(
    r"(?<!\w)(?:\+?1[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}(?!\w)"
)


def redact_pii(text: str) -> str:
    """Redact common email addresses and North American phone numbers."""
    redacted = _EMAIL.sub("[REDACTED]", text)
    return _PHONE.sub("[REDACTED]", redacted)
