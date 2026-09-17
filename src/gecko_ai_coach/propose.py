"""Propose a question the coach gets wrong -- the smallest real contribution.

    ai-coach propose "what is a lane" --page unit0/runtime-lanes \\
        --pages ../dev3pack-cohort-2026-09/units/en

WHY THIS IS THE FIRST RUNG. A beginner does not need to understand BM25 to make
the coach better. Every question it answers wrong, written down with the page
that should have answered it, becomes a test the next change has to pass. That
is ten minutes, no code, and it is the input every algorithm change is measured
against -- which makes it the most useful contribution per minute there is.

WHAT IT CHECKS, so the pull request is right the first time:
  - the page you name exists (and suggests the nearest ids if it does not)
  - whether the coach already answers it -- if it does, there is nothing to add
  - the exact line to add, and with `--write`, it adds it for you

ONE FILE PER QUESTION. Many learners add questions in the same week. If they
all appended to one file, every second pull request would conflict on its last
line, and a beginner's first pull request would end in a merge conflict. A new
file never conflicts with another new file.
"""

from __future__ import annotations

import difflib
import json
import re
from dataclasses import dataclass
from pathlib import Path

from gecko_ai_coach.retrieve import Document, retrieve

#: Where community questions go, one file each. Measured and reported, never used
#: to decide whether a pull request passes -- so adding one never breaks a build.
COMMUNITY = Path("data/community")


class ProposalError(ValueError):
    """The question or the page is not usable, and the message says how to fix it."""


@dataclass(frozen=True)
class Proposal:
    question: str
    page: str
    got: tuple[str, ...]

    @property
    def already_answered(self) -> bool:
        return self.page in self.got

    @property
    def line(self) -> str:
        return json.dumps({"question": self.question, "expected": [self.page]})

    @property
    def filename(self) -> str:
        return slug(self.question) + ".jsonl"


def slug(question: str) -> str:
    """`What is a LANE?` -> `what-is-a-lane`. The same question gets the same name,
    so a duplicate shows up as a file that already exists."""
    return "-".join(re.findall(r"[a-z0-9]+", question.lower()))[:80] or "question"


def propose(question: str, page: str, documents: list[Document], top_k: int = 3) -> Proposal:
    question = question.strip()
    if len(question.split()) < 3:
        raise ProposalError("write the question the way a learner would ask it -- at least 3 words")
    ids = sorted({doc.doc_id for doc in documents})
    if page not in ids:
        close = difflib.get_close_matches(page, ids, n=3, cutoff=0.4)
        hint = f" Did you mean: {', '.join(close)}?" if close else ""
        raise ProposalError(f"no page called {page!r} in these pages.{hint}")
    got: list[str] = []
    for hit in retrieve(question, documents, top_k):
        if hit.chunk.doc_id not in got:
            got.append(hit.chunk.doc_id)
    return Proposal(question=question, page=page, got=tuple(got))


def already_listed(question: str, directory: Path) -> bool:
    """True when the question is in `directory`, or in a labelled set beside it.

    The sets beside it matter most: a held-out question copied into the community
    folder would be tuned on, and a held-out set that gets tuned on stops holding
    anything out.
    """
    if (directory / (slug(question) + ".jsonl")).exists():
        return True
    wanted = slug(question)
    files = [*directory.glob("*.jsonl"), *directory.parent.glob("*.jsonl")]
    for path in files:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.startswith("#"):
                if slug(json.loads(line).get("question", "")) == wanted:
                    return True
    return False


def render(proposal: Proposal) -> str:
    lines = [f'  question  "{proposal.question}"', f"  page      {proposal.page}"]
    lines.append(
        f"  coach got {', '.join(proposal.got) if proposal.got else '(nothing -- it refused)'}"
    )
    lines.append("")
    if proposal.already_answered:
        lines.append(
            "  ALREADY ANSWERED -- the coach finds that page. Nothing to add; try another question."
        )
    else:
        lines.append(
            f"  A REAL MISS -- worth adding. Save this as data/community/{proposal.filename}:"
        )
        lines.append("")
        lines.append(f"  {proposal.line}")
    return "\n".join(lines)


__all__ = ["COMMUNITY", "Proposal", "ProposalError", "already_listed", "propose", "render", "slug"]
