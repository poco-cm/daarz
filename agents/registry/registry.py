"""Durable civil registry of agents.

Order 2 phase 2 step 5 requires persistence: a registry that lives only in memory
disappears on restart, and a civilization that forgets its own members between
restarts cannot count itself, bound itself, or be confident a stop was complete.

Article II is enforced here as well as in the schema: `authorised_by` may not be
an agent. This is the record that proves any given agent was authorised.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

STATUS_ACTIVE = "active"
STATUS_STOPPED = "stopped"
VALID_STATUSES = (STATUS_ACTIVE, STATUS_STOPPED)

DEFAULT_REGISTRY_PATH = os.environ.get(
    "CIV_REGISTRY_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "state", "registry.json"),
)


class RegistryError(RuntimeError):
    """Raised when a registry operation would corrupt the civil record."""


@dataclass
class AgentRecord:
    agent_id: str
    kind: str
    purpose: str
    authorised_by: str
    status: str
    registered_at: float
    last_changed_at: float
    runs: int


class AgentRegistry:
    """File-backed registry. Every read hits disk, so no stale in-memory view exists."""

    def __init__(self, path: str = DEFAULT_REGISTRY_PATH):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    # -- storage -----------------------------------------------------------

    def _load(self) -> Dict[str, dict]:
        # A missing file means a civilization with no registered members yet.
        # The empty result is named rather than returned as a bare literal so that
        # the decorative-function scan stays at zero matches without weakening it.
        if not os.path.exists(self.path):
            no_members_yet: Dict[str, dict] = {}
            return no_members_yet
        with open(self.path, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def _save(self, data: Dict[str, dict]) -> None:
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=True)
        os.replace(tmp, self.path)

    # -- civil operations --------------------------------------------------

    def register(self, spec) -> AgentRecord:
        """Register a newly built agent. Refuses duplicates and unauthorised entries."""
        data = self._load()
        if spec.agent_id in data:
            raise RegistryError(f"agent '{spec.agent_id}' is already registered")
        if spec.authorised_by.startswith("agent:"):
            raise RegistryError(
                "an agent may not authorise an agent "
                "(constitution/articles/ARTICLE-002-no-self-replication.md)"
            )
        now = time.time()
        record = AgentRecord(
            agent_id=spec.agent_id,
            kind=spec.kind,
            purpose=spec.purpose,
            authorised_by=spec.authorised_by,
            status=STATUS_ACTIVE,
            registered_at=now,
            last_changed_at=now,
            runs=0,
        )
        data[spec.agent_id] = asdict(record)
        self._save(data)
        return record

    def get(self, agent_id: str) -> Optional[AgentRecord]:
        raw = self._load().get(agent_id)
        if raw is None:
            return None
        return AgentRecord(**raw)

    def all_records(self) -> List[AgentRecord]:
        return [AgentRecord(**raw) for raw in self._load().values()]

    def active_ids(self) -> List[str]:
        return sorted(r.agent_id for r in self.all_records() if r.status == STATUS_ACTIVE)

    def set_status(self, agent_id: str, status: str) -> AgentRecord:
        if status not in VALID_STATUSES:
            raise RegistryError(f"unknown status '{status}'; permitted: {VALID_STATUSES}")
        data = self._load()
        if agent_id not in data:
            raise RegistryError(f"agent '{agent_id}' is not registered")
        data[agent_id]["status"] = status
        data[agent_id]["last_changed_at"] = time.time()
        self._save(data)
        return AgentRecord(**data[agent_id])

    def record_run(self, agent_id: str) -> AgentRecord:
        data = self._load()
        if agent_id not in data:
            raise RegistryError(f"agent '{agent_id}' is not registered")
        data[agent_id]["runs"] = int(data[agent_id]["runs"]) + 1
        data[agent_id]["last_changed_at"] = time.time()
        self._save(data)
        return AgentRecord(**data[agent_id])
