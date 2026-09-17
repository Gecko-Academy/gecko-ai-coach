"""Lexical retrieval: deterministic, cheap, and readable on sight.

This is deliberately not an embedding index. A keyword baseline is debuggable by
eye, needs no dependencies and no GPU, and sets the bar a fancier retriever must
beat on a labelled set before it earns its place.

IT IS ALSO DELIBERATELY MEDIOCRE. This file is the thing you are invited to
improve. Every knob is in it and nothing is hidden: the stopword list, the chunk
size, how a score is computed, how ties break. `ai-coach measure` prints the
number that says how mediocre, and a pull request that moves it -- and says by
how much, on which set -- is the contribution this project wants.

THE ORDER THAT ACTUALLY MOVES THE NUMBER, measured rather than assumed:
retrieval first, prompt shape second, model last. A 7B model holding the right
passage beats a frontier model holding the wrong one, so most of the headroom
is in this file rather than in whichever model you point at it.
"""

from __future__ import annotations

import math
import re
from collections.abc import Sequence
from dataclasses import dataclass

_TOKEN_RE = re.compile(r"[a-z0-9]+")

#: Words too common to signal relevance. Hand-written, English, and one of the
#: easiest things here to do better -- it knows nothing about the vocabulary of
#: the corpus it is pointed at.
STOPWORDS = frozenset(
    "a an and are as at be but by can could did do does for from has have how i if in "
    "into is it its me my no not of on one only or our over should so some than that "
    "the their then they this to under was we what when where which who why will with "
    "would you your".split()
)


@dataclass(frozen=True)
class Document:
    """A page of the corpus. `doc_id` is what a citation names."""

    doc_id: str
    title: str
    text: str
    url: str = ""


@dataclass(frozen=True)
class Chunk:
    doc_id: str
    title: str
    text: str
    position: int
    url: str = ""


@dataclass(frozen=True)
class ScoredChunk:
    chunk: Chunk
    score: float


def tokens(text: str) -> list[str]:
    return [t for t in _TOKEN_RE.findall(text.lower()) if t not in STOPWORDS]


def chunk_document(doc: Document, max_chars: int = 800) -> list[Chunk]:
    """Pack whole paragraphs into chunks of at most `max_chars` characters.

    Paragraphs are kept whole because a sentence cut in half retrieves badly and
    reads worse. A single oversized paragraph still becomes its own chunk,
    truncated -- losing the tail is better than losing the paragraph.
    """
    paragraphs = [p.strip() for p in doc.text.split("\n\n") if p.strip()]
    chunks: list[Chunk] = []
    current: list[str] = []
    length = 0
    for paragraph in paragraphs:
        if length and length + len(paragraph) + 2 > max_chars:
            chunks.append(Chunk(doc.doc_id, doc.title, "\n\n".join(current), len(chunks), doc.url))
            current, length = [], 0
        current.append(paragraph[:max_chars])
        length += len(paragraph) + 2
    if current:
        chunks.append(Chunk(doc.doc_id, doc.title, "\n\n".join(current), len(chunks), doc.url))
    return chunks


#: The original keyword retriever: every improvement switched off. Pass it to see
#: the number every change is measured against: `retrieve(q, docs, **BASELINE)`.
BASELINE: dict[str, bool | float] = {"bm25": False, "title_weight": 0.0, "one_per_page": False}


def retrieve(
    query: str,
    documents: Sequence[Document],
    top_k: int = 3,
    max_chars: int = 800,
    *,
    bm25: bool = True,
    title_weight: float = 1.0,
    one_per_page: bool = True,
) -> list[ScoredChunk]:
    """Score chunks against a question, and return the best `top_k`.

    Returns `[]` when no chunk shares a token with the query, which is what lets
    a caller refuse before spending a model call. An empty result is a correct
    answer, not a failure.

    THREE SWITCHES, each measurable on its own. Turn one off and run
    `ai-coach measure` to see what it was worth -- that is the fastest way to
    understand this file, and a good first contribution to report:

    `bm25`          counts how often a word appears in a chunk, and discounts
                    long chunks, so a page that mentions everything once stops
                    outranking the page that is actually about the question.
    `title_weight`  a word that also appears in the page TITLE counts extra.
                    A page called "Handing work in" is about handing work in.
    `one_per_page`  the top answers come from different pages, so one long page
                    cannot take every slot.

    With all three off this is exactly the original keyword baseline. Measured
    against the public cohort pages, turning all three on moved:

        data/dev3pack.jsonl          47% -> 59%
        data/course-questions.jsonl  68% -> 76%
        data/held-out.jsonl          79% -> 83%

    The sort key is load-bearing: `(-score, doc_id, position)` makes the same
    question return the same passages on every machine, so a measured
    improvement is a property of the change and not of the hardware.
    """
    query_tokens = set(tokens(query))
    if not query_tokens:
        return []
    all_chunks = [chunk for doc in documents for chunk in chunk_document(doc, max_chars)]
    if not all_chunks:
        return []

    bodies = [tokens(chunk.text) for chunk in all_chunks]
    titles = [set(tokens(chunk.title)) for chunk in all_chunks]

    frequency: dict[str, int] = {}
    for body in bodies:
        for token in set(body) & query_tokens:
            frequency[token] = frequency.get(token, 0) + 1

    total = len(all_chunks)
    average_length = sum(len(body) for body in bodies) / total
    scored: list[ScoredChunk] = []
    for chunk, body, title in zip(all_chunks, bodies, titles, strict=True):
        score = 0.0
        for token in query_tokens:
            weight = (
                math.log(1 + total / frequency[token])
                if token in frequency
                else math.log(1 + total)
            )
            count = body.count(token)
            if count:
                if bm25:
                    squash = 1.2 * (0.25 + 0.75 * len(body) / average_length)
                    score += weight * (count * 2.2) / (count + squash)
                else:
                    score += weight
            if title_weight and token in title:
                score += title_weight * weight
        if score > 0:
            scored.append(ScoredChunk(chunk=chunk, score=round(score, 6)))

    scored.sort(key=lambda s: (-s.score, s.chunk.doc_id, s.chunk.position))
    if one_per_page:
        seen: set[str] = set()
        distinct: list[ScoredChunk] = []
        for item in scored:
            if item.chunk.doc_id not in seen:
                seen.add(item.chunk.doc_id)
                distinct.append(item)
        scored = distinct
    return scored[:top_k]
