"""Memory's protocol address: how other institutions reach it.

Memory serves `remember` and `recall`, and nothing else. A request for any other
action is refused with a stated reason rather than silently ignored, because an
institution that ignores messages is indistinguishable from one that is broken.
"""

from __future__ import annotations

from memory.runtime.memory import InstitutionalMemory
from protocols.institution.requests.request import (
    ACTION_RECALL,
    ACTION_REMEMBER,
    InstitutionRequest,
    InstitutionResponse,
)

INSTITUTION = "memory"


class MemoryService:
    def __init__(self, memory: InstitutionalMemory):
        self.memory = memory
        self.served = 0
        self.refused = 0

    def _refuse(self, request: InstitutionRequest, reason: str) -> InstitutionResponse:
        self.refused += 1
        return InstitutionResponse(
            request_id=request.request_id,
            responder=INSTITUTION,
            accepted=False,
            result=None,
            reason=reason,
        )

    def __call__(self, request: InstitutionRequest) -> InstitutionResponse:
        if request.action == ACTION_REMEMBER:
            missing = [f for f in ("subject", "key", "value") if f not in request.payload]
            if missing:
                return self._refuse(request, f"remember requires {missing}")
            self.memory.remember(
                subject=request.payload["subject"],
                key=request.payload["key"],
                value=request.payload["value"],
                written_by=f"{request.sender} via {request.request_id}",
            )
            self.served += 1
            return InstitutionResponse(
                request_id=request.request_id,
                responder=INSTITUTION,
                accepted=True,
                result={"written": True, "total_writes": self.memory.write_count()},
                reason="recorded",
            )

        if request.action == ACTION_RECALL:
            missing = [f for f in ("subject", "key") if f not in request.payload]
            if missing:
                return self._refuse(request, f"recall requires {missing}")
            value = self.memory.recall(request.payload["subject"], request.payload["key"])
            self.served += 1
            return InstitutionResponse(
                request_id=request.request_id,
                responder=INSTITUTION,
                accepted=True,
                result={"value": value, "known": value is not None},
                reason="recalled" if value is not None else "nothing remembered under that key",
            )

        return self._refuse(
            request, f"'{request.action}' is not served by {INSTITUTION}"
        )
