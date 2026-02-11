# Alogram PayRisk SDK for Python

[![PyPI version](https://badge.fury.io/py/alogram-payrisk.svg)](https://badge.fury.io/py/alogram-payrisk)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

The official Alogram PayRisk 'Smart' SDK for Python. Built for modern financial systems that require high resiliency, ergonomic risk intelligence, and automated identity management.

## 🚀 Features

-   **🏢 Smart Client Architecture**: Specialized clients for server-side (`AlogramRiskClient`) and public-facing (`AlogramPublicClient`) environments.
-   **🛡️ Automated Identity**: Injects `x-api-key`, `Authorization`, and tenant headers automatically.
-   **🔄 Built-in Resiliency**: Transparent exponential backoff and jittered retries powered by `tenacity`.
-   **🕵️ OpenTelemetry Ready**: Native tracing support for deep observability into risk decisions.
-   **🧩 Type Safe**: Built with Pydantic v2 and full PEP 561 compliance (`py.typed`).

## 📦 Installation

```bash
pip install alogram-payrisk
```

## 🛠️ Quick Start

### Evaluate Risk (Server-Side)

```python
from alogram_payrisk import AlogramRiskClient
from alogram_payrisk.models import CheckRequest, Purchase, Identity

# Initialize the smart client
client = AlogramRiskClient(
    api_key="sk_live_your_secret_key",
    tenant_id="tenant_123"
)

# Perform the check with automatic retries and tracing
decision = client.check_risk(CheckRequest(
    purchase=Purchase(amount=99.99, currency="USD"),
    identity=Identity(email="customer@example.com")
))

print(f"Risk Decision: {decision.decision}")
```

---

## 🛡️ Error Handling

The SDK provides specific exceptions for robust error state management:

```python
from alogram_payrisk.exceptions import RateLimitError, ValidationError, AlogramError

try:
    decision = client.check_risk(request)
except RateLimitError:
    # 🔄 Standard exponential backoff is handled by the SDK
    pass
except ValidationError as e:
    # ❌ Check e.body for specific field validation errors
    print(f"Invalid request: {e}")
except AlogramError as e:
    # 🚨 Generic fallback for other API issues
    print(f"API Error: {e.status_code}")
```

## 🔑 Authentication & Keys

To use the Alogram SDK, you need API keys from the [Alogram Dashboard](https://dashboard.alogram.ai/keys).

| Key Type | Prefix | Client | Use Case |
| :--- | :--- | :--- | :--- |
| **Secret Key** | `sk_live_...` | `AlogramRiskClient` | Server-side risk checks. **Never expose.** |
| **Publishable Key** | `pk_live_...` | `AlogramPublicClient` | Frontend signals & browser ingestion. |

## 🤖 For AI Agents (Integration Context)

If you are using an AI agent (like ChatGPT, Claude, or Gemini) to help with your integration, provide it with the following context:

> "I am integrating the Alogram PayRisk Python SDK. I need to implement a risk check during my checkout endpoint. Use the `AlogramRiskClient`, handle `RateLimitError` gracefully, and ensure you use the `idempotency_key` from my transaction ID."

---

## 🧪 Local Testing & Mocking

For fast unit tests without network dependencies, use the built-in `MockRiskClient`.

```python
from alogram_payrisk.testing import MockRiskClient

mock = MockRiskClient()
mock.queue_decision("decline", score=0.95, reason="high_risk_ip")

# Your app code uses the mock as if it were a real client
decision = my_app.process_checkout(mock)
assert decision.decision == "decline"
```

## 🏗️ Environment Testing

### Alogram Sandbox
For safe integration testing without impacting production data, point your client to the Sandbox environment:
```python
client = AlogramRiskClient(
    api_key="sk_test_...",
    base_url="https://api-sandbox.alogram.ai"
)
```

### Local Emulator
For hermetic local testing, run the **Alogram Local Emulator**:
```bash
docker run -p 8080:8080 alogram/payrisk-emulator
```
Point your client to the local instance:
```python
client = AlogramRiskClient(base_url="http://localhost:8080", api_key="test")
```

---

## 📚 Documentation

For full API reference, visit [docs.alogram.ai](https://docs.alogram.ai).

## ⚖️ License

Apache License 2.0. See [LICENSE](LICENSE) for details.
