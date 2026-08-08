"""Integration test for Order 2 phase 3.

Two agents, running under one registry, counted by a live census, moved through a
lifecycle, logged per cycle, and one of them driven into a boundary breach that
must raise a real alert.
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agents.registry.registry import AgentRegistry  # noqa: E402
from factory.runtime.factory import AgentFactory  # noqa: E402
from factory.schemas.agent_spec import KIND_ACCUMULATOR, AgentSpec  # noqa: E402
from observability.alerts.alerts import SEVERITY_CRITICAL, AlertBus  # noqa: E402
from population.census.census import PopulationCensus  # noqa: E402
from population.lifecycle.lifecycle import AgentLifecycle, LifecycleError  # noqa: E402
from runtime.loop.loop import STOP_BOUNDARY, STOP_EXHAUSTED  # noqa: E402
from safety.kill_switch.kill_switch import KillSwitch  # noqa: E402


class PopulationTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.switch = KillSwitch(os.path.join(self.dir, "kill_switch.json"))
        self.registry = AgentRegistry(os.path.join(self.dir, "registry.json"))
        self.bus = AlertBus(os.path.join(self.dir, "alerts.jsonl"))
        self.factory = AgentFactory(
            registry=self.registry,
            kill_switch=self.switch,
            log_dir=os.path.join(self.dir, "logs"),
            alert_bus=self.bus,
        )
        self.census = PopulationCensus(self.registry)
        self.lifecycle = AgentLifecycle(self.registry)

    def spec(self, agent_id, max_operations=1000, step=1):
        return AgentSpec(
            agent_id=agent_id,
            kind=KIND_ACCUMULATOR,
            purpose="Population integration test agent.",
            authorised_by="human:operator",
            max_operations=max_operations,
            max_duration_seconds=60.0,
            parameters={"step": step},
        )

    # -- census ------------------------------------------------------------

    def test_census_counts_zero_before_any_agent_exists(self):
        self.assertEqual(self.census.active_count(), 0)
        self.assertEqual(self.census.take().total, 0)

    def test_census_tracks_two_agents_and_reacts_to_a_stop(self):
        self.factory.create_and_register(self.spec("agent-001"), inputs=[1, 2, 3])
        self.assertEqual(self.census.active_count(), 1)
        self.factory.create_and_register(self.spec("agent-002"), inputs=[4, 5, 6])

        snapshot = self.census.take()
        self.assertEqual(snapshot.active, 2)
        self.assertEqual(snapshot.total, 2)
        self.assertEqual(snapshot.active_ids, ["agent-001", "agent-002"])

        self.lifecycle.stop("agent-001")
        after = self.census.take()
        self.assertEqual(after.active, 1)
        self.assertEqual(after.stopped, 1)
        self.assertEqual(after.total, 2, "a stopped agent still exists; it is not erased")
        self.assertEqual(after.active_ids, ["agent-002"])

    def test_census_is_a_live_query_not_a_stored_number(self):
        self.factory.create_and_register(self.spec("agent-001"), inputs=[1])
        first = self.census.take()
        # Change the registry behind the census's back — no method on the census is called.
        AgentRegistry(os.path.join(self.dir, "registry.json")).set_status("agent-001", "stopped")
        second = self.census.take()
        self.assertEqual(first.active, 1)
        self.assertEqual(second.active, 0, "the census returned a cached count")

    def test_census_by_kind(self):
        self.factory.create_and_register(self.spec("agent-001"), inputs=[1])
        self.factory.create_and_register(self.spec("agent-002"), inputs=[1])
        self.assertEqual(self.census.by_kind(), {KIND_ACCUMULATOR: 2})

    # -- lifecycle ---------------------------------------------------------

    def test_lifecycle_has_exactly_two_states(self):
        self.factory.create_and_register(self.spec("agent-001"), inputs=[1])
        self.assertEqual(self.lifecycle.state_of("agent-001"), "active")
        self.assertEqual(self.lifecycle.stop("agent-001").current, "stopped")
        self.assertEqual(self.lifecycle.activate("agent-001").current, "active")

    def test_redundant_transition_is_refused(self):
        self.factory.create_and_register(self.spec("agent-001"), inputs=[1])
        with self.assertRaises(LifecycleError):
            self.lifecycle.activate("agent-001")

    def test_lifecycle_of_unregistered_agent_is_refused(self):
        with self.assertRaises(LifecycleError):
            self.lifecycle.stop("agent-404")

    # -- logging -----------------------------------------------------------

    def test_every_cycle_of_both_agents_is_logged(self):
        first = self.factory.create_and_register(self.spec("agent-001"), inputs=[1, 2, 3])
        second = self.factory.create_and_register(self.spec("agent-002"), inputs=[7, 8])

        first_result = first.run()
        second_result = second.run()

        self.assertEqual(first_result.stopped_by, STOP_EXHAUSTED)
        self.assertEqual(first.log.cycles_logged(), 3)
        self.assertEqual(second.log.cycles_logged(), 2)

        entries = first.log.entries()
        self.assertEqual(entries[0]["perceived"], 1)
        self.assertEqual(entries[-1]["event"], "run_end")
        self.assertEqual(entries[-1]["final_output"], 6)
        self.assertEqual(second_result.final_output, 15)

        # Each agent writes to its own file; the logs are not shared or overwritten.
        self.assertNotEqual(first.log.path, second.log.path)

    def test_log_records_are_written_to_disk_and_readable_independently(self):
        agent = self.factory.create_and_register(self.spec("agent-001"), inputs=[5, 6])
        agent.run()
        with open(agent.log.path, "r", encoding="utf-8") as handle:
            lines = [line for line in handle if line.strip()]
        self.assertEqual(len(lines), 3, "expected 2 cycle records plus one run_end record")

    # -- alerts ------------------------------------------------------------

    def test_a_boundary_breach_raises_exactly_one_real_alert(self):
        agent = self.factory.create_and_register(
            self.spec("agent-001", max_operations=10), inputs=range(1, 1000)
        )
        self.assertEqual(self.bus.count(), 0, "an alert fired before anything went wrong")

        result = agent.run()

        self.assertEqual(result.stopped_by, STOP_BOUNDARY)
        self.assertEqual(self.bus.count(), 1)
        alert = self.bus.raised()[0]
        self.assertEqual(alert.severity, SEVERITY_CRITICAL)
        self.assertEqual(alert.source, "safety/boundaries")
        self.assertEqual(alert.context["agent_id"], "agent-001")
        self.assertEqual(alert.context["limit_name"], "max_operations")
        self.assertEqual(alert.context["limit_value"], 10)
        self.assertIn("agent-001", alert.subject)

    def test_no_alert_fires_when_agents_stay_within_their_limits(self):
        agent = self.factory.create_and_register(self.spec("agent-001"), inputs=[1, 2, 3])
        agent.run()
        self.assertEqual(self.bus.count(), 0)
        self.assertEqual(self.bus.by_severity(SEVERITY_CRITICAL), [])

    def test_alerts_are_persisted_and_subscribers_are_notified(self):
        seen = []
        self.bus.subscribe(seen.append)
        agent = self.factory.create_and_register(
            self.spec("agent-001", max_operations=5), inputs=range(1, 100)
        )
        agent.run()
        self.assertEqual(len(seen), 1)
        with open(os.path.join(self.dir, "alerts.jsonl"), "r", encoding="utf-8") as handle:
            self.assertEqual(len([line for line in handle if line.strip()]), 1)

    def test_the_breach_is_also_in_the_execution_log(self):
        agent = self.factory.create_and_register(
            self.spec("agent-001", max_operations=8), inputs=range(1, 100)
        )
        agent.run()
        events = [entry["event"] for entry in agent.log.entries()]
        self.assertIn("boundary_violation", events)
        self.assertIn("run_end", events)


if __name__ == "__main__":
    unittest.main(verbosity=2)
