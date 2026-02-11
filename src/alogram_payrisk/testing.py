# Copyright (c) 2025 Alogram Inc.
# All rights reserved.

import datetime
import uuid
import time
from typing import Any, Dict, List, Optional, Union

from alogram_payrisk._generated.payrisk_v1.models.decision_response import DecisionResponse
from alogram_payrisk._generated.payrisk_v1.models.fraud_score import FraudScore
from alogram_payrisk._generated.payrisk_v1.models.risk_level_enum import RiskLevelEnum
from alogram_payrisk._generated.payrisk_v1.models.reason_detail import ReasonDetail

from alogram_payrisk._generated.payrisk_v1.models.risk_category_enum import RiskCategoryEnum

class MockRiskClient:
    """
    🛠️ **MockRiskClient**
    
    A zero-dependency mock implementation of the Alogram Risk Client for local testing.
    """

    def __init__(self, default_decision: str = "approve", default_score: float = 0.1):
        self._calls: List[Dict[str, Any]] = []
        self._queued_responses: List[Union[DecisionResponse, Exception]] = []
        self._default_decision = default_decision
        self._default_score = default_score
        self._delay: float = 0

    def set_default_decision(self, decision: str, score: float = 0.1):
        self._default_decision = decision
        self._default_score = score

    def _get_timestamp(self) -> str:
        return datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")

    def queue_decision(self, decision: str, score: float = 0.1, reason: Optional[str] = None):
        """Queue a specific decision response for the next call."""
        # Map score to risk level roughly for the mock
        risk_level = RiskLevelEnum.LOW
        if score > 0.8:
            risk_level = RiskLevelEnum.HIGH
        elif score > 0.4:
            risk_level = RiskLevelEnum.MEDIUM

        resp = DecisionResponse(
            assessmentId=f"mock-{uuid.uuid4().hex[:12]}",
            decision=decision.lower(),
            decisionAt=self._get_timestamp(),
            fraudScore=FraudScore(
                riskLevel=risk_level,
                score=score,
                explanation="Mocked response"
            ),
            riskScore=score
        )
        if reason:
            resp.reasons = [ReasonDetail(
                code="MOCK_CODE",
                category=RiskCategoryEnum.BEHAVIOR,
                displayName="Mock Reason",
                description=reason
            )]
        self._queued_responses.append(resp)

    def queue_error(self, exception: Exception):
        """Queue an exception to be raised on the next call."""
        self._queued_responses.append(exception)

    def set_delay(self, seconds: float):
        """Simulate network latency."""
        self._delay = seconds

    @property
    def call_count(self) -> int:
        return len(self._calls)

    @property
    def calls(self) -> List[Dict[str, Any]]:
        return self._calls

    def _handle_call(self, method: str, request: Any):
        self._calls.append({"method": method, "request": request, "timestamp": time.time()})
        
        if self._delay > 0:
            time.sleep(self._delay)

        if self._queued_responses:
            item = self._queued_responses.pop(0)
            if isinstance(item, Exception):
                raise item
            return item
        return None

    def check_risk(self, request: Any, idempotency_key: Optional[str] = None, tenant_id: Optional[str] = None) -> DecisionResponse:
        res = self._handle_call("check_risk", request)
        if res:
            return res
        
        # Default response
        risk_level = RiskLevelEnum.LOW
        if self._default_score > 0.8:
            risk_level = RiskLevelEnum.HIGH
        
        return DecisionResponse(
            assessmentId=f"mock-{uuid.uuid4().hex[:12]}",
            decision=self._default_decision.lower(),
            decisionAt=self._get_timestamp(),
            fraudScore=FraudScore(
                riskLevel=risk_level,
                score=self._default_score
            ),
            riskScore=self._default_score,
            reasons=[ReasonDetail(
                code="DEFAULT",
                category=RiskCategoryEnum.BEHAVIOR,
                displayName="Default",
                description="default_mock_response"
            )]
        )

    def ingest_signals(self, request: Any, idempotency_key: Optional[str] = None, tenant_id: Optional[str] = None) -> None:
        self._handle_call("ingest_signals", request)

    def ingest_event(self, event: Any, idempotency_key: Optional[str] = None, tenant_id: Optional[str] = None) -> None:
        self._handle_call("ingest_event", event)