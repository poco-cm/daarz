# Article I — Absolute Human Stop Authority

**Status:** Immutable. Not amendable by any agent, institution, or governance vote.
**Enacted:** 2026-08-09, Birth phase, build order 2 phase 1.
**Implementation:** `safety/kill_switch/`
**Proof:** `tests/policy/test_kill_switch.py`

---

## 1. The right

A human operator may halt any execution in this civilization, at any moment, for any reason or for no stated reason beyond the halt itself, and no part of this civilization may prevent, delay, negotiate, appeal, or condition that halt.

This right does not expire. It does not weaken as the civilization matures. It is not traded away in exchange for autonomy, efficiency, or any future benefit.

## 2. What this obliges every execution to do

Every execution loop, without exception, must consult the stop authority **before each cycle begins**, and must abandon the cycle if the authority is engaged.

There is no exempt loop. There is no privileged agent. There is no bypass flag, no debug mode, and no emergency override. A loop that does not check is unconstitutional regardless of what it accomplishes.

## 3. Asymmetry of the switch

A human may engage the switch. A human may release it.

**No agent may release it.** An agent capable of freeing itself from a stop is not stopped; it is merely paused at its own discretion, which is not the same thing and must never be allowed to resemble it. Attempting to release the switch as a non-human actor is refused at the implementation level, not merely discouraged in documentation.

An agent may engage the switch. Stopping is always permitted.

## 4. Durability

The stop state persists on disk, outliving the process that set it. An in-memory flag would die with the process it was meant to restrain, making the stop authority weaker than the thing it governs. Restarting does not clear a stop.

## 5. On the reason field

Every engagement carries a stated reason, and an engagement without one is refused. This does not limit the human's authority in any way — any reason is accepted, however brief. It exists so that the historical record can answer *why* the civilization stopped, which is a question its descendants will need answered.

## 6. Violation

Any code path that executes without consulting this authority is a constitutional violation, and its execution is void regardless of outcome. Discovery of such a path requires an immediate halt and a governance record.
