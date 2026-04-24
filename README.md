<p align="center">
  <img src="https://raw.githubusercontent.com/alogram/alogram-python/main/.github/assets/logo.png" width="200" alt="Alogram PayRisk Logo">
</p>

# Alogram PayRisk SDK for Python

[![PyPI version](https://badge.fury.io/py/alogram-payrisk.svg)](https://badge.fury.io/py/alogram-payrisk)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

The official Python client for the **Alogram PayRisk Engine**. 

Alogram PayRisk is a decision management and risk orchestration engine for global commerce. It fuses machine learning, behavioral analytics, and deterministic business rules into a high-fidelity scoring pipeline designed for enterprise scale and auditability.
## 🧠 The Three-Expert Architecture

The SDK provides unified access to three specialized risk experts:

-   **Risk Scoring**: Real-time assessment and decision orchestration for purchases.
-   **Signal Intelligence**: Ingestion of behavioral telemetry and payment lifecycle events.
-   **Forensic Data**: Deep visibility into historical assessments and decision transparency.

---

## 🔐 Security: Trust Boundaries

Alogram enforces a strict separation between client-side telemetry and server-side decisioning.

| Client Type | Key Prefix | Environment | Capabilities |
| :--- | :--- | :--- | :--- |
| **`AlogramPublicClient`** | `pk_...` | Browser / Mobile | **Ingestion only.** Cannot perform risk checks or view scores. |
| **`AlogramRiskClient`** | `sk_...` | Secure Backend | **Full access.** Authorized for risk decisions and forensic retrieval. |

> [!WARNING]
> **Never** use a Secret Key (`sk_...`) in a client-side environment. This will expose your tenant's sensitive forensic data.

---

## 🔄 Full Lifecycle Integration

A best-in-class Alogram integration follows the three-step lifecycle:

```python
from alogram_payrisk import AlogramRiskClient
from payrisk_v1 import CheckRequest, PaymentEvent

# 1. Initialize the Secret Client (Backend Only)
with AlogramRiskClient(api_key="sk_live_...", tenant_id="tid_mycorp") as client:

    # 2. Assessment: Call before charging the customer
    decision = client.check_risk(CheckRequest(...))

    if decision.decision == "approve":
        # Process payment via your gateway...

        # 3. Lifecycle: Send the outcome back to Alogram
        client.ingest_event(PaymentEvent(
            payment_intent_id=decision.payment_intent_id,
            event_type="authorization",
            outcome={"approved": True}
        ))
```

---

## 🚀 High-Performance Integration
-   **🏢 Smart Client Architecture**: Specialized clients for server-side (`AlogramRiskClient`) and public-facing (`AlogramPublicClient`).
-   **🛡️ Automated Identity**: Injects `x-api-key`, `Authorization`, and tenant headers automatically.
-   **🔄 Built-in Resiliency**: Automatic exponential backoff and jittered retries (powered by `tenacity`).
-   **🕵️ Native Observability**: Built-in OpenTelemetry tracing for monitoring risk decision latency and outcomes.
-   **🧩 Type Safe**: Built with Pydantic v2 and full PEP 561 compliance (`py.typed`).

## 📦 Installation

```bash
pip install alogram-payrisk
```

## 🛠️ Quick Start

### 1. Evaluate Risk (Risk Scoring Expert)

Assess a purchase in real-time. This invokes the authoritative scoring pipeline.

```python
from alogram_payrisk import AlogramRiskClient, CheckRequest, Purchase, Identity

client = AlogramRiskClient(api_key="sk_live_...", tenant_id="tenant_123")

# Perform the check via the Risk Scoring expert
decision = client.check_risk(CheckRequest(
    purchase=Purchase(amount=99.99, currency="USD"),
    identity=Identity(email="customer@example.com")
))

print(f"Decision: {decision.decision} | Score: {decision.decision_score}")
```

### 2. Ingest Lifecycle Events (Signal Intelligence Expert)

Stream payment lifecycle updates to the Engine for continuous model training.

```python
from alogram_payrisk import PaymentEvent, PaymentOutcome, PaymentAuthorizationOutcome

client.ingest_event(PaymentEvent(
    event_type="authorization",
    payment_intent_id="pi_123...",
    amount=99.99,
    currency="USD",
    outcome=PaymentOutcome(
        authorization=PaymentAuthorizationOutcome(approved=True, responseCode="00")
    )
))
```

### 🔄 3. Full Lifecycle Workflow

For a complete end-to-end example showing how to correlate **client-side signals**, **risk scoring**, and **fraud labeling**, see:
👉 [examples/full_lifecycle_workflow.py](examples/full_lifecycle_workflow.py)

This workflow demonstrates how to:
1.  **Anchor** pre-order signals using `sessionId` and `deviceId`.
2.  **Correlate** those signals during the `check_risk` call.
3.  **Handoff** to the server-minted `paymentIntentId` for post-order events (Auth, Capture, Chargeback).

---

## 🚀 High-Performance Integration

To ensure sub-second risk assessment latencies and handle high-volume signal telemetry efficiently, please adhere to these network best practices:

-   **Persistent Client (Mandatory):** Maintain a single, global instance of the `AlogramRiskClient` or use it as a Context Manager. 
    -   *Anti-pattern:* Creating a new client for every request forces a fresh TCP/TLS handshake.
    -   *Best Practice:* Reuse the client to keep the underlying `httpx` session "hot."
-   **HTTP/2 Multiplexing:** The SDK natively supports HTTP/2. By reusing the client, multiple requests (e.g., several signals) are automatically multiplexed over a single persistent pipe, eliminating connection management overhead.

## 🛡️ Error Handling & Resiliency

The SDK distinguishes between transient network issues and validation errors.

```python
from alogram_payrisk.exceptions import ValidationError, AlogramError

try:
    decision = client.check_risk(request)
except ValidationError as e:
    # ❌ Handle invalid input (e.g., invalid BIN or malformed email)
    print(f"Validation Failed: {e.body}") 
except AlogramError as e:
    # 🚨 Handle generic API or Authentication errors
    print(f"API Error [{e.status}]: {e.message}")
```

## 🕵️ Observability (OpenTelemetry)

The SDK automatically detects OpenTelemetry. If present, it creates spans for all API calls.

```python
from opentelemetry import trace

# Spans will automatically include 'alogram.decision' and 'alogram.trace_id'
with trace.get_tracer(__name__).start_as_current_span("checkout"):
    decision = client.check_risk(request)
```

## 🏗️ Environments

| Environment | Base URL | Key Type |
| :--- | :--- | :--- |
| **Production** | `https://api.alogram.ai` | `sk_live_...` |
| **Sandbox** | `https://api-sandbox.alogram.ai` | `sk_test_...` |
| **Local** | `http://localhost:8080` | `test` |

---

## 🤖 For AI Agents

If using an AI agent (ChatGPT, Claude, Gemini) for integration, provide this context:
> "Use the Alogram PayRisk Python SDK. Always prefer the `AlogramRiskClient` for backend operations. Access the authoritative blended score via the `decision_score` attribute of the response. Use the `idempotency_key` parameter for all write operations."

---

## ⚖️ License

Apache License 2.0. See [LICENSE](LICENSE) for details.
