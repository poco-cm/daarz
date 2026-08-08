"""The one inter-institution message defined in the Formation phase.

Order 2 phase 4 asks for a single real message schema in
`protocols/institution/requests/` — one that is actually sent between two
activated institutions, not a data class nobody constructs.

Design constraints taken from the specification:

- §4 places institution-to-institution requests in this leaf, so this is where the
  schema lives, not inside either institution.
- An institution that is not activated has no address. Sending to it, or claiming
  to send from it, is refused at construction time rather than at delivery time.
- Every request carries an explicit `authorised_by`. Article II's prohibition on
  agents authorising creation is meaningless if an agent can ask an institution to
  do the creating.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from institutions.runtime.activation import ActivationError, require_activated

ACTION_REMEMBER = "remember"
ACTION_RECALL = "recall"
ACTION_BUILD_AGENT = "build_agent"
ACTION_HALT = "halt"

KNOWN_ACTIONS = (ACTION_REMEMBER, ACTION_RECALL, ACTION_BUILD_AGENT, ACTION_HALT)

#: Which activated institution is permitted to serve which action. An action with
#: no handler is not a feature; it is a promise nobody kept.
ACTION_OWNER: Dict[str, str] = {
    ACTION_REMEMBER: "memory",
    ACTION_RECALL: "memory",
    ACTION_BUILD_AGENT: "factory",
    ACTION_HALT: "safety",
}


class ProtocolError(RuntimeError):
    """Raised when a message violates the protocol."""


@dataclass(frozen=True)
class InstitutionRequest:
    sender: str
    recipient: str
    action: str
    payload: Dict[str, Any]
    authorised_by: str
    request_id: str = field(default_factory=lambda: f"REQ-{uuid.uuid4().hex[:12]}")
    sent_at: float = field(default_factory=time.time)

    def __post_init__(self):
        for role, name in (("sender", self.sender), ("recipient", self.recipient)):
            try:
                require_activated(name)
            except ActivationError as error:
                raise ProtocolError(f"{role}: {error}") from error

        if self.sender == self.recipient:
            raise ProtocolError(
                "an institution does not send itself a protocol request; call it directly"
            )
        if self.action not in KNOWN_ACTIONS:
            raise ProtocolError(f"unknown action '{self.action}'; known: {list(KNOWN_ACTIONS)}")
        if ACTION_OWNER[self.action] != self.recipient:
            raise ProtocolError(
                f"action '{self.action}' is served by '{ACTION_OWNER[self.action]}', "
                f"not by '{self.recipient}'"
            )
        if not isinstance(self.payload, dict):
            raise ProtocolError("payload must be a mapping")
        if not self.authorised_by.strip():
            raise ProtocolError("every request must name who authorised it")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "action": self.action,
            "payload": dict(self.payload),
            "authorised_by": self.authorised_by,
            "sent_at": self.sent_at,
        }


@dataclass(frozen=True)
class InstitutionResponse:
    request_id: str
    responder: str
    accepted: bool
    result: Any
    reason: str
    responded_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "responder": self.responder,
            "accepted": self.accepted,
            "result": self.result,
            "reason": self.reason,
            "responded_at": self.responded_at,
        }


class RequestBus:
    """Routes requests to the institution that owns the action, and records the traffic."""

    def __init__(self):
        self._handlers: Dict[str, Callable[[InstitutionRequest], InstitutionResponse]] = {}
        self._traffic: List[Dict[str, Any]] = []

    def register_handler(
        self, institution: str, handler: Callable[[InstitutionRequest], InstitutionResponse]
    ) -> None:
        require_activated(institution)
        self._handlers[institution] = handler

    def traffic(self) -> List[Dict[str, Any]]:
        return list(self._traffic)

    def send(self, request: InstitutionRequest) -> InstitutionResponse:
        handler = self._handlers.get(request.recipient)
        if handler is None:
            raise ProtocolError(
                f"institution '{request.recipient}' is activated but has registered "
                f"no handler; the address exists and nobody is at it"
            )
        response = handler(request)
        self._traffic.append(
            {"request": request.to_dict(), "response": response.to_dict()}
        )
        return response
