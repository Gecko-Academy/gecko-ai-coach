"""The command line: ask a question, or measure the thing that answers it.

    ai-coach ask "how do I hand in a session" --pages ./units/en
    ai-coach ask "explain structured outputs" --provider ollama
    ai-coach measure --pages ./units/en --cases data/coach.jsonl
    ai-coach providers

Two commands, because there are two things you do with a coach: use it, and
find out whether your change to it helped.
"""

from __future__ import annotations

import argparse
import sys
from functools import partial
from pathlib import Path

from gecko_ai_coach import corpus
from gecko_ai_coach.coach import answer
from gecko_ai_coach.measure import CaseError, load_cases, run
from gecko_ai_coach.models import PROVIDERS, ModelError, get_client
from gecko_ai_coach.retrieve import BASELINE, retrieve


def _pages(argument: str | None) -> Path:
    return Path(argument) if argument else Path.cwd()


def _ask(
    question: str, pages: Path, provider: str, model: str, top_k: int, retriever_name: str = ""
) -> int:
    documents = corpus.load(pages)
    if not documents:
        print(f"no pages under {pages}", file=sys.stderr)
        return 2
    try:
        client = get_client(provider, model)
    except ModelError as error:
        print(str(error), file=sys.stderr)
        return 2

    chosen = _retriever(retriever_name, documents)
    result = (
        answer(question, documents, client=client, top_k=top_k)
        if chosen is None
        else answer(question, documents, client=client, retriever=chosen, top_k=top_k)
    )

    if result.refused:
        print(f"\n  {result.reason}.\n")
        # Not an error: refusing is a correct answer, and a non-zero exit here
        # would make every honest refusal look like a broken tool in a script.
        return 0

    if result.prose:
        print(f"\n{result.prose}\n")
        if result.fabricated:
            # Surfaced, never swallowed. A citation the model invented is the
            # single most useful thing this tool can show you about a model.
            named = ", ".join(result.fabricated)
            print(f"  removed {len(result.fabricated)} invented citation(s): {named}\n")

    for scored in result.passages:
        chunk = scored.chunk
        where = chunk.url or chunk.doc_id
        print(f"  {chunk.title}  ({scored.score:.2f})\n  {where}")
        if not result.prose:
            body = chunk.text.strip()
            print("\n" + "\n".join(f"    {line}" for line in body.splitlines()[:12]))
        print()
    if result.reason and result.prose == "":
        print(f"  note: {result.reason}\n")
    return 0


def _retriever(name: str, documents):  # type: ignore[no-untyped-def]
    """The keyword baseline, or an embedding index when one is asked for."""
    if name in ("", "keyword"):
        return None
    if name != "chroma":
        raise ValueError(f"unknown retriever {name!r}. Known: keyword, chroma")
    from gecko_ai_coach.vector import build

    return build(documents)


def _measure(
    pages: Path, cases_path: Path, top_k: int, retriever_name: str = "", baseline: bool = False
) -> int:
    documents = corpus.load(pages)
    try:
        cases = load_cases(cases_path)
    except CaseError as error:
        print(str(error), file=sys.stderr)
        return 2
    try:
        chosen = _retriever(retriever_name, documents)
        if baseline:
            if chosen is not None:
                raise ValueError("--baseline switches off the keyword improvements only")
            chosen = partial(retrieve, **BASELINE)
    except (ValueError, Exception) as error:  # noqa: B014 - VectorError is an Exception
        print(str(error), file=sys.stderr)
        return 2
    report = (
        run(cases, documents, top_k=top_k)
        if chosen is None
        else run(cases, documents, retriever=chosen, top_k=top_k)
    )
    label = (retriever_name or "keyword") + (" (baseline)" if baseline else "")
    print(f"\n  {len(documents)} pages from {pages}  ·  retriever: {label}\n")
    print(report.rendered())
    print()
    # Never fail on a low score: a number you are trying to improve must not be
    # a gate you are trying to pass.
    return 0


def _providers() -> int:
    print()
    for name, lane in sorted(PROVIDERS.items()):
        key = lane.key_env or "no key needed"
        model = lane.default_model or "pass --model"
        print(f"  {name:<12} {lane.base_url}")
        print(f"  {'':<12} {key} · {model}")
        if lane.note:
            print(f"  {'':<12} {lane.note}")
        print()
    print("  echo         no model at all: quote the pages and say nothing more\n")
    return 0


def _propose(question: str, page: str, pages: Path, write: bool) -> int:
    from gecko_ai_coach import corpus
    from gecko_ai_coach.propose import COMMUNITY, ProposalError, already_listed, propose, render

    try:
        proposal = propose(question, page, corpus.load(pages))
    except ProposalError as error:
        print(f"  {error}")
        return 2
    if already_listed(proposal.question, COMMUNITY):
        print(f'  "{proposal.question}" is already in data/. Thank you anyway -- try another one.')
        return 0
    print(render(proposal))
    if not write or proposal.already_answered:
        return 0
    COMMUNITY.mkdir(parents=True, exist_ok=True)
    written = COMMUNITY / proposal.filename
    written.write_text(proposal.line + "\n", encoding="utf-8")
    print(f"\n  Wrote {written}. Commit it and open the pull request -- see CONTRIBUTING.md.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ai-coach", description="Ask a course a question, and measure what answers it."
    )
    sub = parser.add_subparsers(dest="command")

    asker = sub.add_parser("ask", help="answer a question from the pages")
    asker.add_argument("question")
    asker.add_argument("--pages", help="the corpus directory (default: the working directory)")
    asker.add_argument("--provider", default="", help="ollama, moonshot, openai, groq, openrouter")
    asker.add_argument("--model", default="", help="the model id for that provider")
    asker.add_argument("--top-k", type=int, default=3)
    asker.add_argument("--retriever", default="", help="keyword (default) or chroma")

    measurer = sub.add_parser("measure", help="hit rate against a labelled set")
    measurer.add_argument("--pages")
    measurer.add_argument("--cases", required=True, help="a JSONL labelled set")
    measurer.add_argument("--top-k", type=int, default=3)
    measurer.add_argument(
        "--retriever", default="", help="keyword (default) or chroma, with the vector extra"
    )
    measurer.add_argument(
        "--baseline",
        action="store_true",
        help="switch every ranking improvement off: the number a change is compared with",
    )

    proposer = sub.add_parser(
        "propose", help="check a question the coach gets wrong, and add it (a first contribution)"
    )
    proposer.add_argument("question", help="the question, the way a learner would ask it")
    proposer.add_argument("--page", required=True, help="the page id that SHOULD answer it")
    proposer.add_argument("--pages", help="the corpus directory (default: the working directory)")
    proposer.add_argument(
        "--write", action="store_true", help="save it under data/community/ if it is a real miss"
    )

    sub.add_parser("providers", help="the model lanes this knows about")

    args = parser.parse_args(argv)
    if args.command == "ask":
        return _ask(
            args.question,
            _pages(args.pages),
            args.provider,
            args.model,
            args.top_k,
            args.retriever,
        )
    if args.command == "measure":
        return _measure(
            _pages(args.pages), Path(args.cases), args.top_k, args.retriever, args.baseline
        )
    if args.command == "propose":
        return _propose(args.question, args.page, _pages(args.pages), args.write)
    if args.command == "providers":
        return _providers()
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
