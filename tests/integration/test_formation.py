"""Integration test for Order 2 phase 4 (Formation).

Three activated institutions, one protocol, one memory that actually changes what
an agent does on its next run.
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agents.registry.registry import AgentRegistry  # noqa: E402
from factory.runtime.factory import AgentFactory  # noqa: E402
from factory.schemas.agent_spec import KIND_ACCUMULATOR, AgentSpec  # noqa: E402
from factory.services.handler import FactoryService  # noqa: E402
from institutions.runtime.activation import (  # noqa: E402
    ACTIVATED,
    ActivationError,
    activated_names,
    dormant_names,
    is_activated,
    require_activated,
)
from memory.runtime.memory import InstitutionalMemory  # noqa: E402
from memory.services.handler import MemoryService  # noqa: E402
from protocols.institution.requests.request import (  # noqa: E402
    ACTION_BUILD_AGENT,
    ACTION_HALT,
    ACTION_RECALL,
    ACTION_REMEMBER,
    InstitutionRequest,
    ProtocolError,
    RequestBus,
)
from runtime.loop.loop import STOP_KILL_SWITCH  # noqa: E402
from safety.kill_switch.kill_switch import KillSwitch  # noqa: E402
from safety.services.handler import SafetyService  # noqa: E402


class FormationTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.switch = KillSwitch(os.path.join(self.dir, "kill_switch.json"))
        self.registry = AgentRegistry(os.path.join(self.dir, "registry.json"))
        self.memory = InstitutionalMemory(os.path.join(self.dir, "memory.jsonl"))
        self.factory = AgentFactory(
            registry=self.registry,
            kill_switch=self.switch,
            log_dir=os.path.join(self.dir, "logs"),
            memory=self.memory,
        )
        self.bus = RequestBus()
        self.bus.register_handler("memory", MemoryService(self.memory))
        self.bus.register_handler("safety", SafetyService(self.switch))
        self.bus.register_handler(
            "factory",
            FactoryService(self.factory, input_source=lambda payload: range(1, 6)),
        )

    def spec(self, agent_id="agent-001", max_operations=1_000_000):
        return AgentSpec(
            agent_id=agent_id,
            kind=KIND_ACCUMULATOR,
            purpose="Formation phase integration agent.",
            authorised_by="human:operator",
            max_operations=max_operations,
            max_duration_seconds=60.0,
            parameters={"step": 1},
        )

    # -- activation --------------------------------------------------------

    def test_exactly_three_institutions_are_activated(self):
        self.assertEqual(len(ACTIVATED), 3)
        self.assertEqual(activated_names(), ["factory", "memory", "safety"])

    def test_the_other_fourteen_remain_dormant(self):
        self.assertEqual(len(dormant_names()), 14)
        self.assertIn("governance", dormant_names())
        self.assertFalse(is_activated("governance"))

    def test_a_dormant_institution_has_no_address(self):
        with self.assertRaises(ActivationError):
            require_activated("universities")

    def test_a_name_that_is_not_an_institution_is_rejected_distinctly(self):
        with self.assertRaises(ActivationError) as caught:
            require_activated("ministry_of_vibes")
        self.assertIn("§1", str(caught.exception))

    # -- protocol ----------------------------------------------------------

    def test_a_request_to_a_dormant_institution_is_refused_at_construction(self):
        with self.assertRaises(ProtocolError):
            InstitutionRequest(
                sender="factory", recipient="economy", action=ACTION_REMEMBER,
                payload={}, authorised_by="human:operator",
            )

    def test_an_action_sent_to_the_wrong_institution_is_refused(self):
        with self.assertRaises(ProtocolError):
            InstitutionRequest(
                sender="factory", recipient="safety", action=ACTION_REMEMBER,
                payload={}, authorised_by="human:operator",
            )

    def test_an_institution_may_not_message_itself(self):
        with self.assertRaises(ProtocolError):
            InstitutionRequest(
                sender="memory", recipient="memory", action=ACTION_REMEMBER,
                payload={}, authorised_by="human:operator",
            )

    def test_a_request_must_name_its_authoriser(self):
        with self.assertRaises(ProtocolError):
            InstitutionRequest(
                sender="factory", recipient="memory", action=ACTION_REMEMBER,
                payload={}, authorised_by="   ",
            )

    def test_factory_asks_memory_to_remember_and_then_recalls_it(self):
        write = InstitutionRequest(
            sender="factory", recipient="memory", action=ACTION_REMEMBER,
            payload={"subject": "civilization", "key": "founded", "value": "2026-08-09"},
            authorised_by="human:operator",
        )
        response = self.bus.send(write)
        self.assertTrue(response.accepted)

        read = InstitutionRequest(
            sender="safety", recipient="memory", action=ACTION_RECALL,
            payload={"subject": "civilization", "key": "founded"},
            authorised_by="human:operator",
        )
        recalled = self.bus.send(read)
        self.assertTrue(recalled.accepted)
        self.assertEqual(recalled.result["value"], "2026-08-09")
        self.assertTrue(recalled.result["known"])

    def test_recalling_an_unknown_key_is_answered_honestly_not_faked(self):
        response = self.bus.send(InstitutionRequest(
            sender="factory", recipient="memory", action=ACTION_RECALL,
            payload={"subject": "civilization", "key": "never_written"},
            authorised_by="human:operator",
        ))
        self.assertTrue(response.accepted)
        self.assertFalse(response.result["known"])
        self.assertIsNone(response.result["value"])

    def test_traffic_is_recorded_for_both_directions(self):
        self.bus.send(InstitutionRequest(
            sender="factory", recipient="memory", action=ACTION_REMEMBER,
            payload={"subject": "s", "key": "k", "value": 1},
            authorised_by="human:operator",
        ))
        traffic = self.bus.traffic()
        self.assertEqual(len(traffic), 1)
        self.assertEqual(traffic[0]["request"]["sender"], "factory")
        self.assertEqual(traffic[0]["response"]["responder"], "memory")

    def test_an_agent_cannot_cause_creation_through_the_protocol(self):
        response = self.bus.send(InstitutionRequest(
            sender="memory", recipient="factory", action=ACTION_BUILD_AGENT,
            payload={"spec": self.spec("agent-777").to_dict()},
            authorised_by="agent:agent-001",
        ))
        self.assertFalse(response.accepted)
        self.assertIn("ARTICLE-002", response.reason)
        self.assertIsNone(self.registry.get("agent-777"))

    def test_a_human_authorised_build_over_the_protocol_succeeds(self):
        response = self.bus.send(InstitutionRequest(
            sender="memory", recipient="factory", action=ACTION_BUILD_AGENT,
            payload={"spec": self.spec("agent-002").to_dict()},
            authorised_by="human:operator",
        ))
        self.assertTrue(response.accepted, response.reason)
        self.assertIsNotNone(self.registry.get("agent-002"))

    def test_safety_halts_on_request_but_offers_no_release_action(self):
        response = self.bus.send(InstitutionRequest(
            sender="memory", recipient="safety", action=ACTION_HALT,
            payload={"reason": "memory observed an inconsistency"},
            authorised_by="human:operator",
        ))
        self.assertTrue(response.accepted)
        self.assertTrue(self.switch.is_engaged())
        self.assertIn("ARTICLE-001", response.reason)

        with self.assertRaises(ProtocolError):
            InstitutionRequest(
                sender="memory", recipient="safety", action="release",
                payload={}, authorised_by="human:operator",
            )

    def test_an_unexplained_halt_is_refused(self):
        response = self.bus.send(InstitutionRequest(
            sender="memory", recipient="safety", action=ACTION_HALT,
            payload={"reason": "  "}, authorised_by="human:operator",
        ))
        self.assertFalse(response.accepted)
        self.assertFalse(self.switch.is_engaged())

    # -- memory wired to the loop -----------------------------------------

    def test_memory_records_the_end_of_every_run(self):
        agent = self.factory.create_and_register(self.spec(), inputs=[1, 2, 3, 4])
        agent.run()
        self.assertEqual(self.memory.recall("agent-001", "running_total"), 10)
        last = self.memory.recall("agent-001", "last_run")
        self.assertEqual(last["cycles_completed"], 4)
        self.assertEqual(last["stopped_by"], "input_exhausted")

    def test_a_stopped_agent_resumes_from_what_the_civilization_remembers(self):
        first = self.factory.create_and_register(self.spec(), inputs=[1, 2, 3, 4])
        first_result = first.run()
        self.assertEqual(first.resumed_from, 0, "nothing should have been remembered yet")
        self.assertEqual(first_result.final_output, 10)

        # Rebuild the same agent. Memory, not the caller, supplies the starting total.
        second = self.factory.rebuild_registered(self.spec(), inputs=[5, 6])
        self.assertEqual(second.resumed_from, 10, "memory did not reach the new run")
        second_result = second.run()
        self.assertEqual(second_result.final_output, 21, "10 remembered + 5 + 6")

    def test_without_memory_the_same_agent_starts_again_from_zero(self):
        """The control case. If this passed with a resumed total, memory would be a coincidence."""
        forgetful = AgentFactory(registry=self.registry, kill_switch=self.switch)
        first = forgetful.create_and_register(self.spec(), inputs=[1, 2, 3, 4])
        self.assertEqual(first.run().final_output, 10)
        second = forgetful.rebuild_registered(self.spec(), inputs=[5, 6])
        self.assertEqual(second.resumed_from, 0)
        self.assertEqual(second.run().final_output, 11, "no memory means starting over")

    def test_memory_survives_a_halt_mid_run(self):
        agent = self.factory.create_and_register(
            self.spec(max_operations=50), inputs=range(1, 1000)
        )
        self.bus.send(InstitutionRequest(
            sender="memory", recipient="safety", action=ACTION_HALT,
            payload={"reason": "formation test halt"}, authorised_by="human:operator",
        ))
        result = agent.run()
        self.assertEqual(result.stopped_by, STOP_KILL_SWITCH)
        # Even a run that completed zero cycles is remembered as having happened.
        self.assertEqual(self.memory.recall("agent-001", "last_run")["stopped_by"], STOP_KILL_SWITCH)

    def test_memory_keeps_history_not_just_the_latest_value(self):
        agent = self.factory.create_and_register(self.spec(), inputs=[1, 2])
        agent.run()
        history = self.memory.history("agent-001", "running_total")
        self.assertGreaterEqual(len(history), 1)
        self.assertTrue(all(record.written_by for record in history))


if __name__ == "__main__":
    unittest.main(verbosity=2)
