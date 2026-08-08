"""The sole creation path for agents.

Constitutional basis: `constitution/articles/ARTICLE-002-no-self-replication.md`.
Agents come into existence here and nowhere else. `factory/` may create agents
because it is an institution, not an agent.

The factory produces a runnable object from a validated specification. It does
not run it. Creation and execution are kept apart so that authority over one is
not implicitly authority over the other.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from agents.registry.registry import AgentRegistry
from factory.schemas.agent_spec import KIND_ACCUMULATOR, AgentSpec, SpecificationError
from runtime.action.action import AccumulateAction
from runtime.loop.loop import ExecutionLoop
from runtime.perception.perception import SequencePerception
from runtime.reflection.reflection import SimpleReflection
from safety.boundaries.boundaries import Boundaries, BoundaryEnforcer
from safety.kill_switch.kill_switch import KillSwitch


class ConstructionError(RuntimeError):
    """Raised when a specification is valid but cannot be built in this phase."""


@dataclass
class BuiltAgent:
    """A real, runnable agent. Holds its own loop, bound to its own safety limits."""

    spec: AgentSpec
    loop: ExecutionLoop

    @property
    def agent_id(self) -> str:
        return self.spec.agent_id

    def run(self, max_cycles: Optional[int] = None):
        return self.loop.run(max_cycles=max_cycles)


class AgentFactory:
    """Builds agents from specifications, and registers them durably."""

    def __init__(self, registry: AgentRegistry, kill_switch: KillSwitch):
        self.registry = registry
        self.kill_switch = kill_switch

    def build(self, spec: AgentSpec, inputs: Iterable) -> BuiltAgent:
        if spec.kind != KIND_ACCUMULATOR:
            raise ConstructionError(
                f"kind '{spec.kind}' has no construction path in the Birth phase"
            )

        boundaries = Boundaries(
            max_operations=spec.max_operations,
            max_duration_seconds=spec.max_duration_seconds,
        )
        loop = ExecutionLoop(
            agent_id=spec.agent_id,
            perception=SequencePerception(inputs),
            action=AccumulateAction(step=int(spec.parameters.get("step", 1))),
            reflection=SimpleReflection(),
            kill_switch=self.kill_switch,
            enforcer=BoundaryEnforcer(boundaries),
        )
        return BuiltAgent(spec=spec, loop=loop)

    def create_and_register(self, spec: AgentSpec, inputs: Iterable) -> BuiltAgent:
        """Build an agent and enter it in the civil registry, in that order.

        If construction fails, nothing is registered — the registry never holds
        a record for an agent that does not exist.
        """
        agent = self.build(spec, inputs)
        self.registry.register(spec)
        return agent
