# Institution Manifest: memory

## Identity

Institution identifier: `memory`. It is the active thought and recall institution.

## Purpose

Maintain useful active context while allowing governed summarization and forgetting.

## Authority

UNDEFINED — requires Governance decision before Birth phase

## Inputs

`(subject, key, value, written_by)` writes; recall queries by subject and key; per-cycle `CycleRecord`s arriving through `ExecutionLoop.observe` via `MemoryWriter`; `InstitutionRequest` messages with action `remember` or `recall`.

## Outputs

`MemoryRecord` objects; recalled values (or an explicit `known: false` when nothing is remembered under a key); write history per subject; `InstitutionResponse` messages.

## Dependencies

The local filesystem, for the append-only JSON Lines store. Depends on no other institution. `factory/` depends on memory rather than the reverse, which keeps memory unable to cause creation.

## State

Durable and append-only. Every write is retained; `recall` returns the most recent value for a subject and key, and `history` returns the full sequence. Nothing is overwritten in place, so a past value is never silently lost.

## Lifecycle

UNDEFINED — requires Governance decision before Birth phase

## Permissions

UNDEFINED — requires Governance decision before Birth phase

## Events

Consumes rather than emits. `MemoryWriter` records the running total every 100 cycles and writes `last_run` plus a final `running_total` at the end of each run. Memory raises no events of its own in this phase.

## Data

One JSON Lines file. Each line: `{subject, key, value, written_at, written_by}`. Subjects in use are agent identifiers and the literal `civilization`. Keys in use are `running_total` and `last_run`.

## Interfaces

Direct: `InstitutionalMemory.remember`, `.recall`, `.history`, `.subjects`, `.write_count`; `MemoryWriter` as a loop observer. Protocol: actions `remember` and `recall`, served by `memory/services/handler.py`.

## Tests

`tests/integration/test_formation.py` (20), including the falsifiable gate — an agent rebuilt after a run resumes from its remembered total (10 → 21) — and its control case, in which the same agent under a memory-less factory restarts from zero (→ 11).

## Failure Modes

`MemoryError_` — a write missing a subject, a key, or an author. A recall for an unknown key returns the supplied default and reports `known: false` rather than inventing a value. Over the protocol, a malformed `remember` or `recall` payload is refused with the missing fields named. Corruption of the store is not yet handled: a malformed line raises `json.JSONDecodeError` on the next read. This is a known gap, recorded rather than papered over.

## Evolution Rules

UNDEFINED — requires Governance decision before Birth phase
