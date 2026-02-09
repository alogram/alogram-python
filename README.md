# Alogram Payrisk Python SDK

[![PyPI version](https://badge.fury.io/py/alogram-payrisk.svg)](https://badge.fury.io/py/alogram-payrisk)
[![Python Versions](https://img.shields.io/pypi/pyversions/alogram-payrisk.svg)](https://pypi.org/project/alogram-payrisk/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

The official Python client for the **Alogram Payments Risk API**. This SDK provides a robust, "smart" interface for checking fraud risk, ingesting behavioral signals, and managing payment lifecycle events.

**Key Features:**
*   **Resilient:** Built-in retries with exponential backoff for network glips and rate limits.
*   **Traceable:** Automatic injection of `x-trace-id` and `x-idempotency-key` for every request.
*   **Observable:** First-class support for **OpenTelemetry** spans and attributes.
*   **Typed:** Fully typed request/response models using Pydantic.
*   **Pythonic:** Idiomatic exceptions (`AuthenticationError`, `RateLimitError`) instead of raw HTTP status codes.

---

## 🏗️ Installation

Requires Python 3.9+.

```bash
pip install alogram-payrisk
```

To enable OpenTelemetry support:
```bash
pip install "alogram-payrisk[telemetry]"
```

---

## 🚀 Quickstart

### 1. Initialize the Client

You can configure the client using the constructor or environment variables.

```python
from alogram_payrisk import AlogramRiskClient

# The client handles connection pooling and headers automatically
client = AlogramRiskClient(
    base_url="https://api.alogram.ai",
    api_key="sk_live_...",
    tenant_id="your_tenant_id",  # Optional: default tenant context
    debug=False  # Set to True to see raw HTTP logs
)
```

### 2. Check Risk (The "Hello World")

```python
from alogram_payrisk import CheckRequest, Purchase, EntityIds, PaymentMethod, Card

request = CheckRequest(
    event_type="purchase",
    entities=EntityIds(
        tenant_id="tenant_123",
        client_id="client_abc",
        end_customer_id="cust_user_55"
    ),
    purchase=Purchase(
        amount=99.00,
        currency="USD",
        transaction_id="tx_789xyz",
        payment_method=PaymentMethod(
            type="card",
            card=Card(bin="424242", last4="4242", issuer_country="US")
        )
    )
)

try:
    decision = client.check_risk(request)
    
    if decision.decision == "approve":
        print(f"✅ Approved! Risk Score: {decision.risk_score}")
    else:
        print(f"🛑 Declined. Reasons: {decision.reasons}")
        
except Exception as e:
    print(f"Error checking risk: {e}")

---

## 📊 Observability (OpenTelemetry)

The SDK automatically detects if OpenTelemetry is installed and configured in your environment. It will emit spans for all API calls, including details about retries and decision outcomes.

**Captured Attributes:**
*   `alogram.tenant_id`
*   `alogram.event_type`
*   `alogram.idempotency_key`
*   `alogram.trace_id`
*   `alogram.decision` (for risk checks)

No extra configuration is required other than standard OTel setup in your application.

---

## 🛡️ Authentication

The SDK supports two authentication modes:

1.  **API Key (Standard):**
    Pass `api_key` to the constructor. Best for backend services.
    ```python
    client = AlogramRiskClient(api_key="sk_live_...")
    ```

2.  **OIDC / Access Token (Advanced):**
    For environments using short-lived tokens (e.g., GCP Service Accounts).
    ```python
    client = AlogramRiskClient(access_token="eyJhbGci...")
    ```

---

## 🧠 Core Concepts

### Idempotency & Tracing
The SDK automatically generates unique IDs for every request if you don't provide them. This ensures safe retries without double-billing or double-processing.

```python
# Automatic (Recommended)
client.check_risk(request) 
# -> Generates x-idempotency-key: idk_uuid...
# -> Generates x-trace-id: trc_uuid...

# Manual (For when you have your own tracking IDs)
client.check_risk(
    request, 
    idempotency_key="my_unique_order_id_123",
    trace_id="my_trace_id_abc"
)
```

### Automatic Retries
The client uses `tenacity` to automatically retry requests that fail with transient errors:
*   `5xx` Server Errors
*   `429` Rate Limit Exceeded

It uses **exponential backoff** (starting at 2s, up to 10s, max 3 attempts). You do not need to write your own retry loops.

### Webhook Security
Always verify incoming webhooks to ensure they are from Alogram.

```python
from alogram_payrisk import WebhookVerifier

# Returns True or raises ValidationError
WebhookVerifier.verify(
    payload=request.data,
    header_signature=request.headers["x-alogram-signature"],
    secret="your_webhook_secret"
)
```

---

## ⚠️ Error Handling

The SDK maps standard HTTP errors to specific Python exceptions, allowing you to handle failure cases gracefully.

| Exception | HTTP Status | Description |
| :--- | :--- | :--- |
| `AuthenticationError` | 401, 403 | Invalid API Key or Permissions. **Not Retried.** |
| `ValidationError` | 400, 422 | Invalid request body or missing fields. **Not Retried.** |
| `RateLimitError` | 429 | Too many requests. **Automatically Retried.** |
| `InternalServerError` | 500+ | Server-side issues. **Automatically Retried.** |
| `AlogramError` | * | Base class for all SDK errors. |

**Example:**

```python
from alogram_payrisk import AlogramRiskClient, RateLimitError, ValidationError

try:
    client.check_risk(...)
except ValidationError as e:
    # Logic error in your code (e.g., missing field)
    print(f"Fix your request: {e}")
except RateLimitError:
    # Back off and try again later (after auto-retries failed)
    print("System busy, queuing for later.")
```

---

## 🔧 Logging

The SDK uses the standard Python `logging` module under the namespace `alogram.payrisk`.

```python
import logging

# Enable debug logging to see full request/response details
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("alogram.payrisk").setLevel(logging.DEBUG)
```

## 🧩 Data Models & Type Safety

Alogram Payrisk models are built using **Pydantic v2**. This provides several benefits:
*   **Runtime Validation:** Data is validated when models are created.
*   **Editor Support:** Full autocomplete and inline documentation in VSCode, PyCharm, and other IDEs.
*   **Serialization:** Easy conversion to/from JSON or Python dictionaries.

### Exploring Models
You can inspect any model using Python's built-in `help()` or by accessing `.model_json_schema()`:

```python
from alogram_payrisk import Purchase
help(Purchase)
# or
print(Purchase.model_json_schema())
```

---

## 📚 Cookbook Examples

Explore the `examples/` directory for advanced integration patterns:

*   [**Async Signal Ingestion**](examples/async_signal_ingestion.py): Ingest behavioral signals without blocking your main application loop.
*   [**Production Error Handling**](examples/production_error_handling.py): Implement "Fail Open" strategies and robust logging.
*   [**Custom Idempotency**](examples/custom_idempotency.py): Use your own Order IDs to ensure safe retries across systems.

---

## 🛠️ Development & Testing

```bash
# Install dev dependencies
uv sync --extra dev

# Run tests
PYTHONPATH=src uv run pytest
```

---

## 📦 License

Apache 2.0
