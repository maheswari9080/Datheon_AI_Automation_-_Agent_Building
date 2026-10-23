"""Security utilities: Prompt injection defense, input sanitization, HMAC validation."""

import hashlib
import hmac
import re
from typing import Tuple

# Common prompt injection pattern signatures
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"disregard\s+(all\s+)?(previous|prior)\s+instructions",
    r"you\s+are\s+now\s+(a|an|in|the)\s+mode",
    r"system\s*:\s*you\s+are",
    r"system\s+override",
    r"reveal\s+(your|the)\s+(api\s+key|system\s+prompt|secret)",
    r"output\s+all\s+passwords",
    r"drop\s+table",
    r"<script.*?>.*?</script>",
    r"bypass\s+safety\s+filters",
    r"print\s+your\s+rules",
]

COMPILED_INJECTION_REGEX = re.compile(
    "|".join(f"({p})" for p in INJECTION_PATTERNS), re.IGNORECASE
)

def sanitize_untrusted_text(text: str, max_length: int = 10000) -> Tuple[str, bool]:
    """
    Sanitizes untrusted input (emails, webhook payloads, freeform fields).
    Returns (cleaned_text, was_injection_detected).
    """
    if not text:
        return "", False

    # Enforce strict length boundary
    cleaned = text[:max_length].strip()

    # Detect prompt injection vectors
    injection_detected = bool(COMPILED_INJECTION_REGEX.search(cleaned))

    # Strip dangerous control characters (except standard newlines and tabs)
    cleaned = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", cleaned)

    return cleaned, injection_detected

def sanitize_csv_cell(value: str) -> str:
    """
    Sanitizes string against OWASP formula injection (CSV/Spreadsheet injection).
    Prepends a single quote if the string begins with =, +, -, @, or tab/return.
    """
    if not value:
        return ""
    str_val = str(value).strip()
    if str_val and str_val[0] in ("=", "+", "-", "@", "\t", "\r"):
        return f"'{str_val}"
    return str_val

def verify_hmac_sha256(payload: bytes, secret: str, signature_header: str) -> bool:
    """
    Verifies HMAC-SHA256 signatures (e.g. Stripe, Slack, custom webhook signatures).
    Uses hmac.compare_digest for constant-time comparison.
    """
    if not payload or not secret or not signature_header:
        return False

    # Extract signature if formatted as t=...,v1=... (Stripe format)
    target_sig = signature_header
    timestamp = None
    if "v1=" in signature_header:
        parts = signature_header.split(",")
        for part in parts:
            if part.strip().startswith("t="):
                timestamp = part.strip()[2:]
            elif part.strip().startswith("v1="):
                target_sig = part.strip()[3:]

        if timestamp:
            signed_payload = f"{timestamp}.".encode("utf-8") + payload
        else:
            signed_payload = payload
    else:
        signed_payload = payload

    expected_sig = hmac.new(
        secret.encode("utf-8"), signed_payload, hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_sig, target_sig)

def compute_content_hash(content: str) -> str:
    """Generates a deterministic SHA-256 fingerprint for idempotency & deduplication."""
    return hashlib.sha256(content.strip().lower().encode("utf-8")).hexdigest()
