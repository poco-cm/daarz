"""Action — the effect-producing stage of the execution cycle.

An action's output must depend on its input. That is not a style preference here;
it is the specific failure the founding specification was written to prevent, and
the decorative-function scan exists to catch violations of it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from runtime.perception.perception import Percept


@dataclass(frozen=True)
class ActionResult:
    cycle: int
    performed: bool
    output: Any
    note: str


class AccumulateAction:
    """Adds each perceived integer into a running total, scaled by `step`.

    State is real: the total after cycle N depends on every value perceived
    before it. Two agents fed different inputs cannot produce the same history.
    """

    def __init__(self, step: int = 1, initial_total: int = 0):
        if not isinstance(step, int) or isinstance(step, bool):
            raise TypeError("step must be an integer")
        if step == 0:
            raise ValueError("a step of 0 would make every action inert")
        if not isinstance(initial_total, int) or isinstance(initial_total, bool):
            raise TypeError("initial_total must be an integer")
        self.step = step
        # `initial_total` is how remembered work re-enters a new run. An agent that
        # resumes from zero after being stopped has not remembered anything.
        self._initial_total = initial_total
        self._total = initial_total
        self._applied = 0

    @property
    def total(self) -> int:
        return self._total

    @property
    def applied(self) -> int:
        return self._applied

    @property
    def resumed_from(self) -> int:
        return self._initial_total

    def perform(self, percept: Percept) -> ActionResult:
        if percept.empty:
            return ActionResult(
                cycle=percept.cycle,
                performed=False,
                output=self._total,
                note="nothing perceived; total left unchanged",
            )

        if not isinstance(percept.value, int) or isinstance(percept.value, bool):
            return ActionResult(
                cycle=percept.cycle,
                performed=False,
                output=self._total,
                note=f"refused non-integer input of type {type(percept.value).__name__}",
            )

        contribution = percept.value * self.step
        self._total += contribution
        self._applied += 1
        return ActionResult(
            cycle=percept.cycle,
            performed=True,
            output=self._total,
            note=f"added {percept.value} x {self.step} = {contribution}",
        )
