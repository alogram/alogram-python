# Copyright (c) 2025 Alogram Inc.
# Basic usage example for the Alogram Payrisk SDK

from alogram_payrisk import AlogramRiskClient
from alogram_payrisk._generated.payrisk_v1 import (
    CheckRequest,
    EntityIds,
    Purchase,
    PaymentMethod,
    Card,
)


def main():
    # 1. Initialize the Smart Client
    # In production, use your API Key or let it auto-detect OIDC for GCP services
    client = AlogramRiskClient(
        base_url="https://api.alogram.ai", api_key="your-api-key-here"
    )

    # 2. Build a Risk Check Request
    request = CheckRequest(
        entities=EntityIds(
            tenant_id="tid_demo", client_id="cid_demo", end_customer_id="ecid_12345"
        ),
        event_type="purchase",
        purchase=Purchase(
            transaction_id="tx_987654321",
            amount=99.99,
            currency="USD",
            payment_method=PaymentMethod(
                Card(
                    type="card", card_network="visa", bin="411111", issuer_country="US"
                )
            ),
        ),
    )

    # 3. Perform the check
    print("🧪 Sending risk check...")
    decision = client.check_risk(request)

    # 4. Process the professionalized risk taxonomy
    print(f"✅ Decision: {decision.decision}")
    print(f"📊 Risk Score: {decision.risk_score}")

    for reason in decision.reasons:
        print(f"🔍 Reason [{reason.category}]: {reason.display_name}")
        print(f"💡 Action: {reason.recommended_action}")


if __name__ == "__main__":
    main()
