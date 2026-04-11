# Copyright (c) 2025 Alogram Inc.
# Example: Custom Idempotency & Tracing
#
# This example shows how to use your internal identifiers (like Order IDs)
# as idempotency keys. This ensures that even if you retry the risk check
# across multiple service restarts, Alogram will treat it as the same assessment.

import uuid

from alogram_payrisk import AlogramRiskClient, CheckRequest

client = AlogramRiskClient(base_url="https://api.alogram.ai", api_key="sk_test_...")


def handle_checkout(order_id, user_id, amount):
    """
    Handles a user checkout.
    We use the order_id as the idempotency key for safety.
    """

    # 1. Build the request
    request = CheckRequest.from_dict(
        {
            "eventType": "purchase",
            "entities": {
                "tenantId": "tid_default",
                "clientId": "web_app",
                "endCustomerId": user_id,
            },
            "purchase": {
                "amount": amount,
                "currency": "USD",
                "transactionId": order_id,
            },
        }
    )

    # 2. Call check_risk with the custom key
    # If this call fails and you retry it with the SAME order_id,
    # Alogram will return the cached result instead of re-evaluating.
    try:
        decision = client.check_risk(
            request,
            idempotency_key=f"order_{order_id}",
            trace_id=f"req_{uuid.uuid4().hex[:8]}",
        )

        print(f"Order {order_id} | Decision: {decision.decision} | ID: {decision.assessment_id}")

    except Exception as e:
        print(f"Risk check failed for {order_id}: {e}")


if __name__ == "__main__":
    handle_checkout("ord_12345", "user_99", 150.00)
