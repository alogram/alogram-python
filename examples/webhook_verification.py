# Copyright (c) 2025 Alogram Inc.
# Example: Webhook Verification
#
# Secure your webhook endpoints by verifying that the request
# actually came from Alogram.

import hashlib
import hmac

from alogram_payrisk import ValidationError, WebhookVerifier

# Your shared secret from the Alogram Dashboard
WEBHOOK_SECRET = "whsec_your_secret_here"


def handle_alogram_webhook(raw_payload, signature_header):
    """
    Example handler for an Alogram Webhook.
    """
    try:
        # Verify the signature before processing
        WebhookVerifier.verify(
            payload=raw_payload,
            header_signature=signature_header,
            secret=WEBHOOK_SECRET,
        )

        print("✅ Webhook verified!")
        # Process the event...

    except ValidationError as e:
        print(f"🛑 Security Alert: {e}")
        # Return 401 to the sender
        return False


if __name__ == "__main__":
    # Simulated data
    mock_payload = b'{"type": "chargeback.updated", "id": "evt_123"}'

    # In a real app, you get this from request.headers['x-alogram-signature']

    mock_sig = hmac.new(
        WEBHOOK_SECRET.encode("utf-8"), mock_payload, hashlib.sha256
    ).hexdigest()

    handle_alogram_webhook(mock_payload, mock_sig)
