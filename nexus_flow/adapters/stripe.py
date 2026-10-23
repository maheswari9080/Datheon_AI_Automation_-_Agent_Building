"""Stripe payment integration adapter with HMAC-SHA256 signature verification and idempotency."""

import hashlib
import hmac
import time
from typing import Any, Dict, Optional, Set
from nexus_flow.adapters.base import BaseAdapter
from nexus_flow.core.logging import logger

class StripeAdapter(BaseAdapter):
    """Handles Stripe webhook event ingestion, signature verification, and event deduplication."""

    def __init__(self):
        super().__init__(service_name="Stripe")
        self.processed_event_ids: Set[str] = set()

    def health_check(self) -> Dict[str, Any]:
        return {
            "status": "ready",
            "live": self.is_live_mode,
            "secret_configured": bool(self.settings.stripe_webhook_secret),
        }

    def verify_webhook_signature(
        self,
        payload_bytes: bytes,
        signature_header: str,
        tolerance_seconds: int = 300,
    ) -> bool:
        """
        Validates official Stripe-Signature header: t={timestamp},v1={hex_signature}.
        Verifies timestamp freshness within tolerance and compares HMAC-SHA256.
        """
        if not payload_bytes or not signature_header:
            logger.warning("Stripe verification failed: Missing payload or signature header")
            return False

        secret = self.settings.stripe_webhook_secret
        if not secret:
            logger.error("Stripe verification failed: Missing webhook secret")
            return False

        timestamp = None
        signatures = []

        for item in signature_header.split(","):
            parts = item.strip().split("=")
            if len(parts) == 2:
                scheme, val = parts[0], parts[1]
                if scheme == "t":
                    timestamp = val
                elif scheme == "v1":
                    signatures.append(val)

        if not timestamp or not signatures:
            logger.warning("Stripe verification failed: Invalid header format")
            return False

        # Tolerance check
        try:
            event_timestamp = int(timestamp)
            current_time = int(time.time())
            if abs(current_time - event_timestamp) > tolerance_seconds:
                logger.warning(f"Stripe verification failed: Timestamp outside tolerance ({tolerance_seconds}s)")
                return False
        except ValueError:
            return False

        # Compute expected HMAC
        signed_payload = f"{timestamp}.".encode("utf-8") + payload_bytes
        expected_sig = hmac.new(
            secret.encode("utf-8"), signed_payload, hashlib.sha256
        ).hexdigest()

        for sig in signatures:
            if hmac.compare_digest(expected_sig, sig):
                return True

        logger.warning("Stripe verification failed: Signature mismatch")
        return False

    def is_event_processed(self, event_id: str) -> bool:
        """Checks if an event ID has already been recorded to prevent replay attacks."""
        return event_id in self.processed_event_ids

    def record_processed_event(self, event_id: str) -> None:
        """Records event ID in the idempotent memory registry."""
        self.processed_event_ids.add(event_id)

    def generate_test_signature(self, payload_bytes: bytes, timestamp: Optional[int] = None) -> str:
        """Generates a valid test Stripe-Signature header for testing & simulation."""
        ts = timestamp or int(time.time())
        secret = self.settings.stripe_webhook_secret
        signed_payload = f"{ts}.".encode("utf-8") + payload_bytes
        sig = hmac.new(
            secret.encode("utf-8"), signed_payload, hashlib.sha256
        ).hexdigest()
        return f"t={ts},v1={sig}"
