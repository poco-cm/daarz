# BUILD_PHASE_1_REPORT

**Order:** 2 — "خط البناء" (Build Line), phases 1–6
**Period:** 2026-08-09
**Repository:** `poco-cm/daarz`, branch `main`
**Author:** executive agent, under §8 Genesis authority
**Test suite at close:** 100 tests, all passing

---

## 1. Summary

Order 2 asked for six phases, each with an exit gate, under one binding rule: no function
may return a fixed value unrelated to its input, and every step must produce concrete
evidence.

All six phases were executed. Five gates were met as written. One gate — the phase 5
requirement that a proposal traverse the full §7 pipeline — was met **partially and
deliberately**, and the reason is constitutional rather than technical. Section 4 gives the
gate-by-gate comparison; section 6 states the gaps without softening them.

What exists now that did not exist before this order:

- A constitution of three articles, enforced in code rather than described in prose.
- A durable stop authority consulted before every execution cycle, with no exemption path.
- A working agent: specified, built, registered, run, and stopped by a human mid-flight.
- A live population count, a two-state lifecycle, per-cycle logging, and one alert that
  fires only on a real boundary breach.
- Three activated institutions with a validated protocol between them, and a memory that
  changes what an agent does on its next run.
- A §7 change pipeline that refuses to let a proposal pass incorrectly, including refusing
  the executive agent's own attempt to approve its own proposal.

---

## 2. Commits

| Commit | Content |
|---|---|
| `828e6df` | Pre-order remediation: 61 subdirectories for the 25 light layers; 7 directories Order 2 required that did not exist; corrected `SCAFFOLD_REPORT.md`; `DEC-2026-08-08-001` |
| `c71ea082` | Genesis closure: `DEC-2026-08-09-002` ratifying the infrastructure annex, `ANNEX-001`, `SCAFFOLD_REPORT` rev3, `MS-001` |
| `f98a8238` | Phase 1 — constitution and safety |
| `eefe64ed` | Phase 2 — Birth |
| `b40ee152` | Phase 3 — population and observability |
| `4f48b377` | Phase 4 — Formation |
| `10e909f6` | Phase 5 — governance |
| (this commit) | Phase 6 — manifest resolution, snapshot, this report |

---

## 3. Verification gates, run at close

| Gate | Command | Result |
|---|---|---|
| Full suite | `python3 -m unittest discover -s tests -t .` | **100 tests, OK** |
| Decorative functions | `grep -rn "return True$\|return {}\|return []" --include="*.py" .` | **zero matches** |
| Unimplemented stubs | `grep -rln NotImplementedError --include="*.py" .` | **none** |
| Implementation size | 30 modules, 3,470 lines | — |

---

## 4. Exit gates against actual results

### Phase 1 — Constitution and safety

| Required | Actual | Verdict |
|---|---|---|
| At least one real article in `constitution/articles/` | Three: Article I (human stop authority), Article II (no self-replication), Article III (no automated amendment, including by non-enforcement) | **met** |
| Working stop mechanism in `safety/kill_switch/` | `KillSwitch` with file-backed durable state surviving restart; `assert_clear()`; `ExecutionHalted`; a reason is mandatory; release raises `PermissionError` for a non-human | **met** |
| Real limits in `safety/boundaries/` | `Boundaries`, `BoundaryEnforcer`, `BoundaryViolation`, injectable clock, `on_violation` observer hook | **met** |
| A test in `tests/policy/` that actually runs | 12 tests, including a live 2,000-cycle loop halted mid-run from a separate thread | **met** |
| Decision in `archive/decisions/` | `DEC-2026-08-09-003-phase1.md` with embedded test output | **met** |

### Phase 2 — Birth

| Required | Actual | Verdict |
|---|---|---|
| One agent schema in `factory/schemas/` | `AgentSpec` — frozen, validated, rejects an agent as authoriser, rejects an inert step | **met** |
| Real `factory/runtime/` | `AgentFactory` — builds and registers; registers only after successful construction | **met** |
| Three-stage loop in `runtime/loop/` | `perception → action → reflection`, each a real module whose output depends on its input | **met** |
| Kill-switch check **before every cycle** | `assert_clear()` at the top of each iteration; no sampling, no fast path; a pre-engaged switch yields zero cycles | **met** |
| Persistent registration in `agents/registry/` | File-backed JSON registry; verified to survive a fresh registry view | **met** |
| Actually run the agent and kill it mid-run | `agent-001` ran **10,258 cycles of a possible 99,999** and was stopped by an external thread acting as the human operator | **met** |
| Milestone in `civilization/milestones/` | `MS-002-birth.md`, containing the real log — including the first attempt, which **failed** its own check because the agent hit its operation boundary before the human could stop it | **met** |

