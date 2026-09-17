# Contributing

You do not need to know how retrieval works to make this coach better. You need
ten minutes and one question it gets wrong.

This guide has four rungs. Start on rung 1. Each rung ends in a pull request or
an issue, and each one makes the coach measurably better for the whole cohort.

- [Set up once](#set-up-once)
- [Rung 1 — add a question the coach gets wrong](#rung-1--add-a-question-the-coach-gets-wrong) · 10 min · no code
- [Rung 2 — explain a miss](#rung-2--explain-a-miss) · 30 min · no code
- [Rung 3 — change one knob, and measure it](#rung-3--change-one-knob-and-measure-it) · 1–2 h · a few lines of Python
- [Rung 4 — bigger work](#rung-4--bigger-work) · open an issue first
- [Open the pull request](#open-the-pull-request)
- [The numbers today](#the-numbers-today)
- [Good first issues](#good-first-issues)
- [The rules](#the-rules)

## Set up once

You need `git`, [`uv`](https://docs.astral.sh/uv/) and a GitHub account.

1. **Fork** this repository: the **Fork** button, top right on GitHub.
2. Clone **your fork** and the course pages, side by side in one folder:

```bash
git clone https://github.com/<your-github-name>/gecko-ai-coach.git
git clone https://github.com/Gecko-Academy/dev3pack-cohort-2026-09.git
cd gecko-ai-coach
uv sync --extra dev
```

3. Check that it works. Both commands must finish without an error:

```bash
uv run ai-coach ask "how do I hand a session in" --pages ../dev3pack-cohort-2026-09/units/en
uv run pytest
```

Every command below runs from inside `gecko-ai-coach/`.

**Before each new contribution**, bring your fork up to date. On GitHub, open
your fork and click **Sync fork**. Then:

```bash
git checkout main
git pull
git -C ../dev3pack-cohort-2026-09 pull
```

## Rung 1 — add a question the coach gets wrong

**The most useful contribution there is.** A question the coach gets wrong,
written down with the page that should answer it, becomes a test that every
future change has to face. Nobody can fix a mistake that nobody wrote down.

1. Ask the coach something you really wanted to know this week, in your own words:

```bash
uv run ai-coach ask "can I use claude instead of a local model" --pages ../dev3pack-cohort-2026-09/units/en
```

2. If it quoted the wrong page, find the page that answers it. The page id is its
   path under `units/en/` without `.mdx`: `units/en/unit0/runtime-lanes.mdx` is
   `unit0/runtime-lanes`.

3. Check it, and save it:

```bash
uv run ai-coach propose "can I use claude instead of a local model" --page unit0/runtime-lanes \
  --pages ../dev3pack-cohort-2026-09/units/en --write
```

`propose` answers one of four ways. Only the first one writes a file:

| It says | Meaning |
|---|---|
| `A REAL MISS` … `Wrote data/community/<name>.jsonl` | Done. [Open the pull request](#open-the-pull-request). |
| `ALREADY ANSWERED` | The coach finds that page. Try another question. |
| `… is already in data/` | Someone added it first. Try another question. |
| `no page called …  Did you mean: …` | A typo in the page id. Use a suggestion. |

**Good questions** are the way a learner really types: short, informal, and
sometimes with the wrong word. `my notebook check is red` is a better question
than `What is the procedure for validating a notebook submission?`.

**Not useful:** copies of questions already in `data/` (`propose` refuses them),
and questions with no page that answers them — open an issue for those instead.

Pull request title: `question: can I use claude instead of a local model`

## Rung 2 — explain a miss

Pick a `MISS` from a measure run and find out **why** the coach got it wrong.
Write down what you found. You do not have to fix it.

```bash
uv run ai-coach measure --pages ../dev3pack-cohort-2026-09/units/en --cases data/course-questions.jsonl
```

```
  MISS what is in week 1
         wanted unit0/week1
         got    unit0/w05-packages-and-pep8/slides, unit0/w09-mcp-first-server/slides, unit0/week0
```

Open the page it wanted and the pages it got. Ask:

- **Are the words different?** The question says `hand in`. The page says `submit`.
- **Did a big page win?** A slides page says `week` twenty times and wins on volume.
- **Is the label wrong?** Sometimes the page the coach found answers the question
  better than the page in the file. That is a real finding.

Open an **issue** titled `miss: what is in week 1`. Name the three pages, and
write one sentence on the cause. If the label was wrong, fix it in
`data/dev3pack.jsonl` or `data/course-questions.jsonl` and open a pull request
titled `label: what is in week 1` instead.

A clear explanation is often most of the fix. The next person on rung 3 starts
from it.

## Rung 3 — change one knob, and measure it

The ranking lives in one function: `retrieve()` in
[`src/gecko_ai_coach/retrieve.py`](src/gecko_ai_coach/retrieve.py). Read its
docstring first. Then change **one** thing.

1. Make a branch:

```bash
git checkout -b rank/week-questions
```

2. Measure **before** you change anything, and save the output:

```bash
uv run ai-coach measure --pages ../dev3pack-cohort-2026-09/units/en --cases data/dev3pack.jsonl > before-dev.txt
uv run ai-coach measure --pages ../dev3pack-cohort-2026-09/units/en --cases data/course-questions.jsonl > before-course.txt
```

3. Make your change. Add a test to `tests/test_coach.py` that fails without it.

4. Measure again on the same two sets, and compare:

```bash
uv run ai-coach measure --pages ../dev3pack-cohort-2026-09/units/en --cases data/dev3pack.jsonl > after-dev.txt
uv run ai-coach measure --pages ../dev3pack-cohort-2026-09/units/en --cases data/course-questions.jsonl > after-course.txt
diff before-dev.txt after-dev.txt
diff before-course.txt after-course.txt
```

5. **Only when your change is finished**, run the held-out set and the community
   set, once:

```bash
uv run ai-coach measure --pages ../dev3pack-cohort-2026-09/units/en --cases data/held-out.jsonl
uv run ai-coach measure --pages ../dev3pack-cohort-2026-09/units/en --cases data/community
```

Do not change your code after you see the held-out number. If you do, the set is
no longer held out, and its number stops meaning anything. Report it as it is,
also when it went down. Expect it to move less than the other two.

6. Do not commit the `before-*.txt` and `after-*.txt` files. Paste them into the
   pull request description.

`measure --baseline` switches every ranking improvement off: it is the original
keyword retriever. Use it to see what an existing knob is worth.

Pull request title: `rank: <what you changed>`

## Rung 4 — bigger work

Open an issue first, so two people do not build the same thing:

- **Questions in Portuguese.** Many learners ask in Portuguese. Write
  `data/questions-pt.jsonl` and measure it. The first number will be low. That
  is the finding.
- **A second metric.** Hit rate says whether the right page is in the top 3. It
  does not say whether it came first. Mean reciprocal rank does.
- **A better embedding retriever behind the same seam.** Chroma is already there
  (`uv sync --extra vector`, then `--retriever chroma`). It must stay optional:
  the default runs with no download and no network, and that is a feature.

## Open the pull request

```bash
git checkout -b question/claude-instead-of-local   # skip this if you made a branch already
git add data/community/can-i-use-claude-instead-of-a-local-model.jsonl   # your files, by name
git commit -m "question: can I use claude instead of a local model"
git push -u origin question/claude-instead-of-local
```

`git push` prints a link. Open it and click **Create pull request**. The pull
request goes from your fork into `Gecko-Academy/gecko-ai-coach`, branch `main`.

In the description, write:

- **Rung 1:** the question, the page, and what the coach returned.
- **Rung 3:** before and after for every set you ran, and **every question that
  went from `ok` to `MISS`** — not only the ones that went the other way.

The checks run on your pull request. The first time, a maintainer may have to
approve them. If a check is red, open it and read the last lines. Fix it, then
commit and push again to the same branch. The pull request updates by itself.

## The numbers today

Measured on the public cohort pages (74 pages), 17 September 2026, `top_k=3`:

| Set | Questions | `--baseline` | Keyword, as shipped | Chroma |
|---|---|---|---|---|
| `data/dev3pack.jsonl` | 17 | 47% | **59%** | 71% |
| `data/course-questions.jsonl` | 25 | 68% | **76%** | not measured |
| `data/held-out.jsonl` | 24 | 79% | **83%** | not measured |

The held-out set was written before the ranking change, and nobody tuned on it.
That is why it moved least, and why it is the most honest number in the table.

**Tune on** `dev3pack` and `course-questions`. **Report, but never tune on,**
`held-out` and `community`.

## Good first issues

Each one is a real `MISS` from the table above.

**Rung 2 — explain it, or fix a label**

1. `what is prompt injection` wants session 4 `introduction` or `concepts-1`,
   and gets `concepts-2` and `concepts-3`. Which page actually defines it? The
   label may be too narrow.
2. `how do I stop a tool doing something dangerous` wants session 4
   `introduction`, and gets session 4 `concepts-1` in second place. Does
   `concepts-1` answer it? If it does, add it to `expected`.
3. `do I need an API key to do the exercises` gets `unit0/local-model` first. Is
   that wrong?

**Rung 3 — one knob**

4. **Slides pages drown week questions.** `what is in week 1`, `what is week 0
   for` and `when does week 3 start` all return `w*/slides` pages. Try a lower
   weight for slides pages. Report what it costs questions that do want one.
5. **Quiz pages are noise.** `what is the fake provider` returns
   `session-02-model-adapter/quiz`. The answers are already stripped from quiz
   pages, so what is left is questions without answers.
6. **A minimum score, so nothing is returned for nothing.** `how do I deploy a
   Kubernetes ingress controller` returns two pages. Refusing is the correct
   answer. Find a floor that refuses it and keeps the real questions.
7. **Word forms.** `can I run a model locally for free` misses
   `unit0/local-model`, because `locally` never matches `local`. A light stemmer
   is the usual fix. Measure it: stemming also joins words that should stay apart.
8. **The course's own synonyms.** `how do I hand in a session` never matches
   `submit`. A small synonym table can close several misses. In the course's
   session 7, this kind of change took a probe set from 75% to 0%, so the
   regression is the interesting half.
9. **Chunk size.** `max_chars=800` because it had to be something. Nobody has
   measured 400 or 1200.

## The rules

**Bring the number.** A pull request that changes ranking reports the hit rate
before and after, on named sets, and names the regressions as well as the gains.
Without that, nobody can tell an improvement from a change.

- **Tests for behaviour changes.** Each test's docstring names the real failure
  it pins.
- **`uv run ruff format .` and `uv run ruff check .` before you push.**
- **No new runtime dependencies.** A tool people are asked to fork must install
  anywhere, in one step.
- **Never index a `solutions/` directory, an answer key, or a quiz answer.** Two
  tests pin this, and they are not negotiable. A course tool that can quote the
  answers is a cheat sheet.
- **Be kind in review.** For most people here, this is their first pull request.

## Licence

MIT. By contributing, you agree to license your contribution under it.
