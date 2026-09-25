"""Course submission phrases should find submit without broad word rewriting."""

import pytest

from gecko_ai_coach.retrieve import (
    BASELINE,
    Document,
    _submission_text,
    retrieve,
)


@pytest.mark.parametrize(
    "question",
    [
        "how do I hand in a session",
        "hand in homework",
        "how do I hand my work in",
        "hand your notebook in",
        "HAND IN AN ASSIGNMENT",
        "hand\tmy\twork\tin",
    ],
)
def test_submission_phrases_find_the_submission_page(question):
    """Learners saying hand in previously missed pages using submit."""
    docs = [
        Document(
            "submit", "Submitting", "Submit a session, homework, work, notebook or assignment."
        )
    ]
    assert retrieve(question, docs)[0].chunk.doc_id == "submit"


@pytest.mark.parametrize(
    "question",
    [
        "handbook installation",
        "walk hand in hand",
        "hand tools",
        "set up a meeting",
    ],
)
def test_unrelated_phrases_keep_literal_ranking(question):
    """Substring and broad setup rewrites can silently alter unrelated intent."""
    docs = [Document("literal", question, question), Document("submit", "Submit", "submit")]
    assert retrieve(question, docs) == retrieve(question, docs, submission_synonyms=False)


def test_submission_alias_does_not_bypass_refusal():
    """A submission word must not make a mostly unrelated query answerable."""
    docs = [Document("submit", "Submit", "submit homework")]
    assert retrieve("hand in kubernetes ingress controller configuration", docs) == []


def test_submission_switch_and_baseline_keep_the_original_miss():
    """Disabling improvements must retain the literal vocabulary gap for measurement."""
    docs = [Document("submit", "Submit", "submit")]
    assert retrieve("hand in", docs)
    assert retrieve("hand in", docs, submission_synonyms=False) == []
    assert retrieve("hand in", docs, **BASELINE) == []


def test_submission_query_matches_a_hand_in_title():
    """Query-only rewriting missed the course title Handing work in."""
    docs = [Document("submit", "Handing work in", "Open the website.")]
    assert retrieve("submit work", docs)[0].chunk.doc_id == "submit"
    assert retrieve("submit", docs, submission_synonyms=False) == []


# -- the edge of the rule, found by asking it questions it was not written for --
#
# The review that asked for these said it plainly: one held-out set that happens
# to contain no "hand in" phrasing does not TEST the rule, it just does not trip
# it. Session 7 of the course teaches this exact trap with our own numbers --
# query expansion went to 100% on the tuned set and took four unseen queries from
# 75% to 0% at rank 1.
#
# So these are questions written to break it. The first version broke on three of
# them, measured 2026-09-25, and each failure is named on the case that now guards
# it. They stay here whether or not anyone asks a coach about a clock.


@pytest.mark.parametrize(
    "question",
    [
        "hand in hand with the exercise",
        "which hand in the diagram is the pointer",
        "the second hand in the clock diagram",
        "which hands in the photo are raised",
        "show of hands in the room",
    ],
)
def test_the_rule_declines_when_hand_is_a_noun(question):
    """FALSE POSITIVES. "which hand in the diagram is the pointer" became "which
    submit the diagram", and "the second hand in the clock diagram" became "the
    second submit the clock diagram". Neither question is about submitting.

    What fixed it is grammar, not a longer list: a bare `hand` needs one of the
    things you can hand in to follow it, because a bare `hand` is also a body part
    and a clock part. `hands` is out for the same reason.
    """
    assert _submission_text(question) == question


@pytest.mark.parametrize(
    "question",
    [
        "I handed my notebook in last week, where does it go",
        "I am handing my notebook in tomorrow",
        "where do I hand in the session 3 notebook",
        "how do I hand my work in",
        "how do I hand in a session",
    ],
)
def test_the_rule_fires_on_the_ways_people_really_write_it(question):
    """FALSE NEGATIVE. "I handed my notebook in last week" went through untouched:
    the first version knew `hand` and `handing` and not `handed`, so it missed the
    tense a student uses when the thing has already gone wrong -- which is exactly
    when they ask a coach."""
    assert _submission_text(question) != question
    assert "submit" in _submission_text(question)


def test_an_unambiguous_verb_needs_no_object():
    """The branch that costs nothing and pays for itself.

    Requiring an object on EVERY branch was strictly safer and lost a real
    question: `how do I hand in a session` stopped finding `unit0/how-to-submit`,
    because that page says "handing in again is the normal case" and nothing in
    the object list follows. `handing` and `handed` cannot be a body part, so they
    are safe alone where `hand` is not. dev3pack went 59% -> 53% -> 59% across the
    three versions; this is what put it back.
    """
    assert "submit" in _submission_text("handing in again is the normal case")
    assert "submit" in _submission_text("every notebook can be handed in")
    # ...and the bare noun still declines, which is the whole point of the split.
    assert _submission_text("hand in hand") == "hand in hand"


def test_the_page_side_cost_is_cached_away():
    """This runs over every chunk body and title on every question, so its cost is
    proportional to the corpus, per query, in the code that answers people on
    Telegram. Measured on 158 pages / 688 KB: 30.3 ms/query without the rewrite,
    36.0 with it, 31.9 with it cached. After the object requirement removed most
    of the matching work, on and off measure the same.

    The assertion is on the mechanism rather than a duration, because a timing
    test on CI is a flake generator."""
    _submission_text.cache_clear()
    page = "Handing work in. Every notebook can be handed in." * 10
    first = _submission_text(page)
    for _ in range(50):
        assert _submission_text(page) == first
    info = _submission_text.cache_info()
    assert info.misses == 1, "the page text was re-scanned instead of being reused"
    assert info.hits == 50
