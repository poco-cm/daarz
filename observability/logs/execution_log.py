"""Execution logging, attached to the real loop.

Order 2 phase 3 step 3 requires that every cycle is logged truthfully rather than
decoratively. The log therefore records what the cycle *did*, including cycles
that achieved nothing, and it is written by the loop's own observer hook rather
than by a separate narration of what the loop was expected to do.

Format is JSON Lines: one self-contained record per line, append-only, readable
without loading the whole file.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, Iterator, List, Optional


class ExecutionLog:
    def __init__(self, path: str, agent_id: str):
        self.path = path
        self.agent_id = agent_id
        os.makedirs(os.path.dirname(os.path.abspath(self.path)), exist_ok=True)
        self._written = 0

    @property
    def written(self) -> int:
        return self._written

    def _append(self, payload: Dict[str, Any]) -> None:
        payload["agent_id"] = self.agent_id
        payload["at"] = time.time()
        with open(self.path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")
        self._written += 1

    # -- observer hooks ----------------------------------------------------

    def record_cycle(self, record) -> None:
        """Attach with `loop.observe(log.record_cycle)`."""
        self._append(
            {
                "event": "cycle",
                "cycle": record.cycle,
                "perceived": record.perceived,
                "output": record.output,
                "productive": record.productive,
                "note": record.note,
            }
        )

    def record_run_end(self, result) -> None:
        self._append(
            {
                "event": "run_end",
                "cycles_completed": result.cycles_completed,
                "stopped_by": result.stopped_by,
                "detail": result.detail,
                "final_output": result.final_output,
            }
        )

    def record_violation(self, violation) -> None:
        self._append(
            {
                "event": "boundary_violation",
                "limit_name": violation.limit_name,
                "limit_value": violation.limit_value,
                "observed": violation.observed,
            }
        )

    # -- reading -----------------------------------------------------------

    def entries(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.path):
            no_entries: List[Dict[str, Any]] = []
            return no_entries
        with open(self.path, "r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]

    def cycles_logged(self) -> int:
        return sum(1 for entry in self.entries() if entry.get("event") == "cycle")
