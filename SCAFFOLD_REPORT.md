# Genesis Scaffold Report

**Revision:** 2 (2026-08-08) — supersedes revision 1, which contained one factual error corrected below.
**Reference:** `CIVILIZATION_GENESIS_SPECIFICATION`
**Verification method:** automated comparison of the full repository tree against the specification, plus field-level reading of all seventeen institutional `MANIFEST.md` files.

## Status

`Genesis` scaffold created from the approved Civilization Genesis Specification, then remediated once. This revision reports verified state, not intent.

## Scope completed

- 17 full institutions registered with `README.md` and the exact 15-field `MANIFEST.md` contract, in the order mandated by Spec §2. Verified: 17/17 complete, all 15 fields present and correctly ordered in every manifest, 13 fields per manifest carrying the literal `UNDEFINED — requires Governance decision before Birth phase` marker.
- `protocols/` registered with its five protocol families and all seventeen leaf directories from Spec §4.
- 25 infrastructure/tooling layers registered. **Revision 2:** each now carries the 2-4 functional subdirectories required by Spec §1. Revision 1 shipped these layers with a `README.md` only, which did not satisfy §1.
- `civilization/` received its fourteen operational metaphysics directories from Spec §3.
- `archive/` received its twelve immutable-history directories from Spec §6.
- No production runtime, active agent, permissions grant, governance decision, or migration logic was implemented inside the specification's scope.

## Genesis compliance

- Runtime-bearing files contain documentation-only placeholders.
- Zero code files (`.py`, `.ts`, `.js`) exist anywhere inside the specification's scope — institutions, protocols, and lightweight layers are all free of executable logic. Verified by extension scan across all 366 tracked files.
- Unknown decisions are explicitly marked `UNDEFINED — requires Governance decision before Birth phase`.

## Known deviation: content outside the specification

**Correction to revision 1.** Revision 1 stated "No root directory outside the specification was introduced." That statement was false. The repository contains 13 root entries and 113 files that the specification does not define:

| Entry | Files | Nature |
|---|---|---|
| `artifacts/` | 80 | Working TypeScript applications (`api-server`, `mockup-sandbox`) containing real executable logic |
| `lib/` | 20 | `api-spec/openapi.yaml`, `orval.config.ts`, package manifests |
| `attached_assets/` | 2 | Two copies of the founding specification itself |
| `.agents/` | 2 | `MEMORY.md`, `remote-repository-sync.md` |
| `.replit`, `.replitignore`, `.npmrc`, `replit.md` | 4 | Platform configuration |
| `package.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml` | 3 | Root-level package management |
| `tsconfig.json`, `tsconfig.base.json` | 2 | TypeScript configuration |

Additionally `scripts/src/hello.ts`, `scripts/post-merge.sh`, and `scripts/package.json` place executable content inside a specification-defined layer.

**Status of this deviation:** unresolved. It is a governance question under Spec §7 and §8, not an executive one. It is recorded as an open proposal in `governance/architecture_changes/proposals/` and must be either formally ratified as a documented exception or isolated, before the Genesis exit test can be declared passed. Nothing was deleted; Spec §8 prohibits removal without a direct explicit human order.

## Deliberate non-actions

- The Constitution was not authored or changed. `constitution/articles/` exists as an empty documented directory only.
- No agent was activated.
- No institution was granted operational authority.
- No data store, external service, or execution loop was introduced.
- No governance decision was taken on behalf of `governance/`.

## Genesis exit test

Spec §5 requires this report to match the specification 100%. Current state:

- Institutional structure, manifests, `protocols/`, `civilization/`, `archive/`: **matching**.
- Lightweight layers per §1: **matching as of revision 2**.
- Out-of-specification content: **not matching, pending governance**.

The Genesis exit test is therefore **not yet passed**. One open item remains, and it is named above rather than omitted.
