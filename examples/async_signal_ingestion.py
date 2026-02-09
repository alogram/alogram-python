# Copyright (c) 2025 Alogram Inc.
# Example: Async Signal Ingestion
#
# Behavioral signals are most effective when sent frequently, but they
# should never block your user's experience. This example shows how
# to use a ThreadPoolExecutor to ingest signals asynchronously.

import concurrent.futures
import logging

from alogram_payrisk import AlogramRiskClient, SignalsRequest

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("alogram.example")

# Initialize Client
client = AlogramRiskClient(base_url="https://api.alogram.ai", api_key="sk_test_...")

# Use a global executor for your application
executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)


def send_signal_background(tenant_id, client_id, user_id, interaction_type):
    """
    Constructs and sends a signal. This runs in a background thread.
    """
    # Note: For production, we'd use the actual model classes.
    # Here we show the dynamic dictionary path which the client also supports.
    request_data = {
        "signalType": "interaction",
        "entities": {
            "tenantId": tenant_id,
            "clientId": client_id,
            "endCustomerId": user_id,
        },
        "interactions": [
            {
                "interactionType": interaction_type,
                "timestamp": "2023-10-01T12:00:00Z",  # Replace with dynamic
                "locationId": "loc_web_front",
            }
        ],
    }

    try:
        # We use from_dict to validate the schema before sending
        req = SignalsRequest.from_dict(request_data)
        client.ingest_signals(req)
        logger.info(f"✅ Signal {interaction_type} ingested for {user_id}")
    except Exception as e:
        logger.error(f"❌ Failed to ingest signal: {e}")


def handle_user_action(user_id):
    """
    Simulated web handler that triggers a background signal.
    """
    logger.info(f"👤 User {user_id} performed an action.")

    # Fire and forget
    executor.submit(send_signal_background, "tid_123", "cid_web", user_id, "page_view")

    return {"status": "ok"}


if __name__ == "__main__":
    # Simulate a few user actions
    handle_user_action("user_99")
    handle_user_action("user_101")

    # Clean up executor in a real app shutdown
    executor.shutdown(wait=True)
