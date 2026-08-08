# ai-civilization

Genesis scaffold for a governed, learnable AI civilization. The repository currently defines institutional boundaries, lifecycle phases, shared protocols, and archival structure before any live execution is permitted.

## Run & Operate

- `pnpm --filter @workspace/api-server run dev` — run the API server (port 5000)
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from the OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- Required env: `DATABASE_URL` — Postgres connection string

## Stack

- pnpm workspaces, Node.js 24, TypeScript 5.9
- API: Express 5
- DB: PostgreSQL + Drizzle ORM
- Validation: Zod (`zod/v4`), `drizzle-zod`
- API codegen: Orval (from OpenAPI spec)
- Build: esbuild (CJS bundle)

## Where things live

- `CIVILIZATION-GENESIS-SPECIFICATION` — source document for the Genesis scaffold.
- `SCAFFOLD_REPORT.md` — structural completion and compliance report.
- `constitution/`, `governance/`, `civilization/`, `factory/`, `universities/`, `research/`, `defense/`, `population/`, `institutions/`, `scientists/`, `economy/`, `knowledge/`, `memory/`, `learning/`, `safety/`, `security/`, `archive/` — full institutional pattern.
- `protocols/` — schema-only shared language locations.
- Root lightweight directories — infrastructure and tooling layers defined by the specification.

## Architecture decisions

- Genesis is documentation-only: no agent, runtime loop, permission, or governance authority is active.
- Full institutional structure is limited to the 17 institutions named by the specification.
- `civilization/institutions/` and `civilization/population/` are reference indexes, not duplicate sources of truth.
- Architectural changes must follow the documented proposal-to-promotion pipeline.

## Product

The product is in its Genesis phase. Its current capability is to make the future civilization's meaning, authority boundaries, lifecycle, protocols, and preservation model explicit and auditable.

## User preferences

- Do not implement live behavior before the Genesis scaffold is approved and the next phase is explicitly authorized.

## Gotchas

- Before any Birth-phase work, verify the scaffold report and preserve the 15-field manifest contract for every full institution.

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
