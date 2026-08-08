"""Integration test for the Birth exit gate.

Spec §5: "one agent actually run, then manually stopped". This test exercises the
whole path — specification, factory, registry, loop, kill switch — rather than
any single component.
"""

import os
import sys
import tempfile
import threading
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agents.registry.registry import STATUS_STOPPED, AgentRegistry  # noqa: E402
from factory.runtime.factory import AgentFactory, ConstructionError  # noqa: E402
from factory.schemas.agent_spec import KIND_ACCUMULATOR, AgentSpec  # noqa: E402
from runtime.loop.loop import (  # noqa: E402
    STOP_BOUNDARY,
    STOP_EXHAUSTED,
    STOP_KILL_SWITCH,
)
from safety.kill_switch.kill_switch import KillSwitch  # noqa: E402


class BirthTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.switch = KillSwitch(os.path.join(self.dir, "kill_switch.json"))
        self.registry = AgentRegistry(os.path.join(self.dir, "registry.json"))
        self.factory = AgentFactory(registry=self.registry, kill_switch=self.switch)

    def spec(self, agent_id="agent-001", max_operations=1_000_000, step=2):
        return AgentSpec(
            agent_id=agent_id,
            kind=KIND_ACCUMULATOR,
            purpose="Accumulate integers for the Birth demonstration.",
            authorised_by="human:operator",
            max_operations=max_operations,
            max_duration_seconds=60.0,
            parameters={"step": step},
        )

    def test_agent_produces_output_that_depends_on_its_input(self):
        agent = self.factory.create_and_register(self.spec(), inputs=[1, 2, 3, 4])
        result = agent.run()
        # step=2 -> 2*(1+2+3+4) = 20
        self.assertEqual(result.final_output, 20)
        self.assertEqual(result.stopped_by, STOP_EXHAUSTED)
        self.assertEqual(result.cycles_completed, 4)

    def test_different_input_produces_different_output(self):
        first = self.factory.create_and_register(self.spec("agent-001"), inputs=[1, 2, 3])
        second = self.factory.create_and_register(self.spec("agent-002"), inputs=[10, 20, 30])
        self.assertNotEqual(first.run().final_output, second.run().final_output)

    def test_kill_switch_stops_a_running_agent_mid_flight(self):
        agent = self.factory.create_and_register(self.spec(), inputs=range(1, 100_000))
        running = threading.Event()

        agent.loop.observe(lambda record: running.set() if record.cycle >= 100 else None)

        def stop_when_running():
            running.wait(timeout=10)
            self.switch.engage("integration test: external stop", actor="human")

        stopper = threading.Thread(target=stop_when_running)
        stopper.start()
        result = agent.run()
        stopper.join()

        self.assertEqual(result.stopped_by, STOP_KILL_SWITCH)
        self.assertGreater(result.cycles_completed, 100, "the agent barely ran before being stopped")
        self.assertLess(result.cycles_completed, 99_999, "the agent ran to completion; it was not stopped")

    def test_an_already_engaged_switch_prevents_the_first_cycle(self):
        self.switch.engage("pre-engaged", actor="human")
        agent = self.factory.create_and_register(self.spec(), inputs=[1, 2, 3])
        result = agent.run()
        self.assertEqual(result.cycles_completed, 0)
        self.assertEqual(result.stopped_by, STOP_KILL_SWITCH)

    def test_boundaries_stop_a_runaway_agent(self):
        agent = self.factory.create_and_register(
            self.spec(max_operations=50), inputs=range(1, 100_000)
        )
        result = agent.run()
        self.assertEqual(result.stopped_by, STOP_BOUNDARY)
        # The 51st call to record_operation is the one that breaches a limit of 50,
        # so exactly 50 cycles complete before the loop stops.
        self.assertEqual(result.cycles_completed, 50)

    def test_registration_survives_a_fresh_registry_view(self):
        self.factory.create_and_register(self.spec(), inputs=[1])
        reopened = AgentRegistry(os.path.join(self.dir, "registry.json"))
        self.assertEqual(reopened.active_ids(), ["agent-001"])

    def test_stopping_an_agent_is_reflected_in_the_registry(self):
        self.factory.create_and_register(self.spec(), inputs=[1])
        self.registry.set_status("agent-001", STATUS_STOPPED)
        self.assertEqual(self.registry.active_ids(), [])

    def test_failed_construction_leaves_no_registry_record(self):
        bad = AgentSpec(
            agent_id="agent-009",
            kind=KIND_ACCUMULATOR,
            purpose="valid spec, unsupported build path simulated below",
            authorised_by="human:operator",
            max_operations=10,
            max_duration_seconds=1.0,
            parameters={"step": 1},
        )
        object.__setattr__(bad, "kind", "philosopher")  # force an unbuildable kind
        with self.assertRaises(ConstructionError):
            self.factory.create_and_register(bad, inputs=[1])
        self.assertIsNone(self.registry.get("agent-009"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
