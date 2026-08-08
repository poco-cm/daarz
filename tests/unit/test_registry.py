"""Unit tests for the durable civil registry."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agents.registry.registry import (  # noqa: E402
    STATUS_ACTIVE,
    STATUS_STOPPED,
    AgentRegistry,
    RegistryError,
)
from factory.schemas.agent_spec import KIND_ACCUMULATOR, AgentSpec  # noqa: E402


def spec(agent_id="agent-001", authorised_by="human:operator"):
    return AgentSpec(
        agent_id=agent_id,
        kind=KIND_ACCUMULATOR,
        purpose="Accumulate integers.",
        authorised_by=authorised_by,
        max_operations=100,
        max_duration_seconds=5.0,
        parameters={"step": 1},
    )


class RegistryTest(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(tempfile.mkdtemp(), "registry.json")
        self.registry = AgentRegistry(self.path)

    def test_registration_persists_to_disk(self):
        self.registry.register(spec())
        reopened = AgentRegistry(self.path)
        record = reopened.get("agent-001")
        self.assertIsNotNone(record, "the record did not survive a fresh registry view")
        self.assertEqual(record.status, STATUS_ACTIVE)

    def test_unknown_agent_reads_as_none(self):
        self.assertIsNone(self.registry.get("agent-404"))

    def test_duplicate_registration_is_refused(self):
        self.registry.register(spec())
        with self.assertRaises(RegistryError):
            self.registry.register(spec())

    def test_active_ids_reflect_status_changes(self):
        self.registry.register(spec("agent-001"))
        self.registry.register(spec("agent-002"))
        self.assertEqual(self.registry.active_ids(), ["agent-001", "agent-002"])
        self.registry.set_status("agent-002", STATUS_STOPPED)
        self.assertEqual(self.registry.active_ids(), ["agent-001"])

    def test_unknown_status_is_refused(self):
        self.registry.register(spec())
        with self.assertRaises(RegistryError):
            self.registry.set_status("agent-001", "napping")

    def test_status_change_on_unregistered_agent_is_refused(self):
        with self.assertRaises(RegistryError):
            self.registry.set_status("agent-404", STATUS_STOPPED)

    def test_run_counter_increments(self):
        self.registry.register(spec())
        self.assertEqual(self.registry.get("agent-001").runs, 0)
        self.registry.record_run("agent-001")
        self.registry.record_run("agent-001")
        self.assertEqual(self.registry.get("agent-001").runs, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
