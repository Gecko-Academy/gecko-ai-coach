<!--
Thank you for contributing. Fill this in rather than deleting it: the checklist
is how a reviewer reads your pull request, and how you know it is complete.
Working with a coding assistant? Point it at AGENTS.md first.
-->

## What this changes

<!-- One or two sentences. What is different after this pull request? -->

## Which rung is it?

<!-- Tick one. CONTRIBUTING.md explains them. -->

- [ ] **1. A question the coach gets wrong** (`ai-coach propose`, one file under `data/community/`)
- [ ] **2. An explanation of a miss**, or a corrected label
- [ ] **3. A translation**, or a review of one
- [ ] **4. A ranking change** (fill in the numbers below)
- [ ] Something else:

## Rung 1 only — the question

```
question:
page it should answer with:
what the coach returned instead:
```

## Rung 4 only — the numbers

**Nothing else in this section is optional.** A ranking change without before and
after numbers cannot be reviewed.

| Set | Before | After |
|---|---|---|
| `data/dev3pack.jsonl` | | |
| `data/course-questions.jsonl` | | |
| `data/held-out.jsonl` (run once, at the end) | | |
| `data/community/` | | |

**Questions that got worse** — every one that went from `ok` to `MISS`:

```
(paste them, or write "none")
```

<details><summary>The measure output, before and after</summary>

```
(paste both)
```

</details>

## Checklist

- [ ] `uv run pytest` passes
- [ ] `uv run ruff format .` and `uv run ruff check .` are clean
- [ ] A behaviour change comes with a test whose docstring names the failure it pins
- [ ] No new runtime dependency in the default path
- [ ] I did not change my code after seeing the held-out number
- [ ] I can explain every line in this pull request
