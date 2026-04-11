# Copyright (c) 2025 Alogram Inc.
from unittest.mock import MagicMock, patch
import pytest
from datetime import datetime, timezone
from alogram_payrisk import (
    AlogramPublicClient,
    AlogramRiskClient,
    CheckRequest,
    EntityIds,
    Purchase,
    PaymentMethod,
    Card,
    SignalsRequest,
    PaymentEvent,
)

BASE_URL = "https://api.alogram.ai"
API_KEY = "sk_test_12345"
PUB_KEY = "pk_test_12345"


@pytest.fixture
def client():
    return AlogramRiskClient(base_url=BASE_URL, api_key=API_KEY)


@pytest.fixture
def pub_client():
    return AlogramPublicClient(base_url=BASE_URL, api_key=PUB_KEY)


def test_scrub_payload(client):
    """Verify that sensitive fields are masked in debug logs."""
    data = {
        "apiKey": "sk_live_verysecret",
        "email": "user@example.com",
        "phone": "+1234567890",
        "paymentMethod": {"type": "card", "bin": "411111", "cardNetwork": "visa"},
        "metadata": {"some_key": "some_value"},
    }

    scrubbed = client._scrub_payload(data)

    assert scrubbed["apiKey"] == "[MASKED]"
    assert scrubbed["email"] == "[MASKED]"
    assert scrubbed["phone"] == "[MASKED]"
    assert scrubbed["paymentMethod"]["bin"] == "[MASKED]"
    assert scrubbed["paymentMethod"]["type"] == "card"
    assert scrubbed["metadata"]["some_key"] == "[MASKED]"


def test_check_risk_passes_raw_object(client):
    """
    Verify that check_risk passes the raw Pydantic object to the API,
    not a dict, to avoid double-serialization/validation issues.
    """
    request = CheckRequest(
        entities=EntityIds(tenant_id="tid_test", client_id="cid_test"),
        purchase=Purchase(
            amount=100.0,
            currency="USD",
            payment_method=PaymentMethod(Card(type="card", bin="411111")),
        ),
    )

    with patch.object(client.risk_scoring, "risk_check") as mock_risk_check:
        client.check_risk(request)

        args, kwargs = mock_risk_check.call_args
        # Check that the request passed is the actual object
        assert kwargs["check_request"] == request
        assert isinstance(kwargs["check_request"], CheckRequest)


def test_ingest_signals_passes_raw_object(client):
    """Verify that ingest_signals passes the raw object."""
    request = SignalsRequest(
        entities=EntityIds(tenant_id="tid_test", client_id="cid_test"),
        event_type="login",
    )

    with patch.object(client.signals, "ingest_signals") as mock_ingest:
        client.ingest_signals(request)

        args, kwargs = mock_ingest.call_args
        assert kwargs["signals_request"] == request
        assert isinstance(kwargs["signals_request"], SignalsRequest)


def test_ingest_event_passes_raw_object(client):
    """Verify that ingest_event passes the raw object."""
    event = PaymentEvent(
        event_type="authorization",
        amount=100.0,
        currency="USD",
        payment_intent_id="pi_0123456789abcdef0123456789abcdef",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    with patch.object(client.signals, "ingest_payment_event") as mock_ingest:
        client.ingest_event(event)

        args, kwargs = mock_ingest.call_args
        assert kwargs["payment_event"] == event
        assert isinstance(kwargs["payment_event"], PaymentEvent)


def test_to_json_friendly_dict(client):
    """Verify that _to_json_friendly_dict calls to_dict() if available."""
    mock_model = MagicMock()
    mock_model.to_dict.return_value = {"key": "val"}

    result = client._to_json_friendly_dict(mock_model)
    assert result == {"key": "val"}
    mock_model.to_dict.assert_called_once()

    # Test with non-model
    regular_dict = {"a": 1}
    assert client._to_json_friendly_dict(regular_dict) == regular_dict


def test_public_client_ingest_signals_passes_raw_object(pub_client):
    """Verify that AlogramPublicClient.ingest_signals passes the raw object."""
    request = SignalsRequest(
        entities=EntityIds(tenant_id="tid_test", client_id="cid_test"),
        event_type="login",
    )

    with patch.object(pub_client.signals, "ingest_signals") as mock_ingest:
        pub_client.ingest_signals(request)

        args, kwargs = mock_ingest.call_args
        assert kwargs["signals_request"] == request
        assert isinstance(kwargs["signals_request"], SignalsRequest)
