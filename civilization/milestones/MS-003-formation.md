# Milestone 003 — Formation: three institutions and a protocol between them

**Date:** 2026-08-09
**Order:** 2, phase 4
**Exit gate:** exactly 3 institutions activated, one real inter-institution message schema, `memory/` wired into the loop, zero decorative functions, institutional snapshot archived
**Result:** passed

---

## The three

| Institution | Authority | Activated |
|---|---|---|
| `factory` | Sole creator of agents. May build and register; may not run or stop them. | Phase 2 |
| `safety` | Holds the stop authority and the boundary limits. May halt any execution. | Phase 1 |
| `memory` | Durable record of what agents perceived and concluded. May read and write; may not act. | Phase 4 |

Fourteen institutions remain dormant. They have full directory structures and complete
manifests, and no running code. Addressing one over the protocol fails at message
construction, not at delivery — a message to a dormant institution is never a valid
message.

## What "wired to the loop" was made to mean

The weak version of this gate would be a `memory/` module that the loop writes to. That
is satisfiable by a log. The version implemented is stronger and falsifiable: **memory
changes what the agent does next.**

`AgentFactory` consults memory *before* building. An agent that ran, was stopped, and is
rebuilt resumes from its remembered total instead of from zero. The test suite includes
the control case — the same agent built by a factory with no memory starts again from
zero — so a passing result cannot be a coincidence of arithmetic.

## Demonstration — actual output

```
-- factory asks memory to remember --
  accepted: True | recorded | {'written': True, 'total_writes': 1}
-- safety asks memory to recall --
  accepted: True | value: {'value': '2026-08-09', 'known': True}
-- an agent tries to have an agent built --
  accepted: False | refused under ARTICLE-002: an agent may not cause an agent to be created, including by asking an institution to do it
  registry entry for agent-666: None
-- a dormant institution is addressed --
  refused: recipient: institution 'economy' exists but is not activated; activated institutions are ['factory', 'memory', 'safety']
-- memory feeds the loop --
  run 1 resumed_from: 0 -> final output: 10
  run 2 resumed_from: 10 -> final output: 21
  memory holds running_total = 21 | last_run = {'cycles_completed': 2, 'final_output': 21, 'stopped_by': 'input_exhausted'}
```

Read directly from that output: run 1 resumed from 0 and reached 10; run 2 resumed from
10 and reached 21. Without memory the second run would have reached 11. The difference
between 21 and 11 is the entire content of this gate.

## The constitutional asymmetry in the protocol

Any activated institution may request `halt` over the protocol, because a stop that
requires the right credentials is a stop that arrives too late. There is no `release`
action in the protocol vocabulary at all — not a refused one, an absent one. Article I
reserves release to a human, and the protocol gives an institution nothing to reach for.

Article II is enforced at the protocol boundary as well as at the call boundary: a
`build_agent` request whose `authorised_by` names an agent is refused, and nothing is
registered.

## Test suite at this gate

```
Ran 70 tests in 0.156s

OK
```

70 tests: 12 policy, 17 unit, 41 integration (birth, population, formation).

## What is still absent

- No governance decision has ever been taken through `governance/` — phase 5.
- No fourth institution. Phase 5 will run a proposal to activate one through all nine
  stages of §7 and will deliberately **not** implement the result.
