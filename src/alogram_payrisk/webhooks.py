# Copyright (c) 2025 Alogram Inc.
# All rights reserved.

import hmac
import hashlib
from .exceptions import ValidationError


class WebhookVerifier:
    """
    Utility to verify the authenticity of webhooks sent by Alogram.

    Alogram signs webhook requests using a shared secret. The signature
    is sent in the 'x-alogram-signature' header.
    """

    @staticmethod
    def verify(payload: bytes, header_signature: str, secret: str) -> bool:
        """
        Verifies the HMAC-SHA256 signature of a webhook payload.

        Args:
            payload: The raw bytes of the request body.
            header_signature: The value of the 'x-alogram-signature' header.
            secret: Your Alogram Webhook Secret.

        Returns:
            bool: True if the signature is valid.

        Raises:
            ValidationError: If the signature is invalid or malformed.
        """
        if not header_signature or not secret:
            raise ValidationError("Missing signature or secret")

        expected_signature = hmac.new(
            secret.encode("utf-8"), payload, hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(expected_signature, header_signature):
            raise ValidationError("Invalid webhook signature")

        return True
