"""Reflection — the post-cycle review stage.

Reflection does not act. It looks at what just happened and produces a judgement
that later stages, and later phases, can use. In phase 4 this output becomes the
experience written into `memory/`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from runtime.action.action import ActionResult
from runtime.perception.perception import Percept


@dataclass(frozen=True)
class Reflection:
    cycle: int
    productive: bool
    observation: str
    delta: Any


class SimpleReflection:
    """Judges each cycle against the one before it.

    'Productive' means the cycle changed the world state. A cycle that perceived
    nothing, or refused its input, is honestly recorded as unproductive rather
    than being counted as work.
    """

    def __init__(self):
        self._previous_output: Any = None
        self._productive_cycles = 0
        self._idle_cycles = 0

    @property
    def productive_cycles(self) -> int:
        return self._productive_cycles

    @property
    def idle_cycles(self) -> int:
        return self._idle_cycles

    def reflect(self, percept: Percept, result: ActionResult) -> Reflection:
        changed = result.performed and result.output != self._previous_output

        if changed:
            self._productive_cycles += 1
            delta = result.output if self._previous_output is None else (
                result.output - self._previous_output
                if isinstance(result.output, int) and isinstance(self._previous_output, int)
                else result.output
            )
            observation = f"cycle {result.cycle} changed state: {result.note}"
        else:
            self._idle_cycles += 1
            delta = 0
            observation = f"cycle {result.cycle} produced no change: {result.note}"

        self._previous_output = result.output
        return Reflection(
            cycle=result.cycle,
            productive=changed,
            observation=observation,
            delta=delta,
        )

    def summary(self) -> Dict[str, int]:
        return {
            "productive_cycles": self._productive_cycles,
            "idle_cycles": self._idle_cycles,
        }
