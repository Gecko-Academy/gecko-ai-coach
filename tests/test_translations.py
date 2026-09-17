"""Translations of the README: prose changes, commands never do.

A beginner copies commands from whichever README they can read. A command that
was translated along with the prose, or that drifted from the English one, fails
on their machine with no hint why -- so every code block in a translation must
appear, byte for byte, in the English README or CONTRIBUTING.md.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
TRANSLATIONS = sorted(ROOT.glob("README.*.md"))
FENCE = re.compile(r"^```[^\n]*\n(.*?)^```", re.MULTILINE | re.DOTALL)


def _blocks(path: Path) -> list[str]:
    return FENCE.findall(path.read_text(encoding="utf-8"))


def test_there_are_translations_to_check() -> None:
    assert TRANSLATIONS, "no README.<lang>.md found -- the glob or the files moved"


@pytest.mark.parametrize("translation", TRANSLATIONS, ids=lambda p: p.name)
def test_every_code_block_is_copied_from_english(translation: Path) -> None:
    english = "\n".join(_blocks(ROOT / "README.md") + _blocks(ROOT / "CONTRIBUTING.md"))
    for block in _blocks(translation):
        assert block in english, (
            f"{translation.name}: this block is not in the English docs:\n{block}"
        )


@pytest.mark.parametrize("translation", TRANSLATIONS, ids=lambda p: p.name)
def test_every_translation_names_the_commit_it_came_from(translation: Path) -> None:
    first = translation.read_text(encoding="utf-8").splitlines()[0]
    assert re.fullmatch(r"<!-- translated from README\.md at [0-9a-f]{7,40} -->", first), (
        f"{translation.name} must start with <!-- translated from README.md at <commit> -->"
    )


@pytest.mark.parametrize("translation", TRANSLATIONS, ids=lambda p: p.name)
def test_the_english_readme_links_to_every_translation(translation: Path) -> None:
    assert f"]({translation.name})" in (ROOT / "README.md").read_text(encoding="utf-8")
