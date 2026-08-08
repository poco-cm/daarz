# Institution Manifest: safety

## Identity

Institution identifier: `safety`. It is the non-negotiable operational safety institution.

## Purpose

Prevent unsafe activation and provide controlled interruption mechanisms.

## Authority

UNDEFINED — requires Governance decision before Birth phase

## Inputs

Stop requests naming a reason and an actor; declared limits (`max_operations`, `max_duration_seconds`) supplied per agent at construction; `InstitutionRequest` messages with action `halt`.

## Outputs

`SwitchState` records; `ExecutionHalted` raised into any running loop; `BoundaryViolation` raised on breach, preceded by notification of every registered `on_violation` observer; `InstitutionResponse` confirming a halt.

## Dependencies

The local filesystem, for durable kill-switch state that survives process restart. `constitution/articles/` for the rules it enforces. `protocols/institution/requests/` for its address. It depends on no other institution, deliberately: a stop authority that can be disabled by the failure of something else is not a stop authority.

## State

Durable. The engaged/released state of the kill switch is written to a JSON file (`CIV_KILL_SWITCH_PATH`, default `safety/kill_switch/state/`) together with the reason, the actor, and the timestamp. A restart does not clear an engaged switch. `BoundaryEnforcer` state (operation count, elapsed time) is per-run and in-process by design.

## Lifecycle

UNDEFINED — requires Governance decision before Birth phase

## Permissions

UNDEFINED — requires Governance decision before Birth phase

## Events

Kill-switch engagement and release are recorded in durable state. Boundary violations are broadcast to every registered `on_violation` observer before the exception is raised, which is how `observability/alerts/` and `observability/logs/` learn of a breach.

## Data

Kill-switch state file: `{engaged, reason, actor, engaged_at}`. No agent data, no execution history.

## Interfaces

Direct: `KillSwitch.engage`, `.release`, `.is_engaged`, `.read`, `.assert_clear`; `Boundaries`, `BoundaryEnforcer.record_operation`, `.on_violation`. Protocol: action `halt`. There is deliberately no `release` action in the protocol vocabulary — Article I reserves release to a human, so an institution is given nothing to reach for.

## Tests

`tests/policy/test_kill_switch.py` (6, including a live 2000-cycle loop halted mid-run from another thread) and `tests/policy/test_boundaries.py` (6). Halt behaviour is additionally exercised in `test_birth.py`, `test_population.py` and `test_formation.py`.

## Failure Modes

`ExecutionHalted` — raised into a running loop when the switch is engaged; the intended behaviour, not a fault. `BoundaryViolation` — a declared limit was exceeded. `PermissionError` — a non-human attempted release (Article I). A halt request carrying no reason is refused, because an unexplained stop cannot be reviewed afterwards. Unavailable state storage is treated as engaged rather than clear: the safe default is to stop.

## Evolution Rules

UNDEFINED — requires Governance decision before Birth phase
