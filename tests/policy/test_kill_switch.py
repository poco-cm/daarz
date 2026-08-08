"""Policy test: the kill switch actually stops a running execution.

Order 2 phase 1 step 4 requires proof that invoking the kill switch halts a
live execution mid-flight — not that a boolean flips. The test therefore runs a
real loop and engages the switch from a separate thread while the loop is
running, then asserts the loop stopped early.
"""

import os
import sys
import tempfile
import threading
import time
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from safety.kill_switch.kill_switch import ExecutionHalted, KillSwitch  # noqa: E402


class KillSwitchHaltsExecutionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.path = os.path.join(self.tmp, "kill_switch.json")
        self.switch = KillSwitch(self.path)

    def test_clear_switch_does_not_halt(self):
        self.assertFalse(self.switch.is_engaged())
        self.switch.assert_clear()  # must not raise

    def test_engaged_switch_halts_a_running_loop(self):
        completed_cycles = []
        planned_cycles = 2000
        halted = {}

        def engage_after_delay():
            time.sleep(0.05)
            self.switch.engage("policy test: proving the stop authority is real", actor="human")

        stopper = threading.Thread(target=engage_after_delay)
        stopper.start()

        try:
            for cycle in range(planned_cycles):
                self.switch.assert_clear()  # checked before every cycle, no exemption
                completed_cycles.append(cycle)
                time.sleep(0.001)
        except ExecutionHalted as halt:
            halted["reason"] = halt.reason
            halted["actor"] = halt.actor
        finally:
            stopper.join()

        self.assertIn("reason", halted, "the loop ran to completion; the switch did not stop it")
        self.assertEqual(halted["actor"], "human")
        self.assertGreater(len(completed_cycles), 0, "the loop never started, so nothing was stopped")
        self.assertLess(
            len(completed_cycles),
            planned_cycles,
            "the loop completed all planned cycles, so it was not actually halted",
        )

    def test_state_survives_a_new_process_view(self):
        self.switch.engage("durability check", actor="human")
        reopened = KillSwitch(self.path)
        self.assertTrue(reopened.is_engaged())
        self.assertEqual(reopened.read().reason, "durability check")

    def test_agent_cannot_release_the_switch(self):
        self.switch.engage("agent must not be able to free itself", actor="human")
        with self.assertRaises(PermissionError):
            self.switch.release(actor="agent-001")
        self.assertTrue(self.switch.is_engaged())

    def test_human_can_release_the_switch(self):
        self.switch.engage("temporary", actor="human")
        self.switch.release(actor="human")
        self.assertFalse(self.switch.is_engaged())

    def test_engagement_requires_a_reason(self):
        with self.assertRaises(ValueError):
            self.switch.engage("", actor="human")


if __name__ == "__main__":
    unittest.main(verbosity=2)
