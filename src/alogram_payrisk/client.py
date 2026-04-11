# Copyright (c) 2025 Alogram Inc.
# All rights reserved.

import logging
import uuid
from typing import Any, Optional, cast

from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential_jitter,
)

# --- OpenTelemetry Support (Soft Dependency) ---
try:
    from opentelemetry import trace  # type: ignore

    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    trace = None  # type: ignore

# Internal Imports
from ._generated.payrisk_v1.api.risk_scoring_api import RiskScoringApi
from ._generated.payrisk_v1.api.signal_intelligence_api import SignalIntelligenceApi
from ._generated.payrisk_v1.api.forensic_data_api import ForensicDataApi
from ._generated.payrisk_v1.api_client import ApiClient
from ._generated.payrisk_v1.configuration import Configuration
from ._generated.payrisk_v1.exceptions import ApiException
from ._generated.payrisk_v1.models.check_request import CheckRequest
from ._generated.payrisk_v1.models.decision_response import DecisionResponse
from ._generated.payrisk_v1.models.payment_event import PaymentEvent
from ._generated.payrisk_v1.models.signals_request import SignalsRequest
from ._generated.payrisk_v1.models.scores_success_response import ScoresSuccessResponse

# Public Exceptions
from .exceptions import (
    AlogramError,
    AuthenticationError,
    InternalServerError,
    RateLimitError,
    ScopedAccessError,
    ValidationError,
)

log = logging.getLogger("alogram.payrisk")


def is_retryable_error(exception: BaseException) -> bool:
    """Helper to determine if an error should trigger a retry."""
    if isinstance(exception, (RateLimitError, InternalServerError)):
        return True
    return False


class AlogramBaseClient:
    """Internal base class for shared SDK logic."""

    tracer: Optional["trace.Tracer"]  # type: ignore

    def __init__(
        self,
        base_url: str = "https://api.alogram.ai",
        api_key: Optional[str] = None,
        access_token: Optional[str] = None,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        debug: bool = False,
    ):
        self.configuration = Configuration(host=base_url)
        self.configuration.debug = debug

        # 🛡️ SECURITY: Prevent raw http.client/urllib3 from leaking unmasked secrets to stdout
        # when debug=True. We want our own masked logs, not the raw library output.
        if debug:
            import http.client as httplib

            httplib.HTTPConnection.debuglevel = 0
            logging.getLogger("urllib3").setLevel(logging.INFO)

        self.api_client = ApiClient(self.configuration)

        if api_key:
            self.api_client.set_default_header("x-api-key", api_key)
        if access_token:
            self.api_client.set_default_header("Authorization", f"Bearer {access_token}")

        if tenant_id:
            self.api_client.set_default_header("x-trusted-tenant-id", tenant_id)
        if client_id:
            self.api_client.set_default_header("x-trusted-client-id", client_id)

        # Multi-Expert APIs (Tag-based organization in 0.2.5+)
        self.risk_scoring = RiskScoringApi(self.api_client)
        self.signals = SignalIntelligenceApi(self.api_client)
        self.forensics = ForensicDataApi(self.api_client)

        # Initialize Tracer
        if OTEL_AVAILABLE:
            self.tracer = trace.get_tracer("alogram.payrisk", "0.2.8")
        else:
            self.tracer = None  # type: ignore

    def _generate_id(self, prefix: str) -> str:
        return f"{prefix}_{uuid.uuid4().hex}"

    def _map_exception(self, e: ApiException) -> AlogramError:
        msg = f"API Error: {e.reason}"
        body_str = cast(Optional[str], e.body)
        if e.status == 401 or e.status == 403:
            return AuthenticationError(msg, status=e.status, body=body_str)
        if e.status == 429:
            return RateLimitError(msg, status=e.status, body=body_str)
        if e.status == 400 or e.status == 422:
            return ValidationError(msg, status=e.status, body=body_str)
        if e.status >= 500:
            return InternalServerError(msg, status=e.status, body=body_str)
        return AlogramError(msg, status=e.status, body=body_str)

    def _to_json_friendly_dict(self, model: Any) -> Any:
        if hasattr(model, "to_dict"):
            return model.to_dict()
        return model

    def _scrub_payload(self, data: Any) -> Any:
        """Recursively mask sensitive fields in a dictionary for safe logging."""
        if not isinstance(data, dict):
            return data

        sensitive_substrings = (
            "key",
            "token",
            "secret",
            "auth",
            "password",
            "email",
            "phone",
            "card",
            "bin",
        )

        scrubbed = {}
        for k, v in data.items():
            k_str = str(k).lower()
            if isinstance(v, dict):
                scrubbed[k] = self._scrub_payload(v)
            elif isinstance(v, list):
                scrubbed[k] = [self._scrub_payload(i) if isinstance(i, dict) else i for i in v]
            elif any(sub in k_str for sub in sensitive_substrings):
                scrubbed[k] = "[MASKED]"
            else:
                scrubbed[k] = v
        return scrubbed

    def __enter__(self) -> "AlogramBaseClient":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if hasattr(self.api_client, "close"):
            self.api_client.close()


