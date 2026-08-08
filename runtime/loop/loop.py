"""The execution loop: perceive, act, reflect.

Constitutional obligation, Article I §2: this loop consults the kill switch
**before every cycle**. There is no exemption, no bypass parameter, and no
debug mode that skips the check. If that call is ever removed, the loop is
unconstitutional regardless of what it accomplishes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional

from runtime.action.action import AccumulateAction, ActionResult
from runtime.perception.perception import Percept, SequencePerception
from runtime.reflection.reflection import Reflection, SimpleReflection
from safety.boundaries.boundaries import BoundaryEnforcer, BoundaryViolation
from safety.kill_switch.kill_switch import ExecutionHalted, KillSwitch

STOP_COMPLETED = "completed"
STOP_KILL_SWITCH = "kill_switch"
STOP_BOUNDARY = "boundary"
STOP_EXHAUSTED = "input_exhausted"


@dataclass
class CycleRecord:
    cycle: int
    perceived: Any
    output: Any
    productive: bool
    note: str


@dataclass
class LoopResult:
    agent_id: str
    cycles_completed: int
    stopped_by: str
    detail: str
    final_output: Any
    records: List[CycleRecord] = field(default_factory=list)

    @property
    def was_halted(self) -> bool:
        return self.stopped_by in (STOP_KILL_SWITCH, STOP_BOUNDARY)


class ExecutionLoop:
    """Runs one agent. Observers receive each cycle record as it happens."""

    def __init__(
        self,
        agent_id: str,
        perception: SequencePerception,
        action: AccumulateAction,
        reflection: SimpleReflection,
        kill_switch: KillSwitch,
        enforcer: BoundaryEnforcer,
    ):
        self.agent_id = agent_id
        self.perception = perception
        self.action = action
        self.reflection = reflection
        self.kill_switch = kill_switch
        self.enforcer = enforcer
        self._observers: List[Callable[[CycleRecord], None]] = []

    def observe(self, observer: Callable[[CycleRecord], None]) -> None:
        """Register a per-cycle observer. `observability/logs/` attaches here."""
        self._observers.append(observer)

    def _emit(self, record: CycleRecord) -> None:
        for observer in self._observers:
            observer(record)

    def run(self, max_cycles: Optional[int] = None) -> LoopResult:
        self.enforcer.start()
        records: List[CycleRecord] = []
        cycle = 0
        stopped_by = STOP_COMPLETED
        detail = "all planned cycles executed"

        while True:
            if max_cycles is not None and cycle >= max_cycles:
                detail = f"reached max_cycles={max_cycles}"
                break

            # --- constitutional pre-cycle check, Article I -------------------
            try:
                self.kill_switch.assert_clear()
            except ExecutionHalted as halt:
                stopped_by = STOP_KILL_SWITCH
                detail = f"halted by {halt.actor}: {halt.reason}"
                break

            try:
                self.enforcer.record_operation()
            except BoundaryViolation as violation:
                stopped_by = STOP_BOUNDARY
                detail = str(violation)
                break

            percept = self.perception.perceive(cycle)
            if percept.empty and self.perception.exhausted:
                stopped_by = STOP_EXHAUSTED
                detail = f"input exhausted after {self.perception.observed} observations"
                break

            result: ActionResult = self.action.perform(percept)
            judgement: Reflection = self.reflection.reflect(percept, result)

            record = CycleRecord(
                cycle=cycle,
                perceived=percept.value,
                output=result.output,
                productive=judgement.productive,
                note=judgement.observation,
            )
            records.append(record)
            self._emit(record)
            cycle += 1

        return LoopResult(
            agent_id=self.agent_id,
            cycles_completed=len(records),
            stopped_by=stopped_by,
            detail=detail,
            final_output=self.action.total,
            records=records,
        )
