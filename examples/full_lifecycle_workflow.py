# Copyright (c) 2025 Alogram Inc.
#
# Example: Full Lifecycle Workflow
#
# This example demonstrates the complete "Day in the Life" of a transaction:
# 1. Pre-Order: Client-side behavioral signals (linked by Session/Device ID)
# 2. At-Order: Server-side risk check (correlating the signals)
# 3. Post-Order: Payment lifecycle events (linked by Payment Intent ID)
# 4. Feedback: Ingesting a fraud label (Chargeback)

from datetime import datetime, timezone
from alogram_payrisk import (
    AlogramRiskClient,
    AlogramPublicClient,
    CheckRequest,
    EntityIds,
    Purchase,
    PaymentMethod,
    Card,
    SignalsRequest,
    SignalsInteractionVariant,
    Interaction,
    PaymentEvent,
    PaymentOutcome,
    PaymentAuthorizationOutcome,
)

# Configuration
BASE_URL = "https://api.alogram.ai"
PUBLISHABLE_KEY = "pk_test_frontend_key"
SECRET_KEY = "sk_test_backend_key"
TENANT_ID = "tid_demo_store"


def main():
    # --- STEP 0: Establish Anchors ---
    # These are generated on the frontend and persisted during the session.
    session_id = "sid_browser_session_99"
    device_id = "did_persistent_device_44"
    end_customer_id = "ecid_shopper_123"

    print(f"🚀 Starting workflow for Session: {session_id}\n")

    # --- STEP 1: Client-Side Signals (AlogramPublicClient) ---
    # Simulation: User is browsing the site before checking out.
    public_client = AlogramPublicClient(base_url=BASE_URL, api_key=PUBLISHABLE_KEY, tenant_id=TENANT_ID)

    print("📡 [Client] Ingesting browsing signals...")
    public_client.ingest_signals(
        SignalsRequest(
            actual_instance=SignalsInteractionVariant(
                signal_type="interaction",
                entities=EntityIds(session_id=session_id, device_id=device_id, end_customer_id=end_customer_id),
                interactions=[
                    Interaction(
                        interaction_type="page_view",
                        location_id="loc_product_page_abc",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                    )
                ],
            )
        )
    )

    # --- STEP 2: The Risk Check (AlogramRiskClient) ---
    # Simulation: User clicks "Place Order". Backend evaluates the risk.
    risk_client = AlogramRiskClient(base_url=BASE_URL, api_key=SECRET_KEY, tenant_id=TENANT_ID)

    print("📥 [Server] Performing risk check (correlating anchors)...")
    check_req = CheckRequest(
        entities=EntityIds(
            session_id=session_id,  # <--- Link to pre-order signals
            device_id=device_id,  # <--- Link to pre-order signals
            end_customer_id=end_customer_id,
        ),
        event_type="purchase",
        purchase=Purchase(
            transaction_id="tx_internal_555",
            amount=150.00,
            currency="USD",
            payment_method=PaymentMethod(Card(type="card", bin="411111", card_network="visa")),
        ),
    )

    decision = risk_client.check_risk(check_req)

    # 🔑 CRITICAL: Capture the server-minted ID
    pi_id = decision.payment_intent_id
    print(f"✅ Decision: {decision.decision} | Score: {decision.decision_score}")
    print(f"🆔 Generated PaymentIntent: {pi_id}\n")

    # --- STEP 3: Payment Lifecycle (AlogramRiskClient) ---
    # Simulation: The payment processor approved the transaction.
    # We link this back using the payment_intent_id.
    print(f"📡 [Server] Ingesting Authorization success for {pi_id}...")
    risk_client.ingest_event(
        PaymentEvent(
            payment_intent_id=pi_id,
            event_type="authorization",
            timestamp=datetime.now(timezone.utc).isoformat(),
            outcome=PaymentOutcome(authorization=PaymentAuthorizationOutcome(approved=True, responseCode="00")),
        )
    )

    # --- STEP 4: Fraud Labeling (AlogramRiskClient) ---
    # Simulation: Weeks later, a chargeback is received.
    # This acts as the "Ground Truth" label for ML retraining.
    print(f"🚨 [Server] Ingesting Fraud Label (Chargeback) for {pi_id}...")
    risk_client.ingest_event(
        PaymentEvent(
            payment_intent_id=pi_id,
            event_type="chargeback",
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata='{"reason": "fraudulent_transaction", "source": "bank_notice"}',
        )
    )

    print("\n✨ Workflow Complete. The engine has correlated browsing, scoring, and the final fraud label.")


if __name__ == "__main__":
    main()
