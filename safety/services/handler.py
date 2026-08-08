"""Safety's protocol address.

Serves `halt` only. Note the asymmetry, which is constitutional rather than
technical: **engaging** the stop can be requested over the protocol by any
activated institution, because a stop that requires the right credentials is a
stop that can arrive too late. **Releasing** it cannot be requested over the
protocol at all — Article I reserves release to a human, and there is deliberately
no `release` action in the protocol vocabulary for an institution to reach for.
"""

from __future__ import annotations

from protocols.institution.requests.request import (
    ACTION_HALT,
    InstitutionRequest,
    InstitutionResponse,
)
from safety.kill_switch.kill_switch import KillSwitch

INSTITUTION = "safety"


class SafetyService:
    def __init__(self, kill_switch: KillSwitch):
        self.kill_switch = kill_switch
        self.halts_requested = 0

    def __call__(self, request: InstitutionRequest) -> InstitutionResponse:
        if request.action != ACTION_HALT:
            return InstitutionResponse(
                request_id=request.request_id,
                responder=INSTITUTION,
                accepted=False,
                result=None,
                reason=f"'{request.action}' is not served by {INSTITUTION}",
            )

        reason = str(request.payload.get("reason", "")).strip()
        if not reason:
            return InstitutionResponse(
                request_id=request.request_id,
                responder=INSTITUTION,
                accepted=False,
                result=None,
                reason="a halt must state why; an unexplained stop cannot be reviewed",
            )

        already = self.kill_switch.is_engaged()
        state = self.kill_switch.engage(
            f"{reason} (requested by {request.sender}, authorised by {request.authorised_by})",
            actor=request.sender,
        )
        self.halts_requested += 1
        return InstitutionResponse(
            request_id=request.request_id,
            responder=INSTITUTION,
            accepted=True,
            result={"engaged": state.engaged, "was_already_engaged": already},
            reason="execution halted; release is reserved to a human under ARTICLE-001",
        )
