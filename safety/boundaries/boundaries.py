"""Enforceable execution limits.

Spec §8 and Order 2 phase 1 both require these to be *enforced*, not documented.
A boundary that only appears in a README is a boundary that does not exist.

Two limits are enforced in this phase: a maximum number of operations, and a
maximum wall-clock duration. Both are checked from inside the execution path,
so a runaway loop hits them rather than being politely asked to stop.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, List, Optional


class BoundaryViolation(RuntimeError):
    """Raised when an execution exceeds a declared limit."""

    def __init__(self, limit_name: str, limit_value: float, observed: float):
        self.limit_name = limit_name
        self.limit_value = limit_value
        self.observed = observed
        super().__init__(
            f"boundary '{limit_name}' exceeded: limit={limit_value}, observed={observed}"
        )


@dataclass(frozen=True)
class Boundaries:
    max_operations: int
    max_duration_seconds: float

    def __post_init__(self):
        if self.max_operations <= 0:
            raise ValueError("max_operations must be positive")
        if self.max_duration_seconds <= 0:
            raise ValueError("max_duration_seconds must be positive")


class BoundaryEnforcer:
    """Tracks a single execution against its declared boundaries.

    Observers registered via `on_violation` are notified before the exception
    propagates. `observability/alerts/` uses this hook; the enforcer itself
    knows nothing about alerting.
    """

    def __init__(self, boundaries: Boundaries, clock: Callable[[], float] = time.monotonic):
        self.boundaries = boundaries
        self._clock = clock
        self._started_at: Optional[float] = None
        self._operations = 0
        self._observers: List[Callable[[BoundaryViolation], None]] = []

    def on_violation(self, observer: Callable[[BoundaryViolation], None]) -> None:
        self._observers.append(observer)

    def start(self) -> None:
        self._started_at = self._clock()
        self._operations = 0

    @property
    def operations(self) -> int:
        return self._operations

    def elapsed(self) -> float:
        if self._started_at is None:
            return 0.0
        return self._clock() - self._started_at

    def remaining_operations(self) -> int:
        return max(0, self.boundaries.max_operations - self._operations)

    def _raise(self, name: str, limit: float, observed: float) -> None:
        violation = BoundaryViolation(name, limit, observed)
        for observer in self._observers:
            observer(violation)
        raise violation

    def record_operation(self) -> int:
        """Count one operation and enforce both limits. Call once per cycle."""
        if self._started_at is None:
            raise RuntimeError("BoundaryEnforcer.start() must be called before recording")

        self._operations += 1

        if self._operations > self.boundaries.max_operations:
            self._raise("max_operations", self.boundaries.max_operations, self._operations)

        elapsed = self.elapsed()
        if elapsed > self.boundaries.max_duration_seconds:
            self._raise("max_duration_seconds", self.boundaries.max_duration_seconds, elapsed)

        return self._operations
