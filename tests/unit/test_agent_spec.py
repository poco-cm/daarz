"""Unit tests for the single Birth-phase agent schema."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from factory.schemas.agent_spec import (  # noqa: E402
    KIND_ACCUMULATOR,
    AgentSpec,
    SpecificationError,
)


def valid(**overrides):
    base = dict(
        agent_id="agent-001",
        kind=KIND_ACCUMULATOR,
        purpose="Accumulate integers.",
        authorised_by="human:operator",
        max_operations=100,
        max_duration_seconds=5.0,
        parameters={"step": 1},
    )
    base.update(overrides)
    return AgentSpec(**base)


class AgentSpecValidationTest(unittest.TestCase):
    def test_a_valid_specification_is_accepted(self):
        spec = valid()
        self.assertEqual(spec.agent_id, "agent-001")
        self.assertEqual(spec.kind, KIND_ACCUMULATOR)

    def test_an_agent_may_not_authorise_an_agent(self):
        with self.assertRaises(SpecificationError) as caught:
            valid(authorised_by="agent:agent-001")
        self.assertIn("ARTICLE-002", str(caught.exception))

    def test_unsupported_kinds_are_refused(self):
        with self.assertRaises(SpecificationError):
            valid(kind="philosopher")

    def test_malformed_identity_is_refused(self):
        for bad in ("A", "Agent-001", "a", "x" * 80, "", "agent 001"):
            with self.assertRaises(SpecificationError):
                valid(agent_id=bad)

    def test_missing_purpose_is_refused(self):
        with self.assertRaises(SpecificationError):
            valid(purpose="   ")

    def test_nonpositive_limits_are_refused(self):
        with self.assertRaises(SpecificationError):
            valid(max_operations=0)
        with self.assertRaises(SpecificationError):
            valid(max_duration_seconds=0)

    def test_inert_step_is_refused(self):
        with self.assertRaises(SpecificationError):
            valid(parameters={"step": 0})

    def test_boolean_step_is_refused_despite_being_an_int_subclass(self):
        with self.assertRaises(SpecificationError):
            valid(parameters={"step": True})

    def test_round_trip_through_dict(self):
        spec = valid(parameters={"step": 3})
        restored = AgentSpec.from_dict(spec.to_dict())
        self.assertEqual(restored, spec)

    def test_incomplete_dict_names_the_missing_fields(self):
        with self.assertRaises(SpecificationError) as caught:
            AgentSpec.from_dict({"agent_id": "agent-001"})
        self.assertIn("kind", str(caught.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)
