# Copyright (c) 2025 Alogram Inc.
# Example: Production Error Handling
#
# This example demonstrates how to catch specific exceptions from the SDK
# to implement logic like "Fail Open" or customized user messaging.

import logging
from alogram_payrisk import (
    AlogramRiskClient,
    ValidationError,
    AuthenticationError,
    RateLimitError,
    InternalServerError,
    CheckRequest,
)

# In production, use structured logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger("alogram.payrisk.handler")

client = AlogramRiskClient(base_url="https://api.alogram.ai", api_key="sk_test_...")


def process_payment_with_risk_check(request_dict):
    """
    Checks risk before processing a payment.
    Implements a 'Fail Open' strategy for non-auth errors.
    """
    try:
        req = CheckRequest.from_dict(request_dict)
        decision = client.check_risk(req)

        if decision.decision == "decline":
            logger.warning(f"🛑 Declined: {decision.reasons}")
            return {"status": "rejected", "reason": "High risk detected"}

        return {"status": "approved", "risk_score": decision.risk_score}

    except AuthenticationError as e:
        # Critical: Your API key is likely expired or invalid.
        # Stop processing and alert your ops team.
        logger.critical(f"🚨 AUTHENTICATION FAILED: {e}. Check your API Key.")
        raise

    except ValidationError as e:
        # Data error: Your request body doesn't match the schema.
        # This usually indicates a bug in your integration code.
        logger.error(f"❌ INVALID REQUEST: {e}")
        # In a real app, you might want to investigate the body: print(e.body)
        return {"status": "error", "message": "Internal request malformed"}

    except (RateLimitError, InternalServerError) as e:
        # Transient errors: These are automatically retried by the SDK.
        # If they still reach here, the system is exhausted.
        # STRATEGY: 'Fail Open' - log the error but allow the payment to proceed
        # to avoid blocking revenue, then review the transaction later.
        logger.error(
            f"⚠️ SYSTEM DEGRADED ({e.status}): Allowing transaction via Fail-Open."
        )
        return {"status": "approved", "note": "manual_review_required"}

    except Exception as e:
        logger.error(f"🔥 UNEXPECTED ERROR: {type(e).__name__}: {e}")
        return {"status": "error", "message": "Unexpected error"}


if __name__ == "__main__":
    # Test with a missing required field to trigger ValidationError
    bad_request = {
        "eventType": "purchase"
        # entities is missing!
    }
    result = process_payment_with_risk_check(bad_request)
    print(f"Result: {result}")
