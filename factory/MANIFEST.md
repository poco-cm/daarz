# Institution Manifest: factory

## Identity

Institution identifier: `factory`. It is the governed agent-creation institution.

## Purpose

Create agents only through approved specifications and safety boundaries.

## Authority

UNDEFINED — requires Governance decision before Birth phase

## Inputs

`AgentSpec` instances (`factory/schemas/agent_spec.py`), an iterable input source for the agent under construction, and `InstitutionRequest` messages with action `build_agent` arriving over `protocols/institution/requests/`.

## Outputs

`BuiltAgent` objects, each holding a configured `ExecutionLoop`; a durable entry in `agents/registry/`; and `InstitutionResponse` messages carrying `{agent_id, resumed_from}` on success or a stated refusal reason on failure.

## Dependencies

`agents/registry/` (durable registration), `safety/kill_switch/` and `safety/boundaries/` (limits bound at construction), `runtime/` (perception, action, reflection, loop), `memory/` (optional; consulted before build so an agent resumes from what is remembered), `observability/logs/` and `observability/alerts/` (optional, wired at construction), `protocols/institution/requests/`, `institutions/runtime/`.

## State

The institution itself holds no durable state. `AgentFactory` retains only its injected collaborators. All durable state belongs to `agents/registry/` and `memory/`. `FactoryService` retains an in-process map of agents it built during the current run; this is not persisted and is not authoritative.

## Lifecycle

UNDEFINED — requires Governance decision before Birth phase

## Permissions

UNDEFINED — requires Governance decision before Birth phase

## Events

Emits no events of its own in this phase. Agents it constructs emit per-cycle records through `ExecutionLoop.observe`, and boundary violations through `BoundaryEnforcer.on_violation`, both wired by the factory at construction.

## Data

Agent specifications (in memory and as dictionaries in protocol payloads). Writes no files directly; registration data is written by `agents/registry/` to its own JSON store.

## Interfaces

Direct: `AgentFactory.build`, `.create_and_register`, `.rebuild_registered`. Protocol: action `build_agent`, served by `factory/services/handler.py`, reachable only by an activated institution.

## Tests

`tests/unit/test_agent_spec.py` (10), `tests/integration/test_birth.py` (8), and the construction paths exercised throughout `tests/integration/test_population.py` and `test_formation.py`. 100 tests pass across the repository at the close of Order 2 phase 1.

## Failure Modes

`SpecificationError` — the specification is invalid or names an agent as authoriser (Article II). `ConstructionError` — the kind has no construction path, or a rebuild was requested for an unregistered agent. `RegistryError` — duplicate registration. On any construction failure nothing is registered, so the registry never records an agent that does not exist. Over the protocol all of these become a refusal with a stated reason rather than an exception.

## Evolution Rules

UNDEFINED — requires Governance decision before Birth phase
