"""Perception — the input-gathering stage of the execution cycle.

Perception has no opinions and produces no effects. It answers exactly one
question: what is in front of the agent right now? If there is nothing, it says
so explicitly rather than inventing a value.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Iterator, Optional


@dataclass(frozen=True)
class Percept:
    """One observation. `empty` is explicit so that 'nothing' is never mistaken for 0."""

    cycle: int
    value: Any
    empty: bool

    @staticmethod
    def of(cycle: int, value: Any) -> "Percept":
        return Percept(cycle=cycle, value=value, empty=False)

    @staticmethod
    def nothing(cycle: int) -> "Percept":
        return Percept(cycle=cycle, value=None, empty=True)


class SequencePerception:
    """Perceives a finite sequence, one element per cycle, then perceives nothing.

    The source is exhausted honestly: once it runs out, every subsequent percept
    is marked empty. The loop uses that to decide it has no more work.
    """

    def __init__(self, source: Iterable[Any]):
        self._iterator: Iterator[Any] = iter(source)
        self._exhausted = False
        self._observed = 0

    @property
    def observed(self) -> int:
        return self._observed

    @property
    def exhausted(self) -> bool:
        return self._exhausted

    def perceive(self, cycle: int) -> Percept:
        if self._exhausted:
            return Percept.nothing(cycle)
        try:
            value = next(self._iterator)
        except StopIteration:
            self._exhausted = True
            return Percept.nothing(cycle)
        self._observed += 1
        return Percept.of(cycle, value)
