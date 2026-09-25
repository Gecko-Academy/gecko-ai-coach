"""Question-only quiz pages must not crowd answers out of keyword retrieval."""

import pytest

from gecko_ai_coach import corpus
from gecko_ai_coach.retrieve import BASELINE, Document, retrieve


@pytest.mark.parametrize("page_id", ["quiz", "unit/quiz", "unit/session/quiz"])
def test_quiz_questions_do_not_displace_explanations(page_id):
    """Repeated quiz questions previously ranked ahead of the page explaining fake."""
    docs = [
        Document(page_id, "Fake provider", "fake provider " * 20),
        Document("lesson", "Offline", "The fake provider works offline without a key."),
    ]
    assert [h.chunk.doc_id for h in retrieve("fake provider", docs)] == ["lesson"]


@pytest.mark.parametrize("page_id", ["quiz/introduction", "quiz-guide", "pop-quiz-notes"])
def test_related_explanations_are_not_classified_as_quiz_pages(page_id):
    """Matching a substring would hide actual explanations about quizzes."""
    docs = [Document(page_id, "Fake provider", "fake provider")]
    assert retrieve("fake provider", docs)[0].chunk.doc_id == page_id


def test_quiz_only_corpus_refuses_instead_of_quoting_a_question():
    """A quiz-only match cannot answer the learner and must allow refusal."""
    assert retrieve("fake provider", [Document("quiz", "Fake provider", "fake provider?")]) == []


def test_quiz_switch_restores_previous_ranking():
    """The measurement baseline must be able to include quiz candidates again."""
    docs = [Document("quiz", "Fake provider", "fake provider?")]
    assert retrieve("fake provider", docs, quiz_weight=1.0)
    assert retrieve("fake provider", docs, **BASELINE)
    assert BASELINE["quiz_weight"] == 1.0


def test_answer_keys_stay_stripped_even_when_quiz_ranking_is_enabled(tmp_path):
    """Disabling quiz downweighting must never restore an inline answer key."""
    (tmp_path / "quiz.mdx").write_text(
        "# Quiz\n\nfake provider?\n\n"
        '<Question choices={[{ text: "secret answer", correct: true }]} />',
        encoding="utf-8",
    )
    docs = corpus.load(tmp_path)
    hits = retrieve("fake provider", docs, quiz_weight=1.0)
    assert hits
    assert "secret answer" not in hits[0].chunk.text
    assert "correct: true" not in hits[0].chunk.text


# -- the escape hatch: a question that names a quiz gets the quiz --------------


@pytest.mark.parametrize("asked", ["quiz", "quizzes"])
def test_a_question_that_names_a_quiz_can_still_reach_one(asked):
    """A zero with no escape hatch is not a discount, it is a delete.

    "What does the session 8 quiz ask" is a question a student really types, and
    before this the only page that could answer it was the one page scored to
    nothing, so the retriever refused. `slides_weight` already solved the same
    problem on the same afternoon by restoring the full score when the question
    asks for the page kind by name; this is that, for quizzes.
    """
    docs = [
        Document("unit/session-08/quiz", "Session 8 quiz", "fake provider " * 20),
        Document("lesson", "Offline", "The fake provider works offline without a key."),
    ]
    hits = retrieve(f"which {asked} covers fake provider", docs)
    assert hits, "naming the page kind must not still refuse"
    assert hits[0].chunk.doc_id == "unit/session-08/quiz"


def test_the_escape_hatch_does_not_open_for_a_question_that_never_asked():
    """The guard is only a guard if the discount still applies by default.

    Without this the parametrised test above passes for the wrong reason -- a
    change that removed the discount entirely would satisfy it.
    """
    docs = [
        Document("unit/session-08/quiz", "Session 8 quiz", "fake provider " * 20),
        Document("lesson", "Offline", "The fake provider works offline without a key."),
    ]
    assert [h.chunk.doc_id for h in retrieve("fake provider", docs)] == ["lesson"]


def test_a_quiz_only_corpus_answers_a_question_that_asked_for_the_quiz():
    """The companion to `test_quiz_only_corpus_refuses_instead_of_quoting_a_question`.

    Refusing somebody who wanted an explanation is right. Refusing somebody who
    asked for the quiz by name is the bug this escape hatch closes.
    """
    docs = [Document("quiz", "Fake provider", "fake provider?")]
    assert retrieve("fake provider", docs) == []
    assert retrieve("quiz about fake provider", docs)
