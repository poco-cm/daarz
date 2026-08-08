"""The sole creation path for agents.

Constitutional basis: `constitution/articles/ARTICLE-002-no-self-replication.md`.
Agents come into existence here and nowhere else. `factory/` may create agents
because it is an institution, not an agent.

The factory produces a runnable object from a validated specification. It does
not run it. Creation and execution are kept apart so that authority over one is
not implicitly authority over the other.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable, Optional

from agents.registry.registry import AgentRegistry
from factory.schemas.agent_spec import KIND_ACCUMULATOR, AgentSpec, SpecificationError
from memory.runtime.memory import InstitutionalMemory, MemoryWriter
from observability.alerts.alerts import AlertBus, BoundaryBreachAlert
from observability.logs.execution_log import ExecutionLog
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
    log: Optional[ExecutionLog] = None
    memory_writer: Optional[MemoryWriter] = None
    resumed_from: int = 0

    @property
    def agent_id(self) -> str:
        return self.spec.agent_id

    def run(self, max_cycles: Optional[int] = None):
        result = self.loop.run(max_cycles=max_cycles)
        if self.log is not None:
            self.log.record_run_end(result)
        if self.memory_writer is not None:
            self.memory_writer.remember_run_end(result)
        return result


class AgentFactory:
    """Builds agents from specifications, and registers them durably."""

    def __init__(
        self,
        registry: AgentRegistry,
        kill_switch: KillSwitch,
        log_dir: Optional[str] = None,
        alert_bus: Optional[AlertBus] = None,
        memory: Optional[InstitutionalMemory] = None,
    ):
        self.registry = registry
        self.kill_switch = kill_switch
        self.log_dir = log_dir
        self.alert_bus = alert_bus
        self.memory = memory

    def build(self, spec: AgentSpec, inputs: Iterable) -> BuiltAgent:
        if spec.kind != KIND_ACCUMULATOR:
            raise ConstructionError(
                f"kind '{spec.kind}' has no construction path in the Birth phase"
            )

        boundaries = Boundaries(
            max_operations=spec.max_operations,
            max_duration_seconds=spec.max_duration_seconds,
        )
        # Formation phase: the factory consults `memory` before building. An agent
        # that was stopped mid-run resumes from what the civilization remembers of
        # it, rather than starting again from nothing.
        resumed_from = 0
        if self.memory is not None:
            remembered = self.memory.recall(spec.agent_id, "running_total", default=0)
            if isinstance(remembered, int) and not isinstance(remembered, bool):
                resumed_from = remembered

        enforcer = BoundaryEnforcer(boundaries)
        loop = ExecutionLoop(
            agent_id=spec.agent_id,
            perception=SequencePerception(inputs),
            action=AccumulateAction(
                step=int(spec.parameters.get("step", 1)), initial_total=resumed_from
            ),
            reflection=SimpleReflection(),
            kill_switch=self.kill_switch,
            enforcer=enforcer,
        )

        # Observability is wired at construction, so an agent cannot be built
        # unobserved and then quietly run.
        log = None
        if self.log_dir is not None:
            log = ExecutionLog(
                os.path.join(self.log_dir, f"{spec.agent_id}.jsonl"), spec.agent_id
            )
            loop.observe(log.record_cycle)
            enforcer.on_violation(log.record_violation)
        if self.alert_bus is not None:
            enforcer.on_violation(BoundaryBreachAlert(self.alert_bus, spec.agent_id))

        memory_writer = None
        if self.memory is not None:
            memory_writer = MemoryWriter(self.memory, spec.agent_id, every=100)
            loop.observe(memory_writer)

        return BuiltAgent(
            spec=spec,
            loop=loop,
            log=log,
            memory_writer=memory_writer,
            resumed_from=resumed_from,
        )

    def create_and_register(self, spec: AgentSpec, inputs: Iterable) -> BuiltAgent:
        """Build an agent and enter it in the civil registry, in that order.

        If construction fails, nothing is registered — the registry never holds
        a record for an agent that does not exist.
        """
        agent = self.build(spec, inputs)
        self.registry.register(spec)
        return agent

    def rebuild_registered(self, spec: AgentSpec, inputs: Iterable) -> BuiltAgent:
        """Rebuild an agent that is already in the civil registry.

        Used when an agent was stopped and is to run again. Registration is not
        repeated — an agent is registered once — but the build path is identical,
        so the rebuilt agent picks up whatever `memory` holds for it.
        """
        if self.registry.get(spec.agent_id) is None:
            raise ConstructionError(
                f"agent '{spec.agent_id}' is not registered; use create_and_register"
            )
        return self.build(spec, inputs)