class AlogramRiskClient(AlogramBaseClient):
    """🏢 **AlogramRiskClient** (Secret Client)

    Designed for server-side environments using a Secret Key (`sk_...`).
    Provides full access to risk decisioning and score retrieval.
    """

    def __init__(
        self,
        base_url: str = "https://api.alogram.ai",
        api_key: Optional[str] = None,
        access_token: Optional[str] = None,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        debug: bool = False,
    ):
        if api_key and api_key.startswith("pk_"):
            raise ScopedAccessError(
                "Cannot initialize AlogramRiskClient with a Publishable Key (pk_...). "
                "Please use AlogramPublicClient for client-side ingestion or provide a Secret Key (sk_...)."
            )
        super().__init__(
            base_url=base_url,
            api_key=api_key,
            access_token=access_token,
            tenant_id=tenant_id,
            client_id=client_id,
            debug=debug,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(initial=1, max=10, jitter=1),
        retry=retry_if_exception(is_retryable_error),
        reraise=True,
    )
    def check_risk(self, request: CheckRequest, **kwargs) -> DecisionResponse:
        """📥 Evaluate risk for a purchase or entity."""
        ik = kwargs.get("idempotency_key") or self._generate_id("idk")
        tid = kwargs.get("trace_id") or self._generate_id("trc")

        if hasattr(request, "entities") and request.entities:
            self.api_client.set_default_header("x-trusted-tenant-id", request.entities.tenant_id)
            self.api_client.set_default_header("x-trusted-client-id", request.entities.client_id)

        span_ctx = self.tracer.start_as_current_span("alogram.check_risk") if self.tracer else None

        try:
            with span_ctx or open("/dev/null", "w"):
                if span_ctx:
                    span = trace.get_current_span()
                    span.set_attribute("alogram.idempotency_key", ik)
                    span.set_attribute("alogram.trace_id", tid)

                if self.configuration.debug:
                    import json

                    payload_dict = self._to_json_friendly_dict(request)
                    scrubbed = self._scrub_payload(payload_dict)
                    log.debug(f"DEBUG: SDK sending payload: {json.dumps(scrubbed, indent=2)}")

                # In 0.2.5, /v1/risk/check is part of RiskScoringApi
                result = self.risk_scoring.risk_check(
                    check_request=request,
                    x_idempotency_key=ik,
                    x_trace_id=tid,
                )
                if span_ctx:
                    trace.get_current_span().set_attribute("alogram.decision", result.decision)
                return result
        except ApiException as e:
            mapped_exc = self._map_exception(e)
            raise mapped_exc

    def ingest_signals(self, request: SignalsRequest, **kwargs) -> None:
        """📡 Ingest behavioral signals."""
        ik = kwargs.get("idempotency_key") or self._generate_id("idk")
        tid = kwargs.get("trace_id") or self._generate_id("trc")

        span_ctx = self.tracer.start_as_current_span("alogram.ingest_signals") if self.tracer else None
        try:
            with span_ctx or open("/dev/null", "w"):
                if span_ctx:
                    span = trace.get_current_span()
                    span.set_attribute("alogram.idempotency_key", ik)
                    span.set_attribute("alogram.trace_id", tid)

                if self.configuration.debug:
                    import json

                    payload_dict = self._to_json_friendly_dict(request)
                    scrubbed = self._scrub_payload(payload_dict)
                    log.debug(f"DEBUG: SDK sending payload: {json.dumps(scrubbed, indent=2)}")

                # In 0.2.5, ingestion is part of SignalIntelligenceApi
                self.signals.ingest_signals(
                    signals_request=request,
                    x_idempotency_key=ik,
                    x_trace_id=tid,
                )
        except ApiException as e:
            raise self._map_exception(e)

    def ingest_event(self, event: PaymentEvent, **kwargs) -> None:
        """📡 Ingest payment lifecycle events."""
        ik = kwargs.get("idempotency_key") or self._generate_id("idk")
        tid = kwargs.get("trace_id") or self._generate_id("trc")

        span_ctx = self.tracer.start_as_current_span("alogram.ingest_event") if self.tracer else None
        try:
            with span_ctx or open("/dev/null", "w"):
                if span_ctx:
                    span = trace.get_current_span()
                    span.set_attribute("alogram.idempotency_key", ik)
                    span.set_attribute("alogram.trace_id", tid)

                if self.configuration.debug:
                    import json

                    payload_dict = self._to_json_friendly_dict(event)
                    scrubbed = self._scrub_payload(payload_dict)
                    log.debug(f"DEBUG: SDK sending payload: {json.dumps(scrubbed, indent=2)}")

                # In 0.2.5, ingestion is part of SignalIntelligenceApi
                self.signals.ingest_payment_event(
                    payment_event=event,
                    x_idempotency_key=ik,
                    x_trace_id=tid,
                )
        except ApiException as e:
            raise self._map_exception(e)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(initial=1, max=10, jitter=1),
        retry=retry_if_exception(is_retryable_error),
        reraise=True,
    )
    def get_fraud_scores(self, tenant_id: str, **kwargs) -> ScoresSuccessResponse:
        """🔍 Query historical risk assessments and scores."""
        tid = kwargs.get("trace_id") or self._generate_id("trc")

        try:
            return self.forensics.get_fraud_scores(
                tenant_id=tenant_id,
                start_time=kwargs.get("start_time"),
                end_time=kwargs.get("end_time"),
                x_trace_id=tid,
            )
        except ApiException as e:
            raise self._map_exception(e)


