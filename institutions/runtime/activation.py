"""The register of activated institutions.

Order 2 phase 4 activates **exactly three** institutions: `factory`, `safety`, and
`memory`. Fourteen further institution directories exist in the repository with
complete manifests, but a directory is not an institution any more than an empty
building is a ministry. An institution is activated when it has running code, a
declared authority, and a protocol address other institutions can reach it at.

This module is the single answer to "is X activated?". Every other component asks
here rather than keeping its own opinion.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, FrozenSet, List

#: The exact set activated in phase 4. Changing this set is a governance action
#: under §7, not an implementation detail — see governance/ in phase 5.
ACTIVATED: FrozenSet[str] = frozenset({"factory", "safety", "memory"})

#: Every institution named in §1 of the founding specification.
ALL_INSTITUTIONS: FrozenSet[str] = frozenset({
    "constitution", "governance", "civilization", "factory", "universities",
    "research", "defense", "population", "institutions", "scientists",
    "economy", "knowledge", "memory", "learning", "safety", "security", "archive",
})


class ActivationError(RuntimeError):
    """Raised when something addresses an institution that is not activated."""


@dataclass(frozen=True)
class InstitutionProfile:
    name: str
    authority: str
    activated_in: str


PROFILES: Dict[str, InstitutionProfile] = {
    "factory": InstitutionProfile(
        name="factory",
        authority="Sole creator of agents. May build and register; may not run or stop them.",
        activated_in="Order 2 phase 2 (Birth)",
    ),
    "safety": InstitutionProfile(
        name="safety",
        authority="Holds the stop authority and the boundary limits. May halt any execution.",
        activated_in="Order 2 phase 1",
    ),
    "memory": InstitutionProfile(
        name="memory",
        authority="Durable record of what agents perceived and concluded. May read and write; may not act.",
        activated_in="Order 2 phase 4 (Formation)",
    ),
}


def is_activated(name: str) -> bool:
    return name in ACTIVATED


def require_activated(name: str) -> str:
    if name not in ALL_INSTITUTIONS:
        raise ActivationError(f"'{name}' is not an institution named in §1 of the specification")
    if name not in ACTIVATED:
        raise ActivationError(
            f"institution '{name}' exists but is not activated; "
            f"activated institutions are {sorted(ACTIVATED)}"
        )
    return name


def activated_names() -> List[str]:
    return sorted(ACTIVATED)


def dormant_names() -> List[str]:
    return sorted(ALL_INSTITUTIONS - ACTIVATED)


def profile(name: str) -> InstitutionProfile:
    require_activated(name)
    return PROFILES[name]
