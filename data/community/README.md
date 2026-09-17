# Community questions

Questions learners found the coach getting wrong. One file per question, so two
pull requests never conflict.

Add one with:

```bash
ai-coach propose "your question" --page the/page-id \
  --pages ../dev3pack-cohort-2026-09/units/en --write
```

`ai-coach measure --cases data/community` reports them. They never decide
whether a pull request passes, so adding one cannot break anybody's build.
