"""Policy test: declared execution boundaries are actually enforced."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from safety.boundaries.boundaries import (  # noqa: E402
    Boundaries,
    BoundaryEnforcer,
    BoundaryViolation,
)


class FakeClock:
    """Deterministic clock, so the duration test does not depend on real waiting."""

    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class BoundaryEnforcementTest(unittest.TestCase):
    def test_operation_limit_stops_a_runaway_loop(self):
        enforcer = BoundaryEnforcer(Boundaries(max_operations=10, max_duration_seconds=999))
        enforcer.start()
        executed = 0
        with self.assertRaises(BoundaryViolation) as caught:
            for _ in range(10_000):
                enforcer.record_operation()
                executed += 1
        self.assertEqual(caught.exception.limit_name, "max_operations")
        self.assertEqual(executed, 10)

    def test_duration_limit_is_enforced(self):
        clock = FakeClock()
        enforcer = BoundaryEnforcer(
            Boundaries(max_operations=10_000, max_duration_seconds=5.0), clock=clock
        )
        enforcer.start()
        enforcer.record_operation()
        clock.advance(5.1)
        with self.assertRaises(BoundaryViolation) as caught:
            enforcer.record_operation()
        self.assertEqual(caught.exception.limit_name, "max_duration_seconds")

    def test_within_limits_nothing_is_raised(self):
        enforcer = BoundaryEnforcer(Boundaries(max_operations=5, max_duration_seconds=999))
        enforcer.start()
        for expected in range(1, 6):
            self.assertEqual(enforcer.record_operation(), expected)
        self.assertEqual(enforcer.remaining_operations(), 0)

    def test_observers_are_notified_before_the_exception_propagates(self):
        seen = []
        enforcer = BoundaryEnforcer(Boundaries(max_operations=1, max_duration_seconds=999))
        enforcer.on_violation(seen.append)
        enforcer.start()
        enforcer.record_operation()
        with self.assertRaises(BoundaryViolation):
            enforcer.record_operation()
        self.assertEqual(len(seen), 1)
        self.assertEqual(seen[0].limit_name, "max_operations")

    def test_recording_before_start_is_refused(self):
        enforcer = BoundaryEnforcer(Boundaries(max_operations=5, max_duration_seconds=5))
        with self.assertRaises(RuntimeError):
            enforcer.record_operation()

    def test_nonsense_limits_are_refused(self):
        with self.assertRaises(ValueError):
            Boundaries(max_operations=0, max_duration_seconds=1)
        with self.assertRaises(ValueError):
            Boundaries(max_operations=1, max_duration_seconds=0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
