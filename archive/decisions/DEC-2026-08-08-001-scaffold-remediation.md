# Decision Record — Genesis Scaffold Remediation

**ID:** `DEC-2026-08-08-001`
**Date:** 2026-08-08
**Phase:** Genesis (pre-Birth)
**Status:** Executed, partial — one item deliberately left open for governance
**Trigger:** Conformance audit of the repository tree against `CIVILIZATION_GENESIS_SPECIFICATION`, run before dispatching Order 2. The audit found the Genesis exit test in Spec §5 unsatisfied.

---

## 1. Findings that caused this decision

**Finding A — lightweight layers incomplete.** Spec §1 defines a lightweight layer as "README + 2-4 functional subdirectories only". All 25 layers carried a `README.md` and zero subdirectories. As a direct consequence, 14 paths named explicitly in Order 2 did not exist: `constitution/articles/`, `safety/kill_switch/`, `safety/boundaries/`, `tests/policy/`, `runtime/loop/`, `runtime/perception/`, `runtime/action/`, `agents/registry/`, `population/census/`, `population/lifecycle/`, `observability/logs/`, `observability/alerts/`, `governance/proposal/`, `governance/voting/`. Order 2 phase 1 could not have started.

**Finding B — false statement in the scaffold report.** `SCAFFOLD_REPORT.md` revision 1 asserted "No root directory outside the specification was introduced". The repository contains 13 such root entries and 113 files beneath them, including `artifacts/` with real executable TypeScript.

**Finding C — what was already correct.** 17/17 institutions complete; 15/15 manifest fields present and correctly ordered in all 17 manifests; `protocols/`, `civilization/`, `archive/` matching their specification sections literally; zero code files inside the specification's scope. These were verified, not assumed, and no change was made to them.

---

## 2. What was decided and executed

1. Each of the 25 lightweight layers received 2-4 functional subdirectories with a documentation-only `README.md`, per Spec §1. The subdirectory names for each layer are fixed by this record and are not to be renamed without passing the §7 pipeline.
2. Seven institutional subdirectories named explicitly in the human-issued Order 2 were created: `constitution/articles/`, `safety/kill_switch/`, `safety/boundaries/`, `population/census/`, `population/lifecycle/`, `governance/proposal/`, `governance/voting/`.
3. `SCAFFOLD_REPORT.md` was rewritten as revision 2, correcting the false statement in Finding B and declaring the Genesis exit test **not yet passed**.

**Authority basis.** Spec §8 permits the executive agent to create directories and files named literally in the specification or in the following build order, and to write descriptive `README.md` content including explicit `UNDEFINED`. Item 2 rests on the human-issued Order 2, which names each of those seven paths directly. No root directory was created. No pattern was invented. No executable logic was written.

---

## 3. What was deliberately NOT decided

The status of `artifacts/` (80 files), `lib/` (20 files), the Replit platform configuration, and the executable content under `scripts/` remains **open**.

Spec §8 forbids the executive agent from taking a governance decision on behalf of `governance/`, and forbids deleting anything without a direct explicit human order. Both ratifying this content as an exception and removing it are governance acts. Neither was performed. The question is filed as a proposal in `governance/architecture_changes/proposals/PROP-2026-08-08-001.md`.

Nothing was deleted.

---

## 4. Consequences

- The 14 paths required by Order 2 now exist. Order 2 phases 1 through 5 are structurally executable.
- The Genesis exit test remains **open** on exactly one item: the out-of-specification content in Finding B.
- Any future rename or removal of the subdirectories fixed in section 2 requires the full Spec §7 pipeline.

## 5. Evidence

- Tree scan: 627 entries, 366 files, compared field by field against the specification.
- Manifest scan: 17 files, 15/15 fields each, order verified, 13 `UNDEFINED` markers each.
- Code scan: 0 code files inside specification scope; 82 code files total, all under `artifacts/`, `lib/`, and `scripts/`.
