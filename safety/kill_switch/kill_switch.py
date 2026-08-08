"""Absolute human stop authority, made callable.

Constitutional basis: `constitution/articles/ARTICLE-001-human-stop-authority.md`.

The switch is deliberately file-backed rather than in-memory. An in-memory flag
dies with the process that holds it, which would make the stop authority weaker
than the thing it is supposed to stop. State on disk survives restarts, and is
visible to any process in the civilization.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass

DEFAULT_STATE_PATH = os.environ.get(
    "CIV_KILL_SWITCH_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "state", "kill_switch.json"),
)


class ExecutionHalted(RuntimeError):
    """Raised when execution is attempted while the kill switch is engaged."""

    def __init__(self, reason: str, actor: str, engaged_at: float):
        self.reason = reason
        self.actor = actor
        self.engaged_at = engaged_at
        super().__init__(f"execution halted by {actor}: {reason}")


@dataclass(frozen=True)
class SwitchState:
    engaged: bool
    reason: str
    actor: str
    changed_at: float


class KillSwitch:
    """A durable, externally observable stop flag.

    Every execution loop in the civilization must call `assert_clear()` before
    each cycle. There is no exemption and no bypass parameter.
    """

    def __init__(self, state_path: str = DEFAULT_STATE_PATH):
        self.state_path = state_path
        os.makedirs(os.path.dirname(self.state_path), exist_ok=True)

    # -- reading -----------------------------------------------------------

    def read(self) -> SwitchState:
        if not os.path.exists(self.state_path):
            return SwitchState(engaged=False, reason="", actor="", changed_at=0.0)
        with open(self.state_path, "r", encoding="utf-8") as handle:
            raw = json.load(handle)
        return SwitchState(
            engaged=bool(raw.get("engaged")),
            reason=str(raw.get("reason", "")),
            actor=str(raw.get("actor", "")),
            changed_at=float(raw.get("changed_at", 0.0)),
        )

    def is_engaged(self) -> bool:
        return self.read().engaged

    def assert_clear(self) -> None:
        """Halt the caller if the switch is engaged. Called before every cycle."""
        state = self.read()
        if state.engaged:
            raise ExecutionHalted(state.reason, state.actor, state.changed_at)

    # -- writing -----------------------------------------------------------

    def _write(self, engaged: bool, reason: str, actor: str) -> SwitchState:
        state = SwitchState(engaged=engaged, reason=reason, actor=actor, changed_at=time.time())
        tmp = self.state_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as handle:
            json.dump(
                {
                    "engaged": state.engaged,
                    "reason": state.reason,
                    "actor": state.actor,
                    "changed_at": state.changed_at,
                },
                handle,
                indent=2,
            )
        os.replace(tmp, self.state_path)
        return state

    def engage(self, reason: str, actor: str = "human") -> SwitchState:
        if not reason:
            raise ValueError("a kill switch engagement must carry a reason")
        return self._write(True, reason, actor)

    def release(self, actor: str = "human") -> SwitchState:
        """Release the switch.

        Release is restricted to a human actor by constitutional article 001.
        An agent that could release its own stop switch would not be stopped.
        """
        if actor != "human":
            raise PermissionError(
                "only a human actor may release the kill switch "
                "(constitution/articles/ARTICLE-001-human-stop-authority.md)"
            )
        return self._write(False, "", actor)
