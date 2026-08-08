"""The census: how many members this civilization actually has, right now.

Order 2 phase 3 step 1 requires a live query against `agents/registry/`, never a
stored number. A cached count is a number that was true once. This class holds no
count of its own; every call reads the registry.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, List

from agents.registry.registry import STATUS_ACTIVE, STATUS_STOPPED, AgentRegistry


@dataclass(frozen=True)
class CensusSnapshot:
    """A count with a timestamp, because a count without one is a claim about nothing."""

    taken_at: float
    active: int
    stopped: int
    total: int
    active_ids: List[str]

    def as_dict(self) -> Dict[str, object]:
        return {
            "taken_at": self.taken_at,
            "active": self.active,
            "stopped": self.stopped,
            "total": self.total,
            "active_ids": list(self.active_ids),
        }


class PopulationCensus:
    def __init__(self, registry: AgentRegistry):
        self.registry = registry

    def take(self) -> CensusSnapshot:
        records = self.registry.all_records()
        active = [r for r in records if r.status == STATUS_ACTIVE]
        stopped = [r for r in records if r.status == STATUS_STOPPED]
        return CensusSnapshot(
            taken_at=time.time(),
            active=len(active),
            stopped=len(stopped),
            total=len(records),
            active_ids=sorted(r.agent_id for r in active),
        )

    def active_count(self) -> int:
        return self.take().active

    def by_kind(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for record in self.registry.all_records():
            if record.status == STATUS_ACTIVE:
                counts[record.kind] = counts.get(record.kind, 0) + 1
        return counts
