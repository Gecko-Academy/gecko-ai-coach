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
