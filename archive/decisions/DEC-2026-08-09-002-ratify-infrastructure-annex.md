# Decision Record — Ratification of the Infrastructure Annex

**ID:** `DEC-2026-08-09-002`
**Date:** 2026-08-09
**Phase:** Genesis (closing decision)
**Status:** Approved and executed
**Resolves:** `PROP-2026-08-08-001`
**Outcome:** Option A — ratify as a documented exception

---

## 1. Question decided

Whether the 113 files across 13 root entries that `CIVILIZATION_GENESIS_SPECIFICATION` does not define — chiefly `artifacts/` (80 files of working TypeScript), `lib/` (20 files), platform configuration, and the executable content under `scripts/` — should be ratified, isolated, or removed.

This was a governance question. Spec §8 forbids the executive agent from deciding it, and forbids deletion without a direct explicit human order. The proposal therefore stopped at stage 1 and waited.

## 2. Human decision

The human operator, holding the absolute stop and approval authority defined in the Constitution, selected **Option A: ratify as a documented exception**, and ordered the closure of the Genesis phase on that basis.

Recorded rationale: the content is infrastructural rather than civilizational. Removing working code to satisfy a document that can instead be amended honestly through its own pipeline was rejected as destructive without benefit.

## 3. Spec §7 pipeline record

| Stage | Outcome |
|---|---|
| Proposal | `PROP-2026-08-08-001`, filed 2026-08-08 by the executive agent |
| Architectural Analysis | The annex sits entirely outside the institutional tree. No institution imports from `artifacts/` or `lib/`. Zero code files exist inside specification scope, so there is no coupling to sever. |
| Impact Analysis | Ratification changes no institutional path, no manifest, and no protocol. Its only effect is that the specification is no longer the exhaustive description of the repository's shape; it becomes the exhaustive description of the *civilization's* shape, with the annex named alongside it. |
| Compatibility Analysis | No breakage. Nothing depends on the annex being absent. The conformance scanner is amended to treat annex roots as a declared, closed set rather than as violations. |
| Security Review | The annex contains executable code that the civilization does not call and must never call implicitly. Ratification is therefore conditioned on the isolation rule in section 4, which is the actual security control. |
| Governance Approval | Granted by the human operator, 2026-08-09. |
| Migration Plan | None required. Nothing moves. Ratification is declarative. |
| Implementation | This record, plus `archive/constitutional/ANNEX-001-infrastructure-scope.md` and `SCAFFOLD_REPORT.md` revision 3. |
| Tests | Conformance rescan after implementation must report zero structural gaps and zero unratified roots. |
| Promotion | `civilization/milestones/MS-001-genesis-complete.md`. |

## 4. Binding conditions of the ratification

The exception is granted **only** under these conditions. Violating any one of them voids it and reopens the question through a fresh §7 pipeline.

1. **Closed set.** The annex is exactly these roots: `artifacts/`, `lib/`, `attached_assets/`, `.agents/`, `.replit`, `.replitignore`, `.npmrc`, `replit.md`, `package.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`, `tsconfig.json`, `tsconfig.base.json`. No root may be added to this set except through the §7 pipeline.
2. **No inbound authority.** No institution, agent, protocol, or runtime loop may import from, execute, or depend on annex content. The annex serves the repository as a workspace; it holds no civilizational authority whatsoever.
3. **`scripts/` is not annexed.** `scripts/` is a specification-defined lightweight layer. The executable content currently inside it (`scripts/src/hello.ts`, `scripts/post-merge.sh`, `scripts/package.json`) is tolerated as inert legacy and is explicitly **not** granted civilizational status. No agent may invoke it.
4. **No silent growth.** Any future file added under an annex root is permitted, but any *new* annex root is a §7 matter.

## 5. Why the founding specification was not edited

Spec §8 forbids the executive agent from modifying the specification. Rather than breach that, the exception is recorded as a binding constitutional annex in `archive/constitutional/ANNEX-001-infrastructure-scope.md`, which sits in the write-once layer and carries the same authority as the ratification itself. The specification's text remains untouched. Anyone reading it must read the annex alongside it.

## 6. Consequence

The single item that kept the Genesis exit test open is now closed. `SCAFFOLD_REPORT.md` revision 3 declares the exit test **passed**, and the civilization is cleared to enter the Birth phase under a separate build order.