class AlogramPublicClient(AlogramBaseClient):
    """🌐 **AlogramPublicClient** (Public Client)

    Designed for client-side environments (Browsers, Mobile) using a Publishable Key (`pk_...`).
    Strictly restricted to non-sensitive ingestion methods.
    """

    def __init__(
        self,
        base_url: str = "https://api.alogram.ai",
        api_key: Optional[str] = None,
        access_token: Optional[str] = None,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        debug: bool = False,
    ):
        if api_key and api_key.startswith("sk_"):
            raise ScopedAccessError(
                "Cannot initialize AlogramPublicClient with a Secret Key (sk_...). "
                "Please use AlogramRiskClient for server-side operations."
            )
        super().__init__(
            base_url=base_url,
            api_key=api_key,
            access_token=access_token,
            tenant_id=tenant_id,
            client_id=client_id,
            debug=debug,
        )

    def ingest_signals(self, request: SignalsRequest, **kwargs) -> None:
        """📡 Ingest behavioral signals from the frontend."""
        ik = kwargs.get("idempotency_key") or self._generate_id("idk")
        tid = kwargs.get("trace_id") or self._generate_id("trc")

        span_ctx = self.tracer.start_as_current_span("alogram.ingest_signals") if self.tracer else None
        try:
            with span_ctx or open("/dev/null", "w"):
                if span_ctx:
                    span = trace.get_current_span()
                    span.set_attribute("alogram.idempotency_key", ik)
                    span.set_attribute("alogram.trace_id", tid)

                if self.configuration.debug:
                    import json

                    payload_dict = self._to_json_friendly_dict(request)
                    scrubbed = self._scrub_payload(payload_dict)
                    log.debug(f"DEBUG: SDK sending payload: {json.dumps(scrubbed, indent=2)}")

                # In 0.2.5, ingestion is part of SignalIntelligenceApi
                self.signals.ingest_signals(
                    signals_request=request,
                    x_idempotency_key=ik,
                    x_trace_id=tid,
                )
        except ApiException as e:
            raise self._map_exception(e)