### Phase 3 — Population and observability

| Required | Actual | Verdict |
|---|---|---|
| `population/census/` reflecting the real number of active agents by live query | `PopulationCensus` holds no count; every call reads the registry from disk. Tested adversarially by mutating the registry through a *separate* object and asserting the census notices | **met** |
| `population/lifecycle/` with active/stopped only | Exactly two states, two permitted transitions, redundant transitions refused | **met** |
| `observability/logs/` wired to the loop | Per-agent JSON Lines log attached through the loop's own observer hook, recording every cycle including unproductive ones | **met** |
| One real alert firing on a `safety/boundaries/` breach | `BoundaryBreachAlert` fires from inside `BoundaryEnforcer` before the exception is raised. Verified in both directions: one critical alert on breach, **zero** on a compliant run | **met** |
| Integration test with two agents | `tests/integration/test_population.py`, 13 tests | **met** |

### Phase 4 — Formation

| Required | Actual | Verdict |
|---|---|---|
| Exactly 3 institutions activated | `factory`, `safety`, `memory`. Asserted by test. The other 14 are dormant and have no protocol address | **met** |
| One real message schema in `protocols/institution/requests/` | `InstitutionRequest` / `InstitutionResponse` / `RequestBus`. Validated at construction: a message to a dormant institution cannot be built at all | **met** |
| `memory/` wired to the loop | Wired in the strong sense: the factory consults memory **before** building, so a stopped agent resumes from its remembered total. Run 1 reached 10; run 2 resumed from 10 and reached 21. The control case — same agent, memory-less factory — reaches 11 | **met** |
| Zero decorative functions | Scan returns zero matches | **met** |
| Snapshot in `archive/institutional/` | `SNAPSHOT-2026-08-09-formation.md`, generated by parsing the source with `ast` rather than written by hand | **met** |
| Milestone | `MS-003-formation.md` | **met** |

### Phase 5 — Governance

| Required | Actual | Verdict |
|---|---|---|
| Minimal `governance/proposal/` and `governance/voting/` | Both implemented. The pipeline refuses skipped stages, repeated stages, invented stages, missing findings, and missing evidence. Voting refuses non-human voters, double votes, unreasoned votes, sub-quorum approval, and silence | **met** |
| Run one proposal through all §7 stages | **Partially met — deliberately.** See below | **partial** |
| Do **not** implement the fourth institution | Not implemented. `ACTIVATED` remains exactly three, asserted by a test so an accidental future activation breaks the suite | **met** |
| Record in `archive/decisions/` | `DEC-2026-08-09-007-phase5.md` | **met** |

**On the partial gate.** Two facts collide. Order 2 asks for one proposal to traverse the
full pipeline. §8 of the founding specification forbids the executive agent from taking a
governance decision on behalf of `governance/`, "even formally, even in test data".
Traversing the real pipeline to the end requires passing `governance_approval`, which
requires counted human ballots.

The resolution taken, stated plainly:

- The **mechanism** is demonstrated end to end. `test_a_proposal_can_traverse_all_ten_stages`
  runs a proposal through every stage with synthetic human voters on a synthetic poll.
- The **real** proposal, `PROP-2026-08-09-002` (activate `population` as the fourth
  institution), passed five stages with genuine analysis and was then **refused
  advancement by its own pipeline** for lack of ballots:

  ```
  refused as expected: governance_approval cannot pass: the poll is 'pending'
  (no ballots have been cast; silence is not consent)
  ```

That refusal is offered as the phase evidence. Reporting a complete real traversal would
have required the agent to cast a human's vote. **A human ballot is required to advance
`PROP-2026-08-09-002`.**

Also recorded: Order 2 refers to "the nine stages of §7". The text of §7 names **ten**.
All ten are implemented; the founding document was treated as the authority. This is
flagged for correction if the intent was different.

### Phase 6 — Consolidation

