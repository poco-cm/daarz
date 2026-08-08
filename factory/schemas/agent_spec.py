"""The single agent schema permitted in the Birth phase.

Order 2 phase 2 step 1: define exactly one agent kind. Not several. A civilization
that cannot run one agent correctly gains nothing from being able to describe five.

The schema is a *specification*, not an agent. It carries no behaviour of its own;
`factory/runtime/` turns it into something that runs.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List

AGENT_ID_PATTERN = re.compile(r"^[a-z][a-z0-9\-]{2,63}$")

#: The only agent kind that exists in the Birth phase.
KIND_ACCUMULATOR = "accumulator"

SUPPORTED_KINDS = (KIND_ACCUMULATOR,)


class SpecificationError(ValueError):
    """Raised when an agent specification is not fit to be built from."""


@dataclass(frozen=True)
class AgentSpec:
    """A validated description of an agent that does not exist yet.

    Fields:
        agent_id     stable civil identity, unique across the registry
        kind         must be one of SUPPORTED_KINDS
        purpose      one sentence stating the single problem this agent handles
        authorised_by  who authorised creation. Article II forbids agent authorship.
        max_operations  hard operation ceiling for any single run
        max_duration_seconds  hard wall-clock ceiling for any single run
        parameters   kind-specific settings, validated per kind
    """

    agent_id: str
    kind: str
    purpose: str
    authorised_by: str
    max_operations: int
    max_duration_seconds: float
    parameters: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        errors: List[str] = []

        if not AGENT_ID_PATTERN.match(self.agent_id or ""):
            errors.append(
                f"agent_id '{self.agent_id}' must be lowercase alphanumeric with hyphens, 3-64 chars"
            )

        if self.kind not in SUPPORTED_KINDS:
            errors.append(f"kind '{self.kind}' is not supported; permitted kinds: {SUPPORTED_KINDS}")

        if not (self.purpose or "").strip():
            errors.append("purpose must state, in one sentence, the single problem this agent handles")

        actor = (self.authorised_by or "").strip()
        if not actor:
            errors.append("authorised_by is required; an unauthorised agent is unconstitutional")
        elif actor.startswith("agent:"):
            errors.append(
                "an agent may not authorise the creation of an agent "
                "(constitution/articles/ARTICLE-002-no-self-replication.md)"
            )

        if self.max_operations <= 0:
            errors.append("max_operations must be positive")
        if self.max_duration_seconds <= 0:
            errors.append("max_duration_seconds must be positive")

        errors.extend(self._validate_parameters())

        if errors:
            raise SpecificationError("; ".join(errors))

    def _validate_parameters(self) -> List[str]:
        problems: List[str] = []
        if self.kind == KIND_ACCUMULATOR:
            step = self.parameters.get("step", 1)
            if not isinstance(step, int) or isinstance(step, bool):
                problems.append("accumulator parameter 'step' must be an integer")
            elif step == 0:
                problems.append("accumulator parameter 'step' of 0 would make the agent inert")
        return problems

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "kind": self.kind,
            "purpose": self.purpose,
            "authorised_by": self.authorised_by,
            "max_operations": self.max_operations,
            "max_duration_seconds": self.max_duration_seconds,
            "parameters": dict(self.parameters),
        }

    @staticmethod
    def from_dict(raw: Dict[str, Any]) -> "AgentSpec":
        missing = [
            k for k in ("agent_id", "kind", "purpose", "authorised_by",
                        "max_operations", "max_duration_seconds")
            if k not in raw
        ]
        if missing:
            raise SpecificationError(f"specification is missing required fields: {missing}")
        return AgentSpec(
            agent_id=raw["agent_id"],
            kind=raw["kind"],
            purpose=raw["purpose"],
            authorised_by=raw["authorised_by"],
            max_operations=int(raw["max_operations"]),
            max_duration_seconds=float(raw["max_duration_seconds"]),
            parameters=dict(raw.get("parameters", {})),
        )
