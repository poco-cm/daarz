"""Institutional memory — the third institution activated in the Formation phase.

Memory is not logging. `observability/logs/` records what happened for humans to
read afterwards; memory holds what the civilization can *act on later*. The
difference is testable, and it is tested: an agent stopped mid-run and rebuilt
resumes from its remembered total rather than from zero. If memory were
decorative, that number would come back as 0.

Authority, deliberately narrow: memory may read and write records. It may not
create agents, run them, or stop them.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


class MemoryError_(RuntimeError):
    """Raised when a memory operation is not permitted or the record is malformed."""


@dataclass(frozen=True)
class MemoryRecord:
    subject: str
    key: str
    value: Any
    written_at: float
    written_by: str


class InstitutionalMemory:
    """Durable key-value memory, scoped per subject, with full write history retained."""

    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(os.path.abspath(self.path)), exist_ok=True)

    # -- storage -----------------------------------------------------------

    def _read_all(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.path):
            nothing_remembered: List[Dict[str, Any]] = []
            return nothing_remembered
        with open(self.path, "r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]

    # -- institutional operations -----------------------------------------

    def remember(self, subject: str, key: str, value: Any, written_by: str) -> MemoryRecord:
        if not subject.strip() or not key.strip():
            raise MemoryError_("a memory needs both a subject and a key")
        if not written_by.strip():
            raise MemoryError_("every memory must record who wrote it")
        record = MemoryRecord(
            subject=subject, key=key, value=value, written_at=time.time(), written_by=written_by
        )
        with open(self.path, "a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    {
                        "subject": record.subject,
                        "key": record.key,
                        "value": record.value,
                        "written_at": record.written_at,
                        "written_by": record.written_by,
                    },
                    sort_keys=True,
                )
                + "\n"
            )
        return record

    def recall(self, subject: str, key: str, default: Any = None) -> Any:
        """Return the most recent value written for this subject and key."""
        latest = None
        for raw in self._read_all():
            if raw["subject"] == subject and raw["key"] == key:
                latest = raw
        if latest is None:
            return default
        return latest["value"]

    def history(self, subject: str, key: Optional[str] = None) -> List[MemoryRecord]:
        records = []
        for raw in self._read_all():
            if raw["subject"] != subject:
                continue
            if key is not None and raw["key"] != key:
                continue
            records.append(MemoryRecord(**raw))
        return records

    def subjects(self) -> List[str]:
        return sorted({raw["subject"] for raw in self._read_all()})

    def write_count(self) -> int:
        return len(self._read_all())


class MemoryWriter:
    """Attaches memory to the execution loop.

    Registered with `loop.observe(...)`, so memory is written from inside the cycle
    that produced it — not reconstructed afterwards from a log.
    """

    def __init__(self, memory: InstitutionalMemory, agent_id: str, every: int = 1):
        if every < 1:
            raise MemoryError_("`every` must be at least 1 cycle")
        self.memory = memory
        self.agent_id = agent_id
        self.every = every
        self.writes = 0

    def __call__(self, record) -> None:
        if record.cycle % self.every != 0:
            return
        self.memory.remember(
            subject=self.agent_id,
            key="running_total",
            value=record.output,
            written_by="runtime/loop",
        )
        self.writes += 1

    def remember_run_end(self, result) -> None:
        self.memory.remember(
            subject=self.agent_id,
            key="last_run",
            value={
                "cycles_completed": result.cycles_completed,
                "stopped_by": result.stopped_by,
                "final_output": result.final_output,
            },
            written_by="runtime/loop",
        )
        self.memory.remember(
            subject=self.agent_id,
            key="running_total",
            value=result.final_output,
            written_by="runtime/loop",
        )
        self.writes += 2
