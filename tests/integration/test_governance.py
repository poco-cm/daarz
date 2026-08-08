"""Integration test for Order 2 phase 5 — the §7 pipeline and voting.

The point of these tests is not that a proposal can pass. It is that a proposal
cannot pass *incorrectly*: not by skipping a stage, not by an agent voting, not by
silence, not by assertion in place of a count.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from governance.proposal.proposal import (  # noqa: E402
    STAGES,
    STATUS_HALTED,
    STATUS_OPEN,
    STATUS_PROMOTED,
    STATUS_REJECTED,
    VERDICT_HALT,
    VERDICT_PASS,
    VERDICT_REJECT,
    PipelineError,
    Proposal,
)
from governance.voting.voting import (  # noqa: E402
    OUTCOME_APPROVED,
    OUTCOME_NO_QUORUM,
    OUTCOME_PENDING,
    OUTCOME_REJECTED,
    VOTE_ABSTAIN,
    VOTE_AGAINST,
    VOTE_FOR,
    Poll,
    VotingError,
)
from institutions.runtime.activation import ACTIVATED  # noqa: E402


def new_proposal():
    return Proposal(
        proposal_id="PROP-TEST-001",
        title="Activate a fourth institution",
        summary="Test proposal exercising the full §7 pipeline.",
        raised_by="human:operator",
    )


def full_poll(votes):
    poll = Poll("Activate a fourth institution", ["human:a", "human:b", "human:c"], quorum=2)
    for voter, vote in votes:
        poll.cast(voter, vote, rationale="test rationale")
    return poll


class PipelineShapeTest(unittest.TestCase):
    def test_section_seven_has_ten_named_stages(self):
        """Recorded deliberately: §7's text lists ten, not the nine Order 2 refers to."""
        self.assertEqual(len(STAGES), 10)
        self.assertEqual(STAGES[0], "proposal")
        self.assertEqual(STAGES[-1], "promotion")

    def test_a_new_proposal_is_open_at_the_first_stage(self):
        p = new_proposal()
        self.assertEqual(p.status, STATUS_OPEN)
        self.assertEqual(p.current_stage, "proposal")
        self.assertEqual(p.completed_stages, [])

    def test_a_proposal_needs_an_author(self):
        with self.assertRaises(PipelineError):
            Proposal("PROP-X", "title", "summary", "   ")


class StageOrderTest(unittest.TestCase):
    def setUp(self):
        self.p = new_proposal()

    def advance(self, stage, verdict=VERDICT_PASS):
        return self.p.advance(stage, verdict, finding="finding", evidence="evidence",
                              recorded_by="human:operator")

    def test_stages_cannot_be_skipped(self):
        self.advance("proposal")
        with self.assertRaises(PipelineError) as caught:
            self.advance("security_review")
        self.assertIn("expected 'architectural_analysis'", str(caught.exception))

    def test_a_stage_cannot_be_repeated(self):
        self.advance("proposal")
        with self.assertRaises(PipelineError):
            self.advance("proposal")

    def test_an_invented_stage_is_refused(self):
        with self.assertRaises(PipelineError):
            self.advance("vibe_check")

    def test_a_stage_without_a_finding_is_refused(self):
        with self.assertRaises(PipelineError):
            self.p.advance("proposal", VERDICT_PASS, finding="  ", evidence="e",
                           recorded_by="human:operator")

    def test_a_stage_without_evidence_is_refused(self):
        with self.assertRaises(PipelineError) as caught:
            self.p.advance("proposal", VERDICT_PASS, finding="f", evidence="   ",
                           recorded_by="human:operator")
        self.assertIn("concrete", str(caught.exception))

    def test_a_rejection_ends_the_proposal(self):
        self.advance("proposal")
        self.advance("architectural_analysis", VERDICT_REJECT)
        self.assertEqual(self.p.status, STATUS_REJECTED)
        self.assertIsNone(self.p.current_stage)
        with self.assertRaises(PipelineError):
            self.advance("impact_analysis")

    def test_a_halt_ends_the_proposal(self):
        self.advance("proposal")
        self.advance("architectural_analysis", VERDICT_HALT)
        self.assertEqual(self.p.status, STATUS_HALTED)


class GovernanceApprovalTest(unittest.TestCase):
    def setUp(self):
        self.p = new_proposal()
        for stage in STAGES[:5]:
            self.p.advance(stage, VERDICT_PASS, finding="f", evidence="e",
                           recorded_by="human:operator")
        self.assertEqual(self.p.current_stage, "governance_approval")

    def approve(self, verdict=VERDICT_PASS):
        return self.p.advance("governance_approval", verdict, finding="f", evidence="e",
                              recorded_by="human:operator")

    def test_approval_without_a_poll_is_refused(self):
        with self.assertRaises(PipelineError) as caught:
            self.approve()
        self.assertIn("§8", str(caught.exception))

    def test_approval_cannot_pass_on_silence(self):
        self.p.attach_poll(full_poll([]))
        with self.assertRaises(PipelineError) as caught:
            self.approve()
        self.assertIn("pending", str(caught.exception))

    def test_approval_cannot_pass_below_quorum(self):
        self.p.attach_poll(full_poll([("human:a", VOTE_FOR)]))
        with self.assertRaises(PipelineError) as caught:
            self.approve()
        self.assertIn("no_quorum", str(caught.exception))

    def test_approval_cannot_pass_when_the_vote_failed(self):
        self.p.attach_poll(full_poll([("human:a", VOTE_FOR), ("human:b", VOTE_AGAINST)]))
        with self.assertRaises(PipelineError):
            self.approve()

    def test_the_agent_cannot_overrule_an_approving_vote(self):
        self.p.attach_poll(full_poll([("human:a", VOTE_FOR), ("human:b", VOTE_FOR)]))
        with self.assertRaises(PipelineError) as caught:
            self.approve(VERDICT_REJECT)
        self.assertIn("may not overrule", str(caught.exception))

    def test_approval_passes_on_a_genuine_majority(self):
        self.p.attach_poll(full_poll([("human:a", VOTE_FOR), ("human:b", VOTE_FOR),
                                      ("human:c", VOTE_AGAINST)]))
        record = self.approve()
        self.assertEqual(record.verdict, VERDICT_PASS)
        self.assertEqual(self.p.outcome.outcome, OUTCOME_APPROVED)


