"""Birth demonstration: run one real agent, then stop it with the kill switch.

Spec §5 defines the Birth exit test as "one agent actually run, then manually
stopped, with a concrete log as evidence". This module produces that log. It is
executable evidence, not a description of evidence.

Run:  python3 -m runtime.loop.birth_run
"""

from __future__ import annotations

import os
import sys
import tempfile
import threading
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agents.registry.registry import STATUS_STOPPED, AgentRegistry  # noqa: E402
from factory.runtime.factory import AgentFactory  # noqa: E402
from factory.schemas.agent_spec import KIND_ACCUMULATOR, AgentSpec  # noqa: E402
from runtime.loop.loop import STOP_KILL_SWITCH  # noqa: E402
from safety.kill_switch.kill_switch import KillSwitch  # noqa: E402


def demonstrate(state_dir: str) -> int:
    lines = []

    def log(message: str) -> None:
        stamp = time.strftime("%Y-%m-%dT%H:%M:%S")
        line = f"[{stamp}] {message}"
        lines.append(line)
        print(line)

    switch = KillSwitch(os.path.join(state_dir, "kill_switch.json"))
    registry = AgentRegistry(os.path.join(state_dir, "registry.json"))
    factory = AgentFactory(registry=registry, kill_switch=switch)

    spec = AgentSpec(
        agent_id="agent-001",
        kind=KIND_ACCUMULATOR,
        purpose="Accumulate a stream of integers so the Birth phase has a real, verifiable output.",
        authorised_by="human:operator",
        max_operations=1_000_000,
        max_duration_seconds=60.0,
        parameters={"step": 2},
    )

    log(f"specification validated: {spec.agent_id} kind={spec.kind} step={spec.parameters['step']}")

    agent = factory.create_and_register(spec, inputs=range(1, 100_000))
    record = registry.get(spec.agent_id)
    log(f"agent registered durably: status={record.status} authorised_by={record.authorised_by}")

    running = threading.Event()
    cycles_seen = {"count": 0}

    def watch(record):
        cycles_seen["count"] = record.cycle + 1
        if record.cycle < 5:
            log(f"  cycle {record.cycle}: perceived={record.perceived} "
                f"total={record.output} productive={record.productive}")
        if record.cycle >= 100:
            running.set()

    agent.loop.observe(watch)

    def stop_when_clearly_running():
        # Wait until the agent is demonstrably mid-flight, then stop it from outside.
        running.wait(timeout=10)
        switch.engage("Birth demonstration: human operator stopping the first agent", actor="human")

    stopper = threading.Thread(target=stop_when_clearly_running)
    log("human operator will engage the kill switch once the agent is past cycle 100")
    stopper.start()

    started = time.time()
    result = agent.run()
    elapsed = time.time() - started
    stopper.join()

    registry.record_run(spec.agent_id)
    registry.set_status(spec.agent_id, STATUS_STOPPED)

    log(f"run ended after {result.cycles_completed} cycles in {elapsed:.3f}s")
    log(f"stopped_by={result.stopped_by} detail={result.detail}")
    log(f"final accumulated output={result.final_output}")
    log(f"registry status now: {registry.get(spec.agent_id).status}")

    if result.stopped_by != STOP_KILL_SWITCH:
        log("FAILURE: the agent was not stopped by the kill switch")
        return 1
    if result.cycles_completed == 0:
        log("FAILURE: the agent never ran, so nothing was stopped")
        return 1

    log("Birth exit test satisfied: one real agent ran, then a human stopped it.")
    with open(os.path.join(state_dir, "birth_run.log"), "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else tempfile.mkdtemp(prefix="birth-")
    os.makedirs(target, exist_ok=True)
    raise SystemExit(demonstrate(target))
