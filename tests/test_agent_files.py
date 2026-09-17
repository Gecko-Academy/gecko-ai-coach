"""The files an assistant reads, and the promise that their links are real.

A coding assistant opens `llms.txt` or `AGENTS.md`, follows a path, and finds
nothing. It then guesses, which is the one behaviour this project is built to
prevent. So every local path these files name is checked here.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
AGENT_FILES = ("llms.txt", "AGENTS.md", "CLAUDE.md", ".github/PULL_REQUEST_TEMPLATE.md")
BLOB = re.compile(r"https://github\.com/Gecko-Academy/gecko-ai-coach/(?:blob|tree)/main/([^)\s]+)")
LOCAL = re.compile(r"\]\((?!https?:|#)([^)#]+)")


@pytest.mark.parametrize("name", AGENT_FILES)
def test_the_file_an_assistant_reads_is_there(name: str) -> None:
    assert (ROOT / name).is_file(), f"{name} is missing: an assistant told to read it finds nothing"


@pytest.mark.parametrize("name", (*AGENT_FILES, "README.md", "CONTRIBUTING.md"))
def test_every_path_it_names_exists(name: str) -> None:
    text = (ROOT / name).read_text(encoding="utf-8")
    named = {match for match in BLOB.findall(text)} | {
        match for match in LOCAL.findall(text) if not match.startswith("<")
    }
    missing = sorted(path for path in named if not (ROOT / path.rstrip("/")).exists())
    assert not missing, f"{name} points at paths that do not exist: {missing}"


def test_claude_md_points_at_the_policy_rather_than_copying_it() -> None:
    """Two copies of a policy become two policies, and the second one is never updated."""
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert "AGENTS.md" in text
    assert len(text.splitlines()) < 20, "CLAUDE.md is growing its own policy; keep it in AGENTS.md"


def test_the_issue_forms_are_valid() -> None:
    yaml = pytest.importorskip("yaml", reason="pyyaml is not a dependency of this project")
    for form in sorted((ROOT / ".github/ISSUE_TEMPLATE").glob("*.yml")):
        loaded = yaml.safe_load(form.read_text(encoding="utf-8"))
        assert isinstance(loaded, dict), form.name
        if form.name != "config.yml":
            assert loaded.get("name") and loaded.get("body"), form.name