| Required | Actual | Verdict |
|---|---|---|
| Run all tests | 100 tests, all passing | **met** |
| Resolve `UNDEFINED`s where possible in the 3 activated institutions | 27 of 39 resolved (9 per institution). 12 left open — see section 5 | **met** |
| Snapshot in `archive/snapshots/` | `SNAPSHOT-2026-08-09-order2-close.md`, generated from source | **met** |
| `BUILD_PHASE_1_REPORT.md` at root comparing every gate to actual result | This document | **met** |
| Do not proceed to Education | Not started. No `universities/`, `learning/`, or `research/` code exists | **met** |

---

## 5. Manifest resolution — what was resolved and what was not

The rule applied: **a field is resolved only when the answer is an observable fact about
code that now exists.** A field whose answer requires someone to *decide* something stays
`UNDEFINED`, because §8 forbids the executive agent from deciding on governance's behalf.

Resolved for each of `factory`, `safety`, `memory` (9 fields each, 27 total): Inputs,
Outputs, Dependencies, State, Events, Data, Interfaces, Tests, Failure Modes.

Left `UNDEFINED` (4 fields each, 12 total): **Authority, Permissions, Lifecycle, Evolution
Rules**. These are governance questions. What an institution *may* do, who may grant it
more, when it may be retired, and how it may change are not facts about code — they are
decisions, and no human has taken them.

One honest tension to name: `institutions/runtime/activation.py` contains an
`InstitutionProfile.authority` string for each activated institution, written by the agent
in phase 4. That is a **de facto** operating description, not a governance grant. The
manifests deliberately do not adopt it. If governance later rules differently, the code
must change, not the ruling.

Recorded in full in `archive/decisions/DEC-2026-08-09-008-phase6.md`.

---

## 6. Gaps, defects, and things not done

Stated without softening, because a report that lists only successes is not a report.

1. **`PROP-2026-08-09-002` is unfinished and requires a human ballot.** Five of ten stages.
2. **A real defect was found and left unfixed, by design.** Security review of the proposal
   found that `set_lifecycle` over the protocol would let an institution mark an agent
   `stopped` without engaging the kill switch. The loop consults `safety/`, never the
   registry — so that would be a stop that does not stop. It is recorded as a binding
   condition on any future implementation rather than fixed now, because fixing it would
   mean implementing part of the fourth institution, which Order 2 forbids.
3. **`population/` and `observability/` contain running code but are not activated
   institutions.** They have no protocol address and no declared authority. This is an
   inconsistency in kind, accepted because Order 2 fixed the activated count at exactly
   three.
4. **Memory has no corruption handling.** A malformed line in the store raises
   `json.JSONDecodeError` on the next read. Known gap, not yet addressed.
5. **The three-stage loop supports exactly one agent kind.** `accumulator`. Adding kinds
   without something needing them would be decoration.
6. **`archive/` is written to but never read by running code.** It is a record for humans,
   not yet a resource the civilization consults.
7. **Nothing runs continuously.** Agents run when invoked and stop. There is no scheduler,
   no daemon, and no autonomous activity of any kind.
8. **The phase 2 decision record was written after the phase 2 commit**, not before. Noted
   in `DEC-2026-08-09-004`. Later phases recorded in order.
9. **Governance can only decide; it cannot execute.** An approved proposal produces a
   record, not a change. Nothing wires `governance/` to the code it would govern.

---

## 7. Constitutional position at close

| Article | Enforced where | Verified by |
|---|---|---|
| I — Only a human may release a stop; anyone may engage one | `safety/kill_switch/`; the protocol has no `release` action at all | `tests/policy/test_kill_switch.py`; `test_formation.py::test_safety_halts_on_request_but_offers_no_release_action` |
| II — No self-replication | `factory/schemas/`, `agents/registry/`, and `factory/services/` — three independent points | `test_agent_spec.py`; `test_registry.py`; `test_formation.py::test_an_agent_cannot_cause_creation_through_the_protocol` |
| III — No automated amendment | `governance/voting/` — silence, timeout, and absence of opposition can never approve | `test_governance.py::test_silence_yields_pending_not_approval` and six related refusal tests |

---

## 8. Boundary of this order

Order 2 phase 6 states: **do not proceed to the Education phase.** That boundary is
observed. No code exists under `universities/`, `learning/`, `research/`, or `scientists/`.

The next order, if given, would need to decide at minimum:

- Whether `PROP-2026-08-09-002` is approved, rejected, or withdrawn.
- Whether the four `UNDEFINED` governance fields are to be resolved, and by whom.
- Whether `governance/` should be able to *cause* change, or only to record it.
- Whether §7 has nine stages or ten.