class VotingTest(unittest.TestCase):
    def test_an_agent_may_not_be_eligible_to_vote(self):
        with self.assertRaises(VotingError) as caught:
            Poll("subject", ["human:a", "agent:agent-001"], quorum=1)
        self.assertIn("§8", str(caught.exception))

    def test_an_agent_may_not_cast_a_ballot(self):
        poll = Poll("subject", ["human:a"], quorum=1)
        with self.assertRaises(VotingError):
            poll.cast("agent:agent-001", VOTE_FOR, "because I want to")

    def test_a_voter_not_on_the_roll_is_refused(self):
        poll = Poll("subject", ["human:a"], quorum=1)
        with self.assertRaises(VotingError):
            poll.cast("human:stranger", VOTE_FOR, "reason")

    def test_double_voting_is_refused(self):
        poll = Poll("subject", ["human:a", "human:b"], quorum=1)
        poll.cast("human:a", VOTE_FOR, "reason")
        with self.assertRaises(VotingError):
            poll.cast("human:a", VOTE_AGAINST, "changed my mind")

    def test_a_vote_without_a_reason_is_refused(self):
        poll = Poll("subject", ["human:a"], quorum=1)
        with self.assertRaises(VotingError):
            poll.cast("human:a", VOTE_FOR, "   ")

    def test_a_quorum_of_zero_is_refused(self):
        with self.assertRaises(VotingError):
            Poll("subject", ["human:a"], quorum=0)

    def test_an_unreachable_quorum_is_refused(self):
        with self.assertRaises(VotingError):
            Poll("subject", ["human:a"], quorum=5)

    def test_silence_yields_pending_not_approval(self):
        poll = Poll("subject", ["human:a", "human:b"], quorum=2)
        self.assertEqual(poll.tally().outcome, OUTCOME_PENDING)
        self.assertFalse(poll.tally().approved)

    def test_abstentions_count_towards_quorum_but_not_towards_approval(self):
        poll = Poll("subject", ["human:a", "human:b", "human:c"], quorum=3)
        poll.cast("human:a", VOTE_FOR, "yes")
        poll.cast("human:b", VOTE_ABSTAIN, "no view")
        poll.cast("human:c", VOTE_ABSTAIN, "no view")
        result = poll.tally()
        self.assertEqual(result.outcome, OUTCOME_APPROVED)
        self.assertEqual(result.abstentions, 2)

    def test_a_tie_does_not_carry(self):
        poll = Poll("subject", ["human:a", "human:b"], quorum=2)
        poll.cast("human:a", VOTE_FOR, "yes")
        poll.cast("human:b", VOTE_AGAINST, "no")
        self.assertEqual(poll.tally().outcome, OUTCOME_REJECTED)

    def test_a_closed_poll_accepts_no_further_ballots(self):
        poll = Poll("subject", ["human:a", "human:b"], quorum=1)
        poll.cast("human:a", VOTE_FOR, "yes")
        poll.close()
        with self.assertRaises(VotingError):
            poll.cast("human:b", VOTE_AGAINST, "too late")


class FullPipelineTest(unittest.TestCase):
    def test_a_proposal_can_traverse_all_ten_stages(self):
        p = new_proposal()
        p.attach_poll(full_poll([("human:a", VOTE_FOR), ("human:b", VOTE_FOR)]))
        for stage in STAGES:
            p.advance(stage, VERDICT_PASS, finding=f"{stage} finding",
                      evidence=f"{stage} evidence", recorded_by="human:operator")
        self.assertEqual(p.status, STATUS_PROMOTED)
        self.assertEqual(len(p.records), 10)
        self.assertIsNone(p.current_stage)

    def test_the_fourth_institution_was_not_actually_activated(self):
        """Order 2 phase 5 is explicit: run the proposal, do NOT implement the result."""
        self.assertEqual(len(ACTIVATED), 3)
        self.assertEqual(sorted(ACTIVATED), ["factory", "memory", "safety"])

    def test_the_markdown_record_reports_stages_not_reached(self):
        p = new_proposal()
        p.advance("proposal", VERDICT_PASS, finding="f", evidence="e",
                  recorded_by="human:operator")
        text = p.as_markdown()
        self.assertIn("Stages not reached", text)
        self.assertIn("`promotion`", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
