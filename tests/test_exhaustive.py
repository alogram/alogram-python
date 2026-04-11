# Copyright (c) 2025 Alogram Inc.
import json
import pytest
from datetime import datetime, timezone
from alogram_payrisk import (
    AlogramRiskClient,
    CheckRequest,
    EntityIds,
    Purchase,
    PaymentMethod,
    Card,
    Wallet,
    Realtime,
    BankTransfer,
    Crypto,
    Invoice,
    DeviceInfo,
    IpInfo,
    Integrity,
    Identity,
    PostalAddress,
    MerchantContext,
    OrderContext,
    SignalsRequest,
    SignalsAccountVariant,
    SignalsInteractionVariant,
    Account,
    Interaction,
    PaymentEvent,
    PaymentOutcome,
    PaymentAuthorizationOutcome,
)

BASE_URL = "https://api.alogram.ai"
API_KEY = "sk_test_12345"


@pytest.fixture
def client():
    return AlogramRiskClient(base_url=BASE_URL, api_key=API_KEY)


def build_full_postal_address():
    return PostalAddress(
        address_line1="123 Main St",
        address_line2="Apt 4B",
        city="San Francisco",
        region="CA",
        postal_code="94105",
        country="US",
    )


def build_full_device_info():
    return DeviceInfo(
        fingerprint="fp_0123456789012345678901234567890123456789",
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        ip=IpInfo(
            ip_address="1.2.3.4",
            ip_version="ipv4",
            country="US",
            region="CA",
            city="San Francisco",
            asn="AS15169",
            organization="Google LLC",
        ),
        integrity=Integrity(is_bot=False, is_proxy=False, is_vpn=False, is_tor=False, is_hosting=False),
    )


def build_full_identity():
    return Identity(
        email="test-user@example.com",
        email_domain="example.com",
        phone="+14155552671",
        shipping_address=build_full_postal_address(),
        billing_address=build_full_postal_address(),
    )


def build_full_purchase(payment_method):
    return Purchase(
        location_id="loc_web_storefront",
        transaction_id="tx_01234567890123456789",
        timestamp=datetime.now(timezone.utc).isoformat(),
        amount=250.50,
        currency="USD",
        payment_method=payment_method,
        device_info=build_full_device_info(),
        merchant=MerchantContext(mcc="5812", merchant_country="US"),
        order=OrderContext(
            order_id="ord_987654321",
            order_total=250.50,
            shipping_method="ship",
            line_item_count=3,
        ),
        metadata=json.dumps({"test": True, "source": "exhaustive_test"}),
    )


def test_exhaustive_serialization(client):
    """
    Test serialization of CheckRequest with ALL possible PaymentMethod types
    and ALL optional fields populated.
    """

    payment_methods = [
        PaymentMethod(Card(type="card", card_network="visa", bin="411111", issuer_country="US")),
        PaymentMethod(Wallet(type="wallet", wallet_provider="apple_pay")),
        PaymentMethod(Realtime(type="realtime", realtime_network="pix")),
        PaymentMethod(BankTransfer(type="bank_transfer", bank_name="Chase")),
        PaymentMethod(Crypto(type="crypto", crypto_currency="BTC")),
        PaymentMethod(Invoice(type="invoice", invoice_id="INV-123")),
    ]

    for pm in payment_methods:
        request = CheckRequest(
            entities=EntityIds(
                tenant_id="tid_alogramtech",
                client_id="cid_demo",
                end_customer_id="ecid_0123456789",
                payment_instrument_id="pi_0123456789",
                device_id="did_0123456789012345678901234567890123456789",
                session_id="sid_0123456789",
            ),
            event_type="purchase",
            payment_intent_id="pi_0123456789abcdef0123456789abcdef",
            purchase=build_full_purchase(pm),
            identity=build_full_identity(),
        )

        # 1. Test to_dict()
        d = request.to_dict()
        assert isinstance(d, dict)
        assert d["eventType"] == "purchase"
        assert d["paymentIntentId"] == "pi_0123456789abcdef0123456789abcdef"
        assert "entities" in d
        assert "purchase" in d
        assert "identity" in d

        # Verify nested structures
        assert d["purchase"]["paymentMethod"]["type"] in [
            "card",
            "wallet",
            "realtime",
            "bank_transfer",
            "crypto",
            "invoice",
        ]
        assert d["purchase"]["deviceInfo"]["fingerprint"].startswith("fp_")
        assert d["identity"]["email"] == "test-user@example.com"
        assert d["identity"]["shippingAddress"]["country"] == "US"

        # 2. Test round-trip
        reconstructed = CheckRequest.from_dict(d)
        assert reconstructed.event_type == request.event_type
        assert reconstructed.entities.tenant_id == request.entities.tenant_id

        # 3. Test JSON serialization
        j = request.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed["eventType"] == "purchase"


def test_exhaustive_signals_serialization(client):
    """Test exhaustive serialization of SignalsRequest variants."""

    entities = EntityIds(tenant_id="tid_test", client_id="cid_test")

    # 1. Account Variant
    account_variant = SignalsAccountVariant(
        signal_type="account",
        entities=entities,
        account=Account(
            email="test@example.com",
            phone="+14155552671",
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata=json.dumps({"source": "test"}),
        ),
    )
    pm_acc = SignalsRequest(actual_instance=account_variant)
    d_acc = pm_acc.to_dict()
    assert d_acc["signalType"] == "account"
    assert d_acc["account"]["email"] == "test@example.com"

    # 2. Interaction Variant
    interaction_variant = SignalsInteractionVariant(
        signal_type="interaction",
        entities=entities,
        interactions=[
            Interaction(
                interaction_type="login",
                element_id="btn_submit",
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
        ],
    )
    pm_int = SignalsRequest(actual_instance=interaction_variant)
    d_int = pm_int.to_dict()
    assert d_int["signalType"] == "interaction"
    assert len(d_int["interactions"]) == 1
    assert d_int["interactions"][0]["interactionType"] == "login"


def test_exhaustive_payment_event_serialization(client):
    """Test exhaustive serialization of PaymentEvent."""
    event = PaymentEvent(
        event_type="authorization",
        payment_intent_id="pi_0123456789abcdef0123456789abcdef",
        timestamp=datetime.now(timezone.utc).isoformat(),
        amount=100.0,
        currency="USD",
        outcome=PaymentOutcome(authorization=PaymentAuthorizationOutcome(approved=True, responseCode="00")),
        metadata=json.dumps({"test": True}),
    )

    d = event.to_dict()
    assert d["eventType"] == "authorization"
    assert d["paymentIntentId"] == "pi_0123456789abcdef0123456789abcdef"
    assert d["amount"] == 100.0
    assert d["outcome"]["authorization"]["responseCode"] == "00"
    assert d["outcome"]["authorization"]["approved"] is True
