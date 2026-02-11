# Copyright (c) 2025 Alogram Inc.
# Comprehensive test suite for the Alogram Payrisk Python SDK

import json
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from alogram_payrisk import (
    AlogramPublicClient,
    AlogramRiskClient,
    CheckRequest,
    ScopedAccessError,
)

BASE_URL = "https://api.alogram.ai"
SECRET_KEY = "sk_test_12345"
PUBLIC_KEY = "pk_test_12345"


@pytest.fixture
def client():
    return AlogramRiskClient(
        base_url=BASE_URL, api_key=SECRET_KEY, tenant_id="tid_default"
    )


def build_valid_request_dict():
    return {
        "entities": {
            "tenantId": "tid_test",
            "clientId": "cid_test",
            "endCustomerId": "ecid_test_customer",
        },
        "eventType": "purchase",
        "purchase": {
            "locationId": "loc_123",
            "transactionId": "tx_test_123456789",
            "timestamp": "2023-10-01T12:00:00Z",
            "amount": 10.0,
            "currency": "USD",
            "paymentMethod": {
                "type": "card",
                "cardNetwork": "visa",
                "bin": "411111",
                "issuerCountry": "US",
            },
        },
    }


def mock_rest_response(status, data=None, headers=None, reason=None):
    resp = MagicMock()
    resp.status = status
    resp.reason = reason or "OK"
    resp.data = json.dumps(data).encode("utf-8") if data is not None else b""
    
    # Ensure headers is a real dict for the generated client's ApiResponse validation
    headers_dict = headers or {"content-type": "application/json"}
    resp.headers = headers_dict

    def getheader(name, default=None):
        return headers_dict.get(name.lower(), default)

    resp.getheader = getheader

    def getheaders():
        return headers_dict

    resp.getheaders = getheaders
    return resp


def test_scoped_initialization():
    # Secret Client must have sk_ or none
    with pytest.raises(ScopedAccessError):
        AlogramRiskClient(base_url=BASE_URL, api_key=PUBLIC_KEY)

    # Public Client must have pk_ or none
    with pytest.raises(ScopedAccessError):
        AlogramPublicClient(base_url=BASE_URL, api_key=SECRET_KEY)


def test_check_risk_success(client):
    request_data = build_valid_request_dict()
    valid_response = {
        "assessmentId": "as_12345678901234567890123456789012",
        "decision": "approve",
        "riskScore": 0.1,
        "paymentIntentId": "pi_12345678901234567890123456789012",
        "decisionAt": datetime.now(timezone.utc).isoformat(),
    }

    with patch.object(client.api_client.rest_client, "request") as mock_req:
        mock_req.return_value = mock_rest_response(200, valid_response)
        resp = client.check_risk(CheckRequest.from_dict(request_data))
        assert resp.decision == "approve"

        args, kwargs = mock_req.call_args
        sent_headers = kwargs["headers"]
        assert sent_headers["x-api-key"] == SECRET_KEY


def test_public_client_restricted_methods():
    pub_client = AlogramPublicClient(base_url=BASE_URL, api_key=PUBLIC_KEY)

    # Should only have ingest_signals
    assert hasattr(pub_client, "ingest_signals")
    assert not hasattr(pub_client, "check_risk")
    assert not hasattr(pub_client, "ingest_event")


def test_retry_logic_on_500(client):
    request_data = build_valid_request_dict()
    valid_response = {
        "assessmentId": "as_retrysuccess12345678901234567",
        "decision": "approve",
        "riskScore": 0.5,
        "paymentIntentId": "pi_00000000000000000000000000000000",
        "decisionAt": datetime.now(timezone.utc).isoformat(),
    }

    with patch.object(client.api_client.rest_client, "request") as mock_req:
        mock_req.side_effect = [
            mock_rest_response(500, {"code": 500}, reason="Internal Error"),
            mock_rest_response(500, {"code": 500}, reason="Internal Error"),
            mock_rest_response(200, valid_response),
        ]
        resp = client.check_risk(CheckRequest.from_dict(request_data))
        assert resp.decision == "approve"
        assert mock_req.call_count == 3
