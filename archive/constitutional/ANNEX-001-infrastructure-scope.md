# Constitutional Annex 001 — Infrastructure Scope

**Status:** Binding. Write-once. Read alongside `CIVILIZATION_GENESIS_SPECIFICATION`.
**Ratified:** 2026-08-09 by human governance approval, `DEC-2026-08-09-002`
**Amends:** nothing. The founding specification's text is untouched. This annex sits beside it.

---

## Why this annex exists

The founding specification describes the shape of the civilization. It does not describe the shape of the repository that hosts the civilization. Those turned out to be different things, and pretending otherwise would have required either deleting working code or letting the scaffold report lie. Both were rejected.

This annex names the difference explicitly, so that no future reader mistakes tolerated infrastructure for ratified civilizational structure.

## The annex set

These roots exist in the repository, are permitted, and hold **no civilizational authority**:

```
artifacts/            lib/                  attached_assets/      .agents/
.replit               .replitignore         .npmrc                replit.md
package.json          pnpm-lock.yaml        pnpm-workspace.yaml
tsconfig.json         tsconfig.base.json
```

This set is **closed**. Adding a root to it requires the full Spec §7 pipeline.

## The isolation rule

No institution, agent, protocol, or runtime loop may import from, execute, or depend on anything in the annex set. The relationship is one-directional and empty: the civilization does not see the annex.

This rule is the reason the annex is safe to ratify. It is not a formality; it is the entire security basis of the decision.

## What is deliberately not annexed

`scripts/` is a specification-defined lightweight layer, not annex content. The executable files currently inside it are inert legacy, tolerated but ungoverned, and no agent may invoke them. If `scripts/` is ever to hold live automation, that requires its own §7 passage.

## Precedence

Where this annex and the founding specification appear to conflict, the specification governs the civilization and this annex governs the repository. Neither overrides the Constitution.
