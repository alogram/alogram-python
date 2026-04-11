# Copyright (c) 2025 Alogram Inc.
from hypothesis import given, strategies as st, settings
from datetime import datetime, timezone
import pytest
from alogram_payrisk import (
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
    Identity,
    SignalsRequest,
    SignalsAccountVariant,
    SignalsInteractionVariant,
    Account,
    Interaction,
    PaymentEvent,
)

# --- Common Strategies ---

st_hex_32 = st.text("0123456789abcdef", min_size=32, max_size=32)
st_hex_64 = st.text("0123456789abcdef", min_size=64, max_size=64)
st_alphanum = st.text(
    st.characters(whitelist_categories=("Ll", "Lu", "Nd"), min_codepoint=48, max_codepoint=122),
    min_size=2,
    max_size=20,
)


@st.composite
def email_strategy(draw):
    user = draw(
        st.text(
            st.characters(
                whitelist_categories=("Ll", "Lu", "Nd"),
                min_codepoint=48,
                max_codepoint=122,
            ),
            min_size=1,
            max_size=20,
        )
    )
    domain = draw(
        st.text(
            st.characters(
                whitelist_categories=("Ll", "Lu", "Nd"),
                min_codepoint=48,
                max_codepoint=122,
            ),
            min_size=2,
            max_size=10,
        )
    )
    tld = draw(st.sampled_from(["com", "net", "org", "io"]))
    return f"{user}@{domain}.{tld}"


@st.composite
def entity_ids_strategy(draw):
    safe_chars = st.characters(whitelist_categories=("Ll", "Nd"), min_codepoint=48, max_codepoint=122)
    return EntityIds(
        tenant_id="tid_" + draw(st.text(safe_chars, min_size=2, max_size=10)),
        client_id="cid_" + draw(st.text(safe_chars, min_size=2, max_size=10)),
        end_customer_id="ecid_" + draw(st.text(safe_chars, min_size=2, max_size=10)),
        payment_instrument_id="pi_" + draw(st_alphanum),
        device_id="did_" + draw(st_alphanum),
        session_id="sid_" + draw(st_alphanum),
        email_hash="sha256_" + draw(st_hex_64),
        phone_hash="sha256_" + draw(st_hex_64),
    )


# --- Payment Method Strategies ---


@st.composite
def card_strategy(draw):
    return Card(
        type="card",
        card_network=draw(st.sampled_from(["visa", "mastercard", "amex", "discover", "jcb", "unionpay", "other"])),
        bin=draw(st.text("0123456789", min_size=6, max_size=8)),
        issuer_country=draw(st.text("ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=2, max_size=2)),
        cvv_result=draw(st.sampled_from(["M", "N", "P", "S", "U"])),
        avs_result=draw(
            st.sampled_from(
                [
                    "Y",
                    "N",
                    "A",
                    "Z",
                    "U",
                    "R",
                    "S",
                    "G",
                    "B",
                    "C",
                    "D",
                    "M",
                    "P",
                    "X",
                    "W",
                ]
            )
        ),
    )


@st.composite
def wallet_strategy(draw):
    return Wallet(
        type="wallet",
        wallet_provider=draw(st.sampled_from(["apple_pay", "google_pay", "samsung_pay", "paypal", "venmo", "other"])),
    )


@st.composite
def realtime_strategy(draw):
    return Realtime(
        type="realtime",
        realtime_type=draw(st.sampled_from(["zelle", "rtp", "fed_now", "faster_payments", "upi"])),
    )


@st.composite
def payment_method_strategy(draw):
    variant = draw(st.sampled_from(["card", "wallet", "realtime", "bank_transfer", "crypto", "invoice"]))
    if variant == "card":
        return PaymentMethod(draw(card_strategy()))
    elif variant == "wallet":
        return PaymentMethod(draw(wallet_strategy()))
    elif variant == "realtime":
        return PaymentMethod(draw(realtime_strategy()))
    elif variant == "bank_transfer":
        return PaymentMethod(BankTransfer(type="bank_transfer"))
    elif variant == "crypto":
        return PaymentMethod(Crypto(type="crypto"))
    else:
        return PaymentMethod(Invoice(type="invoice"))


# --- Request Strategies ---


@st.composite
def identity_strategy(draw):
    return Identity(
        email=draw(email_strategy()),
        phone="+1" + draw(st.text("0123456789", min_size=10, max_size=10)),
    )


@st.composite
def check_request_strategy(draw):
    return CheckRequest(
        entities=draw(entity_ids_strategy()),
        event_type="purchase",
        payment_intent_id="pi_" + draw(st_hex_32),
        purchase=Purchase(
            location_id="loc_web",
            transaction_id="tx_" + draw(st_alphanum),
            timestamp=datetime.now(timezone.utc).isoformat(),
            amount=draw(st.floats(min_value=0.01, max_value=10000.0)),
            currency="USD",
            payment_method=draw(payment_method_strategy()),
        ),
        identity=draw(identity_strategy()),
    )


@st.composite
def signals_request_strategy(draw):
    variant = draw(st.sampled_from(["account", "interaction"]))
    entities = draw(entity_ids_strategy())

    if variant == "account":
        return SignalsRequest(
            SignalsAccountVariant(
                signal_type="account",
                entities=entities,
                account=Account(email=draw(email_strategy())),
            )
        )
    else:
        return SignalsRequest(
            SignalsInteractionVariant(
                signal_type="interaction",
                entities=entities,
                interactions=[
                    Interaction(
                        interaction_type=draw(st.sampled_from(["login", "page_view", "custom_event"])),
                        timestamp=datetime.now(timezone.utc).isoformat(),
                    )
                ],
            )
        )


@st.composite
def payment_event_strategy(draw):
    return PaymentEvent(
        event_type=draw(st.sampled_from(["authorization", "capture", "refund"])),
        payment_intent_id="pi_" + draw(st_hex_32),
        timestamp=datetime.now(timezone.utc).isoformat(),
        amount=draw(st.floats(min_value=0.01, max_value=10000.0)),
        currency="USD",
    )


# --- Tests ---


@settings(max_examples=100, deadline=None)
@given(check_request_strategy())
def test_fuzz_check_request(request_obj):
    d = request_obj.to_dict()
    reconstructed = CheckRequest.from_dict(d)
    assert reconstructed.entities.tenant_id == request_obj.entities.tenant_id
    assert (
        reconstructed.purchase.payment_method.actual_instance.type
        == request_obj.purchase.payment_method.actual_instance.type
    )


@settings(max_examples=50, deadline=None)
@given(signals_request_strategy())
def test_fuzz_signals_request(request_obj):
    d = request_obj.to_dict()
    reconstructed = SignalsRequest.from_dict(d)
    assert reconstructed.actual_instance.signal_type == request_obj.actual_instance.signal_type


@settings(max_examples=50, deadline=None)
@given(payment_event_strategy())
def test_fuzz_payment_event(event_obj):
    d = event_obj.to_dict()
    reconstructed = PaymentEvent.from_dict(d)
    assert reconstructed.payment_intent_id == event_obj.payment_intent_id
    assert reconstructed.event_type == event_obj.event_type


if __name__ == "__main__":
    pytest.main([__file__])
