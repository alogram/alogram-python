# Copyright (c) 2025 Alogram Inc.
# All rights reserved.

import os
import sys

# 🚀 Standard Vendoring: Make the internal 'payrisk_v1' package discoverable
# This allows machine-generated models to resolve their absolute imports
# (e.g. from payrisk_v1.models...) without manual source patches.
_internal_path = os.path.join(os.path.dirname(__file__), "_generated")
if _internal_path not in sys.path:
    sys.path.insert(0, _internal_path)

# 1. Core Clients
from .client import AlogramPublicClient, AlogramRiskClient  # noqa: E402

# 2. Canonical Models (Ergonomic exports for SDK users)
from payrisk_v1.models.card import Card  # noqa: E402
from payrisk_v1.models.wallet import Wallet  # noqa: E402
from payrisk_v1.models.realtime import Realtime  # noqa: E402
from payrisk_v1.models.bank_transfer import BankTransfer  # noqa: E402
from payrisk_v1.models.crypto import Crypto  # noqa: E402
from payrisk_v1.models.invoice import Invoice  # noqa: E402
from payrisk_v1.models.integrity import Integrity  # noqa: E402
from payrisk_v1.models.postal_address import PostalAddress  # noqa: E402
from payrisk_v1.models.signals_account_variant import SignalsAccountVariant  # noqa: E402
from payrisk_v1.models.signals_interaction_variant import (
    SignalsInteractionVariant,
)  # noqa: E402
from payrisk_v1.models.account import Account  # noqa: E402
from payrisk_v1.models.interaction import Interaction  # noqa: E402

# Canonical Models (Flattened for ergonomic use)
from payrisk_v1.models.check_request import CheckRequest  # noqa: E402
from payrisk_v1.models.decision_response import DecisionResponse  # noqa: E402
from payrisk_v1.models.device_info import DeviceInfo  # noqa: E402, F401
from payrisk_v1.models.entity_ids import EntityIds  # noqa: E402
from payrisk_v1.models.identity import Identity  # noqa: E402
from payrisk_v1.models.ip_info import IpInfo  # noqa: E402
from payrisk_v1.models.merchant_context import MerchantContext  # noqa: E402, F401
from payrisk_v1.models.order_context import OrderContext  # noqa: E402, F401
from payrisk_v1.models.payment_event import PaymentEvent  # noqa: E402
from payrisk_v1.models.payment_method import PaymentMethod  # noqa: E402
from payrisk_v1.models.payment_outcome import PaymentOutcome  # noqa: E402
from payrisk_v1.models.payment_authorization_outcome import (
    PaymentAuthorizationOutcome,
)  # noqa: E402

from payrisk_v1.models.purchase import Purchase  # noqa: E402
from payrisk_v1.models.signals_request import SignalsRequest  # noqa: E402

# 3. Professional Exceptions
from .exceptions import (  # noqa: E402
    AlogramError,
    AuthenticationError,
    RateLimitError,
    InternalServerError,
    ScopedAccessError,
    ValidationError,
)

__all__ = [
    "AlogramPublicClient",
    "AlogramRiskClient",
    "CheckRequest",
    "DecisionResponse",
    "DeviceInfo",
    "EntityIds",
    "Purchase",
    "PaymentMethod",
    "PaymentEvent",
    "PaymentOutcome",
    "PaymentAuthorizationOutcome",
    "SignalsRequest",
    "AlogramError",
    "AuthenticationError",
    "RateLimitError",
    "InternalServerError",
    "ScopedAccessError",
    "ValidationError",
    "Card",
    "Wallet",
    "Realtime",
    "BankTransfer",
    "Crypto",
    "Invoice",
    "Identity",
    "IpInfo",
    "Integrity",
    "PostalAddress",
    "SignalsAccountVariant",
    "SignalsInteractionVariant",
    "Account",
    "Interaction",
]
