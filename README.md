# Gecko AI Coach

**English** · [Português (rascunho)](README.pt-BR.md) · [Español (borrador)](README.es.md)

![Python](https://img.shields.io/badge/python-3.11+-blue)
![uv](https://img.shields.io/badge/uv-managed-6e56cf)
![License](https://img.shields.io/badge/license-MIT-blue)
![Hit rate](https://img.shields.io/badge/hit_rate@3-65%25_keyword_·_71%25_chroma-005efa)

Ask a course a question, get the passage that answers it and a citation you can open. Then **measure the thing that found it, and beat it.**

Built for the [Dev3Pack AI-Engineering Bootcamp](https://github.com/Gecko-Academy/dev3pack-cohort-2026-09), and useful against any directory of markdown.

## Contents

- [Start here](#start-here)
- [Find your way](#find-your-way)
- [For coding assistants](#for-coding-assistants)
- [Use it inside your harness](#use-it-inside-your-harness)
- [It is meant to be improved](#it-is-meant-to-be-improved)
- [Where the headroom is](#where-the-headroom-is)
- [Retrievers](#retrievers)
- [Models](#models)
- [Library](#library)
- [What it will not do](#what-it-will-not-do)
- [Contributing](#contributing)

## Start here

```bash
git clone https://github.com/Gecko-Academy/gecko-ai-coach.git
cd gecko-ai-coach
uv sync --extra dev

uv run ai-coach ask "where do I submit my work" --pages ../dev3pack-cohort-2026-09/units/en
```

No key, no download, no network: the default retriever reads the pages and quotes them.

To use it from anywhere else, install it straight from git. **There is no published package, and none is needed:**

```bash
uv pip install "gecko-ai-coach @ git+https://github.com/Gecko-Academy/gecko-ai-coach"
```

## Find your way

**Want to contribute and not sure where to start?** Every link below opens the
thing itself, not a folder to search.

| I want to… | Go straight to |
|---|---|
| **make my first contribution** | [rung 1](CONTRIBUTING.md#rung-1--add-a-question-the-coach-gets-wrong) — a question the coach gets wrong: 10 minutes, no code |
| **pick something to work on** | [good first issues](https://github.com/Gecko-Academy/gecko-ai-coach/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) — each one is a real miss |
| **translate the README** | [Translate the README](CONTRIBUTING.md#translate-the-readme) — two drafts are waiting for a native speaker |
| **change the ranking** | [`src/gecko_ai_coach/retrieve.py`](src/gecko_ai_coach/retrieve.py), then [rung 3](CONTRIBUTING.md#rung-3--change-one-knob-and-measure-it) |
| **see how good it is today** | [the numbers](CONTRIBUTING.md#the-numbers-today), or run `measure` below |
| **use it while I study** | [inside your harness](#use-it-inside-your-harness), as an MCP server |
| **know what a pull request must contain** | [the pull request template](.github/PULL_REQUEST_TEMPLATE.md) |

## For coding assistants

Read [`AGENTS.md`](AGENTS.md) first. [`llms.txt`](llms.txt) is the short index,
and `CLAUDE.md` points at the same policy — do not fork it.

Then read in this order:

| File | Why |
|---|---|
| [CONTRIBUTING.md](CONTRIBUTING.md) | The four rungs, and the one rule: bring the number |
| [src/gecko_ai_coach/retrieve.py](src/gecko_ai_coach/retrieve.py) | The ranking, and every switch in it |
| [src/gecko_ai_coach/measure.py](src/gecko_ai_coach/measure.py) | What the number means, and what it cannot see |
| [data/](data/) | The labelled sets. `held-out.jsonl` is never tuned on |
| [tests/test_coach.py](tests/test_coach.py) | Each test's docstring names the real failure it pins |

**The three rules that matter most here**, in full in `AGENTS.md`:

1. **A change to ranking without before-and-after numbers is not a contribution.** Run `measure` twice and paste both.
2. **Report the regressions**, not only the gains.
3. **Never tune on `data/held-out.jsonl`.** Run it once, at the end.

## Use it inside your harness

The coach also runs as an **MCP server**, so your assistant can ask the course
questions while you work — in Claude Code, Codex, or anything that speaks MCP.

A capability is two halves, and both live in [`capabilities/course/`](capabilities/course):
a **Skill** that tells the agent when to reach for this and what the tools mean,
and an **MCP server** that is the tools themselves. Neither substitutes for the other.

```json
{
  "mcpServers": {
    "gecko-ai-coach-course": {
      "command": "uvx",
      "args": ["--from", "gecko-ai-coach @ git+https://github.com/Gecko-Academy/gecko-ai-coach.git@main",
               "gecko-ai-coach-course"],
      "env": { "COACH_PAGES": "/path/to/dev3pack-cohort-2026-09/units/en" }
    }
  }
}
```

| Tool | Does |
|---|---|
| `ask_course` | the passages that answer a question, each with the page id it came from |
| `list_pages` | every page the coach can quote — also tells you whether a week has opened |
| `measure_retrieval` | the hit rate against a labelled set, every miss named |

It reads and nothing else: it never writes a file, fetches a URL, or looks
outside the pages directory it was given. Retrieved page text is data, never
instructions.

**Adding your own capability** is a directory beside `course/` with the same two
halves. The server is one stdlib file with no SDK, so you can read all of it
before you copy it.

## It is meant to be improved

This is a teaching tool, and the teaching is the improving. The number that says how good it is ships with it:

```bash
uv run ai-coach measure --pages ../dev3pack-cohort-2026-09/units/en --cases data/dev3pack.jsonl
```

```
  74 pages from ../dev3pack-cohort-2026-09/units/en  ·  retriever: keyword

  hit rate @3: 65%  (17 questions)

  ok   where do I submit my work
  MISS how do I hand in a session
         wanted unit0/how-to-submit
         got    unit0/week1, unit0/week2, unit0/week3
```

**You can help without writing code.** Found a question the coach gets wrong? One command checks it and saves it as a test:

```bash
uv run ai-coach propose "can I use claude instead of a local model" --page unit0/runtime-lanes \
  --pages ../dev3pack-cohort-2026-09/units/en --write
```

[CONTRIBUTING.md](CONTRIBUTING.md) walks through it step by step, from that first ten-minute pull request to changing the ranking — with good first issues taken from real misses.

## Where the headroom is

Measured rather than assumed, and in this order:

1. **Retrieval.** Whether the right passage is in the prompt at all. A 7B model holding the right passage beats a frontier model holding the wrong one.
2. **How much you give it.** Three tight chunks beat ten loose ones. Small models degrade with long context faster than large ones do.
3. **The output shape.** A narrow schema is followed far more reliably than an open instruction, at every model size.
4. **Making refusal legitimate.** Models hallucinate hardest when refusing feels forbidden. `NOT IN THESE PAGES` is a correct answer here.
5. **Verification after generation.** Every citation is checked against what was actually retrieved; invented ones are stripped and reported.
6. **The model.** Last, and usually by less than people expect.

Most people arrive believing 6 is the whole job. `measure` is there to disagree in numbers.

## Retrievers

| Name | Needs | Hit rate @3 | Notes |
|---|---|---|---|
| `keyword` | nothing | **65%** | the default: no dependency, no download, instant. `--baseline` measures it with every improvement off: 47% |
| `chroma` | `chromadb` and a model download | **71%** | embeddings, with a similarity floor |

```bash
uv pip install chromadb
uv run ai-coach measure --pages <pages> --cases data/dev3pack.jsonl --retriever chroma
```

**The floor is the interesting part**, and both retrievers now have one. A vector index returns its nearest neighbours however far away they are, so with no floor `chroma` scores 59% and answers a question about Kubernetes with course material. The keyword retriever had the same hole until `min_coverage` closed it — it asks how much of the question appears on the winning page, and returns nothing when too little does. Measured on this set:

| `min_score` | Hit rate | Answerable | Refusals |
|---|---|---|---|
| 0.00 | 59% | 10/15 | **0/2** |
| 0.20 | 65% | 10/15 | 1/2 |
| **0.25** | **71%** | **10/15** | **2/2** |
| 0.30 | 65% | 9/15 | 2/2 |
| 0.40 | 47% | 6/15 | 2/2 |

`0.25` is the default and it was **chosen on this set**, which is the thing this project warns against — so it is written down rather than hidden. It is a default, not a finding. Measure it on your own set before trusting it.

## Models

Any OpenAI-shaped endpoint, over stdlib `urllib` — no SDK, no wheel to build.

```bash
uv run ai-coach providers
```

| Lane | Key | Notes |
|---|---|---|
| `ollama` | none | local, free, offline. `ollama serve` |
| `moonshot` | `MOONSHOT_API_KEY` | `api.moonshot.cn/v1` from mainland China |
| `openai` | `OPENAI_API_KEY` | |
| `groq` | `GROQ_API_KEY` | |
| `openrouter` | `OPENROUTER_API_KEY` | many models behind one key |
| `echo` | none | no model at all: quote the pages, say nothing more |

Swap one, run `measure`, and see how much it moved. That comparison is the point of having a seam.

## Library

```python
from pathlib import Path
from gecko_ai_coach import corpus, coach

documents = corpus.load(Path("units/en"))
result = coach.answer("where do I submit my work", documents)
print(result.pages[0])  # unit0/how-to-submit
```

`coach.answer` takes `retriever=` and `client=`, so replacing either is one line rather than a fork.

## What it will not do

- **Index a `solutions/` directory or an inline `<Question />` block.** A course tool that can quote the answer key is a cheat sheet. Two tests pin this.
- **Cache an index to disk.** One that can go stale is wrong in a way nobody looks at.
- **Read a key from anywhere but the environment**, or put one in an error.

## Contributing

Start with [rung 1 of CONTRIBUTING.md](CONTRIBUTING.md#rung-1--add-a-question-the-coach-gets-wrong): ten minutes, no code. Or [review a translation](CONTRIBUTING.md#translate-the-readme) of this page. One rule for ranking changes: bring the number — before and after, on a named set, and the regression as well as the gain.

MIT.
