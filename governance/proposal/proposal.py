"""The §7 change pipeline, implemented as something a proposal must actually pass.

§7 of the founding specification states the pipeline literally:

    Proposal → Architectural Analysis → Impact Analysis → Compatibility Analysis
       → Security Review → Governance Approval → Migration Plan
       → Implementation → Tests → Promotion

That is **ten** named stages. Order 2 phase 5 refers to "the nine stages of §7";
the discrepancy is recorded rather than resolved by silently dropping one. All ten
named stages are implemented, because the specification text is the authority and
the order's count appears to be an arithmetic slip.

The pipeline is not a checklist. A stage cannot be skipped, cannot be entered
twice, cannot be entered out of order, and a rejection at any stage ends the
proposal there.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from governance.voting.voting import Outcome, Poll

STAGES: Tuple[str, ...] = (
    "proposal",
    "architectural_analysis",
    "impact_analysis",
    "compatibility_analysis",
    "security_review",
    "governance_approval",
    "migration_plan",
    "implementation",
    "tests",
    "promotion",
)

VERDICT_PASS = "pass"
VERDICT_REJECT = "reject"
VERDICT_HALT = "halt"
VALID_VERDICTS = (VERDICT_PASS, VERDICT_REJECT, VERDICT_HALT)

STATUS_OPEN = "open"
STATUS_REJECTED = "rejected"
STATUS_HALTED = "halted"
STATUS_PROMOTED = "promoted"


class PipelineError(RuntimeError):
    """Raised when the pipeline is used in a way §7 does not permit."""


@dataclass(frozen=True)
class StageRecord:
    stage: str
    verdict: str
    finding: str
    evidence: str
    recorded_by: str
    recorded_at: float = field(default_factory=time.time)


class Proposal:
    """A single architectural change, travelling through §7 under its own record."""

    def __init__(self, proposal_id: str, title: str, summary: str, raised_by: str):
        for name, value in (("proposal_id", proposal_id), ("title", title),
                            ("summary", summary), ("raised_by", raised_by)):
            if not value.strip():
                raise PipelineError(f"a proposal needs a {name}")
        self.proposal_id = proposal_id
        self.title = title
        self.summary = summary
        self.raised_by = raised_by
        self.opened_at = time.time()
        self._records: List[StageRecord] = []
        self._poll: Optional[Poll] = None
        self._outcome: Optional[Outcome] = None

    # -- state -------------------------------------------------------------

    @property
    def records(self) -> List[StageRecord]:
        return list(self._records)

    @property
    def completed_stages(self) -> List[str]:
        return [r.stage for r in self._records]

    @property
    def current_stage(self) -> Optional[str]:
        """The next stage this proposal is eligible to enter, or None if it is finished."""
        if self.status != STATUS_OPEN:
            return None
        done = len(self._records)
        if done >= len(STAGES):
            return None
        return STAGES[done]

    @property
    def status(self) -> str:
        for record in self._records:
            if record.verdict == VERDICT_REJECT:
                return STATUS_REJECTED
            if record.verdict == VERDICT_HALT:
                return STATUS_HALTED
        if len(self._records) == len(STAGES):
            return STATUS_PROMOTED
        return STATUS_OPEN

    @property
    def outcome(self) -> Optional[Outcome]:
        return self._outcome

    # -- movement ----------------------------------------------------------

    def attach_poll(self, poll: Poll) -> None:
        if self._poll is not None:
            raise PipelineError("this proposal already has a poll")
        self._poll = poll

    @property
    def poll(self) -> Optional[Poll]:
        return self._poll

    def advance(self, stage: str, verdict: str, finding: str, evidence: str,
                recorded_by: str) -> StageRecord:
        if self.status != STATUS_OPEN:
            raise PipelineError(
                f"proposal {self.proposal_id} is {self.status}; it cannot advance further"
            )
        if stage not in STAGES:
            raise PipelineError(f"'{stage}' is not a stage of §7")
        expected = self.current_stage
        if stage != expected:
            raise PipelineError(
                f"§7 is ordered: expected '{expected}', got '{stage}'. "
                "Stages cannot be skipped or reordered."
            )
        if verdict not in VALID_VERDICTS:
            raise PipelineError(f"'{verdict}' is not a verdict; valid: {list(VALID_VERDICTS)}")
        if not finding.strip():
            raise PipelineError(f"stage '{stage}' recorded no finding; §7 requires analysis")
        if not evidence.strip():
            raise PipelineError(
                f"stage '{stage}' recorded no evidence. Order 2: every step must produce "
                "something concrete."
            )
        if not recorded_by.strip():
            raise PipelineError("every stage record must name who recorded it")

        if stage == "governance_approval":
            self._check_approval_is_a_real_vote(verdict)

        record = StageRecord(
            stage=stage, verdict=verdict, finding=finding,
            evidence=evidence, recorded_by=recorded_by,
        )
        self._records.append(record)
        return record

    def _check_approval_is_a_real_vote(self, verdict: str) -> None:
        """Governance approval may not be asserted; it must be counted."""
        if self._poll is None:
            raise PipelineError(
                "governance_approval requires an attached poll. §8 forbids the executive "
                "agent from deciding on behalf of governance."
            )
        outcome = self._poll.tally()
        self._outcome = outcome
        if verdict == VERDICT_PASS and not outcome.approved:
            raise PipelineError(
                f"governance_approval cannot pass: the poll is '{outcome.outcome}' "
                f"({outcome.detail})"
            )
        if verdict in (VERDICT_REJECT, VERDICT_HALT) and outcome.approved:
            raise PipelineError(
                "the poll approved this proposal; the executive agent may not overrule it"
            )

    # -- reporting ---------------------------------------------------------

    def to_dict(self) -> Dict[str, object]:
        return {
            "proposal_id": self.proposal_id,
            "title": self.title,
            "summary": self.summary,
            "raised_by": self.raised_by,
            "status": self.status,
            "stages_completed": self.completed_stages,
            "stages_remaining": [s for s in STAGES if s not in self.completed_stages],
            "records": [
                {
                    "stage": r.stage,
                    "verdict": r.verdict,
                    "finding": r.finding,
                    "evidence": r.evidence,
                    "recorded_by": r.recorded_by,
                }
                for r in self._records
            ],
            "poll_outcome": None if self._outcome is None else self._outcome.outcome,
        }

    def as_markdown(self) -> str:
        lines = [
            f"# {self.proposal_id} — {self.title}",
            "",
            f"**Raised by:** {self.raised_by}  ",
            f"**Status:** {self.status}  ",
            f"**Stages completed:** {len(self._records)} of {len(STAGES)}",
            "",
            "## Summary",
            "",
            self.summary,
            "",
            "## §7 pipeline record",
            "",
            "| # | Stage | Verdict | Finding | Evidence |",
            "|---|---|---|---|---|",
        ]
        for index, record in enumerate(self._records, start=1):
            lines.append(
                f"| {index} | `{record.stage}` | **{record.verdict}** | "
                f"{record.finding} | {record.evidence} |"
            )
        remaining = [s for s in STAGES if s not in self.completed_stages]
        if remaining:
            lines += ["", "## Stages not reached", "", ", ".join(f"`{s}`" for s in remaining)]
        if self._outcome is not None:
            lines += [
                "",
                "## Vote",
                "",
                f"Outcome: **{self._outcome.outcome}** — {self._outcome.detail}",
            ]
        return "\n".join(lines) + "\n"
