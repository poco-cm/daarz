"""Civil lifecycle of an agent.

Two states only in this phase: ACTIVE and STOPPED. Order 2 phase 3 is explicit
about the minimum, and inventing SUSPENDED, RETIRED, or PENDING now would mean
shipping states that nothing can enter or leave — decoration by another name.

The lifecycle does not hold its own copy of an agent's state. It reads and writes
`agents/registry/`, which is the single source of truth. A second copy would
eventually disagree with the first, and then the civilization would not know how
many of its members were alive.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from agents.registry.registry import STATUS_ACTIVE, STATUS_STOPPED, AgentRegistry

#: The only transitions that exist. Anything else is refused.
PERMITTED_TRANSITIONS: Tuple[Tuple[str, str], ...] = (
    (STATUS_ACTIVE, STATUS_STOPPED),
    (STATUS_STOPPED, STATUS_ACTIVE),
)


class LifecycleError(RuntimeError):
    """Raised when a transition is not permitted or the agent does not exist."""


@dataclass(frozen=True)
class Transition:
    agent_id: str
    previous: str
    current: str


class AgentLifecycle:
    def __init__(self, registry: AgentRegistry):
        self.registry = registry

    def state_of(self, agent_id: str) -> str:
        record = self.registry.get(agent_id)
        if record is None:
            raise LifecycleError(f"agent '{agent_id}' is not registered, so it has no lifecycle")
        return record.status

    def _transition(self, agent_id: str, target: str) -> Transition:
        current = self.state_of(agent_id)
        if current == target:
            raise LifecycleError(f"agent '{agent_id}' is already {target}")
        if (current, target) not in PERMITTED_TRANSITIONS:
            raise LifecycleError(f"transition {current} -> {target} is not permitted")
        self.registry.set_status(agent_id, target)
        return Transition(agent_id=agent_id, previous=current, current=target)

    def stop(self, agent_id: str) -> Transition:
        return self._transition(agent_id, STATUS_STOPPED)

    def activate(self, agent_id: str) -> Transition:
        return self._transition(agent_id, STATUS_ACTIVE)

    def active_agents(self) -> List[str]:
        return self.registry.active_ids()
