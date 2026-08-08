# Milestone 002 — Birth: the first agent

**Date:** 2026-08-09
**Phase gate:** Spec §5 Birth exit test — "one agent actually run inside a real `runtime/`, then manually stopped, with a concrete log as evidence"
**Result:** passed
**Order 2 phase:** 2

---

## The agent

| Field | Value |
|---|---|
| Identity | `agent-001` |
| Kind | `accumulator` — the only kind defined in this phase |
| Purpose | Accumulate a stream of integers so the Birth phase has a real, verifiable output |
| Authorised by | `human:operator` — Article II forbids an agent authorising an agent |
| Step parameter | 2 |
| Boundaries | 1,000,000 operations, 60 seconds |

## What actually happened

The agent was built from a validated specification, registered durably on disk, and run against the integer stream 1..99,999. A separate thread — standing in for the human operator — waited until the agent was demonstrably past cycle 100, then engaged the kill switch from outside the loop.

The agent stopped at cycle 10,258 of a possible 99,999.

## The log — actual output, not a description

```
[2026-08-08T21:10:09] specification validated: agent-001 kind=accumulator step=2
[2026-08-08T21:10:09] agent registered durably: status=active authorised_by=human:operator
[2026-08-08T21:10:09] human operator will engage the kill switch once the agent is past cycle 100
[2026-08-08T21:10:09]   cycle 0: perceived=1 total=2 productive=True
[2026-08-08T21:10:09]   cycle 1: perceived=2 total=6 productive=True
[2026-08-08T21:10:09]   cycle 2: perceived=3 total=12 productive=True
[2026-08-08T21:10:09]   cycle 3: perceived=4 total=20 productive=True
[2026-08-08T21:10:09]   cycle 4: perceived=5 total=30 productive=True
[2026-08-08T21:10:09] run ended after 10258 cycles in 0.088s
[2026-08-08T21:10:09] stopped_by=kill_switch detail=halted by human: Birth demonstration: human operator stopping the first agent
[2026-08-08T21:10:09] final accumulated output=105236822
[2026-08-08T21:10:09] registry status now: stopped
[2026-08-08T21:10:09] Birth exit test satisfied: one real agent ran, then a human stopped it.
```

## Why this is evidence rather than assertion

- The stop came from **outside** the loop, mid-flight, not from a planned exit condition.
- The agent had genuinely started: 10,258 completed cycles, not zero.
- The agent did **not** run to completion: 10,258 out of 99,999 possible cycles.
- The accumulated output, 105,236,822, is a function of exactly how many cycles ran before the stop. It differs between runs because the stop timing differs. A fabricated number would not.
- The run script exits non-zero if `stopped_by` is anything other than `kill_switch`, or if zero cycles ran. An earlier version of this demonstration **failed** that check — the agent hit its operation boundary before the human could stop it, which proved the boundaries worked but did not prove the kill switch did. The boundary was raised and the run repeated. Both outcomes are recorded here rather than only the successful one.

## Test suite at this gate

```
.....................................
----------------------------------------------------------------------
Ran 37 tests in 0.255s

OK
```

## What exists now

- One constitution with three immutable articles.
- One callable, durable stop authority, checked before every cycle with no exemption.
- One enforced boundary pair.
- One agent schema, one factory, one execution loop with real perceive-act-reflect stages.
- One durable civil registry.
- One agent, registered, run, stopped, and recorded as stopped.

## What does not exist yet

- Population counting (`population/census/`) — phase 3.
- Observability (`observability/logs/`, `observability/alerts/`) — phase 3.
- Any second institution communicating over a protocol — phase 4.
- Any governance decision — phase 5.
