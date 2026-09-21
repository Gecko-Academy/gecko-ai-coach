"""Slides should not crowd out equally relevant course explanations."""

import pytest

from gecko_ai_coach.retrieve import BASELINE, Document, retrieve


@pytest.mark.parametrize(
    "topic", ["week zero", "week one", "week three", "demo day", "tools", "models"]
)
def test_explanation_wins_over_equally_relevant_slides(topic):
    """A slides page tying an explanatory page must not take its first slot."""
    docs = [Document("a/slides", topic, topic), Document("z/explanation", topic, topic)]
    assert retrieve(topic, docs, 1)[0].chunk.doc_id == "z/explanation"
    assert retrieve(topic, docs, 1, slides_weight=1.0)[0].chunk.doc_id == "a/slides"


@pytest.mark.parametrize("word", ["slides", "slide", "deck"])
def test_explicit_slide_requests_keep_their_scores(word):
    """A learner asking for the deck must not pay the general-question penalty."""
    docs = [Document("course/slides", "Tools", "tools slides slide deck")]
    query = "tools " + word
    assert retrieve(query, docs) == retrieve(query, docs, slides_weight=1.0)


def test_slides_remain_available_when_they_are_the_only_answer():
    """Discounting slides must not hide material available only in a deck."""
    docs = [Document("course/slides", "Adapters", "HTTP vendor adapters")]
    assert retrieve("HTTP vendor adapters", docs)[0].chunk.doc_id == "course/slides"


def test_directory_named_slides_does_not_penalize_its_explanations():
    """A directory name must not classify every page beneath it as a slide deck."""
    docs = [Document("slides/introduction", "Adapters", "HTTP adapters")]
    assert retrieve("HTTP adapters", docs) == retrieve("HTTP adapters", docs, slides_weight=1.0)


def test_baseline_keeps_slide_scores_unchanged():
    """Turning off improvements must also disable the new slides discount."""
    docs = [Document("course/slides", "Adapters", "HTTP adapters")]
    assert retrieve("HTTP adapters", docs, **BASELINE) == retrieve(
        "HTTP adapters", docs, **dict(BASELINE, slides_weight=1.0)
    )
    assert BASELINE["slides_weight"] == 1.0
