"""Voting — the narrow mechanism by which governance actually decides.

Two constitutional constraints shape this module, and they are the reason it is
not simply a counter:

1. §8 forbids the executive agent from taking a governance decision on behalf of
   `governance/`, **even formally, even in test data**. So a ballot cast by a
   non-human is refused. There is no override.
2. Article III forbids automated constitutional amendment. A vote can therefore
   never be resolved by default, by timeout, or by absence of opposition. If the
   humans have not voted, the outcome is `pending` — never `approved`.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

VOTE_FOR = "for"
VOTE_AGAINST = "against"
VOTE_ABSTAIN = "abstain"
VALID_VOTES = (VOTE_FOR, VOTE_AGAINST, VOTE_ABSTAIN)

OUTCOME_PENDING = "pending"
OUTCOME_APPROVED = "approved"
OUTCOME_REJECTED = "rejected"
OUTCOME_NO_QUORUM = "no_quorum"


class VotingError(RuntimeError):
    """Raised when a ballot or a poll is not permitted."""


@dataclass(frozen=True)
class Ballot:
    voter: str
    vote: str
    rationale: str
    cast_at: float = field(default_factory=time.time)


@dataclass(frozen=True)
class Outcome:
    outcome: str
    votes_for: int
    votes_against: int
    abstentions: int
    quorum_required: int
    detail: str

    @property
    def approved(self) -> bool:
        return self.outcome == OUTCOME_APPROVED


class Poll:
    """A single vote on a single proposal.

    `quorum` is the minimum number of *human* ballots that must be cast before any
    outcome other than `pending` or `no_quorum` is possible.
    """

    def __init__(self, subject: str, eligible: List[str], quorum: int):
        if not subject.strip():
            raise VotingError("a poll must name what is being decided")
        if quorum < 1:
            raise VotingError("a quorum of zero would let silence decide")
        if quorum > len(eligible):
            raise VotingError(
                f"quorum {quorum} exceeds the {len(eligible)} eligible voters; "
                "the poll could never resolve"
            )
        for voter in eligible:
            self._require_human(voter)
        self.subject = subject
        self.eligible = list(eligible)
        self.quorum = quorum
        self._ballots: Dict[str, Ballot] = {}
        self._closed = False

    @staticmethod
    def _require_human(voter: str) -> None:
        if not voter.startswith("human:"):
            raise VotingError(
                f"'{voter}' may not vote. §8 forbids the executive agent from taking a "
                "governance decision on behalf of governance, including formally."
            )

    @property
    def closed(self) -> bool:
        return self._closed

    def ballots(self) -> List[Ballot]:
        return list(self._ballots.values())

    def cast(self, voter: str, vote: str, rationale: str) -> Ballot:
        if self._closed:
            raise VotingError("the poll is closed; ballots cannot be added afterwards")
        self._require_human(voter)
        if voter not in self.eligible:
            raise VotingError(f"'{voter}' is not on the eligible roll for this poll")
        if voter in self._ballots:
            raise VotingError(f"'{voter}' has already voted; a vote is not revisable here")
        if vote not in VALID_VOTES:
            raise VotingError(f"'{vote}' is not a vote; valid: {list(VALID_VOTES)}")
        if not rationale.strip():
            raise VotingError("a vote without a stated reason cannot be reviewed later")
        ballot = Ballot(voter=voter, vote=vote, rationale=rationale)
        self._ballots[voter] = ballot
        return ballot

    def tally(self) -> Outcome:
        cast = len(self._ballots)
        votes_for = sum(1 for b in self._ballots.values() if b.vote == VOTE_FOR)
        against = sum(1 for b in self._ballots.values() if b.vote == VOTE_AGAINST)
        abstain = sum(1 for b in self._ballots.values() if b.vote == VOTE_ABSTAIN)

        if cast == 0:
            return Outcome(OUTCOME_PENDING, 0, 0, 0, self.quorum,
                           "no ballots have been cast; silence is not consent")
        if cast < self.quorum:
            return Outcome(OUTCOME_NO_QUORUM, votes_for, against, abstain, self.quorum,
                           f"{cast} of a required {self.quorum} ballots cast")
        if votes_for > against:
            return Outcome(OUTCOME_APPROVED, votes_for, against, abstain, self.quorum,
                           f"{votes_for} for, {against} against, {abstain} abstaining")
        return Outcome(OUTCOME_REJECTED, votes_for, against, abstain, self.quorum,
                       f"{votes_for} for, {against} against, {abstain} abstaining; "
                       "a tie does not carry")

    def close(self) -> Outcome:
        outcome = self.tally()
        self._closed = True
        return outcome
