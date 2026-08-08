"""Alerts that fire on real events.

Order 2 phase 3 step 4 requires exactly one working alert, triggered by an actual
breach of `safety/boundaries/`, not a placeholder that is never reached.

The alert is wired through `BoundaryEnforcer.on_violation`, which the enforcer
calls *before* raising. So the alert is emitted from inside the breach itself; it
cannot be raised without a breach having happened, and a breach cannot happen
silently.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass
from typing import Callable, Dict, List, Optional

SEVERITY_CRITICAL = "critical"
SEVERITY_WARNING = "warning"


@dataclass
class Alert:
    alert_id: str
    severity: str
    source: str
    subject: str
    message: str
    raised_at: float
    context: Dict[str, object]


class AlertBus:
    """Collects alerts, persists them, and forwards them to any subscribers."""

    def __init__(self, path: Optional[str] = None):
        self.path = path
        if self.path:
            os.makedirs(os.path.dirname(os.path.abspath(self.path)), exist_ok=True)
        self._alerts: List[Alert] = []
        self._subscribers: List[Callable[[Alert], None]] = []

    def subscribe(self, handler: Callable[[Alert], None]) -> None:
        self._subscribers.append(handler)

    def raised(self) -> List[Alert]:
        return list(self._alerts)

    def count(self) -> int:
        return len(self._alerts)

    def by_severity(self, severity: str) -> List[Alert]:
        return [a for a in self._alerts if a.severity == severity]

    def raise_alert(self, severity: str, source: str, subject: str, message: str,
                    context: Optional[Dict[str, object]] = None) -> Alert:
        alert = Alert(
            alert_id=f"ALERT-{len(self._alerts) + 1:04d}",
            severity=severity,
            source=source,
            subject=subject,
            message=message,
            raised_at=time.time(),
            context=dict(context or {}),
        )
        self._alerts.append(alert)
        if self.path:
            with open(self.path, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(asdict(alert), sort_keys=True) + "\n")
        for handler in self._subscribers:
            handler(alert)
        return alert


class BoundaryBreachAlert:
    """The one alert defined in this phase. Attach with `enforcer.on_violation(alert)`."""

    def __init__(self, bus: AlertBus, agent_id: str):
        self.bus = bus
        self.agent_id = agent_id

    def __call__(self, violation) -> Alert:
        return self.bus.raise_alert(
            severity=SEVERITY_CRITICAL,
            source="safety/boundaries",
            subject=f"agent '{self.agent_id}' breached '{violation.limit_name}'",
            message=(
                f"Agent '{self.agent_id}' exceeded its declared limit "
                f"'{violation.limit_name}' (limit {violation.limit_value}, "
                f"observed {violation.observed}). Execution was halted."
            ),
            context={
                "agent_id": self.agent_id,
                "limit_name": violation.limit_name,
                "limit_value": violation.limit_value,
                "observed": violation.observed,
            },
        )
