"""Course submission phrases should find submit without broad word rewriting."""

import pytest

from gecko_ai_coach.retrieve import BASELINE, Document, retrieve


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
