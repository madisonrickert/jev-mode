[← All ratings](README.md)

*Rated under an earlier rubric (2026-09-28). A re-rating is queued.*

> **jlowin/vibecheck** at [`1011988`](https://github.com/jlowin/vibecheck/tree/1011988a5c7b71b891d3a022fdbd5745c2a36edb) · library
> ### Verdict 2: Rework it
> Execution ●○○ · Fit ●●○ · Coverage ●●● · Evidence ●○○
>
> - vibecheck (jlowin, 35 stars, no license file) is a Python library that wraps TypeSafe's System One API in four verbs: `check` (one Noul, probability against a threshold or a (low, high) band), `classify` (one Choice), `label` (one independent Noul per option), and `score` (one Score, probability-weighted position).
> - It adds `assess` (a dataclass whose fields become questions in one request), `batch` (many questions about one state in one request), and `filter`/`group` (one request per item).
> - The design is close to Jev's own advice: typed answers are read directly, structured data goes through as JSON, `label` and `assess` pass their inputs as JSON fields, thresholds and uncertainty bands are first-class, and the docs say to keep counting and arithmetic in code and to pin a versioned model.
>
> **Top fix:** Change the README batch example and `examples/score/numeric_levels.py` to described levels (situations, no numbers in the level text), and make numeric `range` levels either warn or accept a dict of number to description only.

## What holds it back

- **The right primitive** (F2): The verbs map correctly (Noul/Choice/Score, `backends.py:_to_wire`), but `score` accepts bare numbers as levels and the README ships them in its own batch example: `urgency = b.score("How urgent is this?", range(1, 6))` and `stars = await score(..., range(1, 6), review)`, plus `examples/score/numeric_levels.py`. `_plans.py:_levels` turns numbers into `str(v)` descriptions. The README says described levels "give better answers than bare numbers" but still demonstrates the bare form.
- **Batching** (F4): `batch` and `assess` send many questions over one state in one request (`_batch.py:send`), which is right. But `filter` and `group` over a dataset send one request per item (`_run.py:arun_each`; docstring: "Each item is its own request"), and the README's own claim is that batching 100 questions cost about 1% of the tokens. No inverted request (criteria in the state, rows as questions) is offered.
- **Measured in the workflow** (F7): No accuracy, cost or latency measurement on any task in the repo. The tests use `FakeBackend` and a mocked HTTP transport (`tests/test_api.py`, `tests/test_typesafe_backend.py`); they check the plumbing, not answer quality.
- **Choice order handled** (F13): `classify` and `group` route work and `classify` over functions runs the picked handler (`examples/classify/functions.py`, `handler(ticket)`; README "refund" handler) with no order averaging or per-item shuffling (`_plans.py:_classify` passes options in dict order). Those actions run without review.
- **Sample size** (F15): The only claim with numbers, "In a test with a 5,000-token document, 100 questions asked together gave the same answers as 100 separate requests, for about 1% of the tokens" (README, Many Questions), gives one document and no method or script. Docs: https://docs.typesafe.ai/cookbooks/classification_using_confidence.md

## Fixes (from reading the code; not tested against it)

1. **F2 wrong primitive: bare numeric Score levels.** Change the README batch example and `examples/score/numeric_levels.py` to described levels (situations, no numbers in the level text), and make numeric `range` levels either warn or accept a dict of number to description only. Source: [`primitives/score`](https://docs.typesafe.ai/primitives/score), [`primitives`](https://docs.typesafe.ai/primitives).
2. **F4 one question per request over a dataset.** Give `filter` and `group` an inverted-request mode: put the criteria in the state and send each row as a question, or batch several items per request. Check it against per-item requests on a small sample first. Source: [`patterns/fan-out`](https://docs.typesafe.ai/patterns/fan-out), [`cookbooks/parallel_questions`](https://docs.typesafe.ai/cookbooks/parallel_questions).
3. **F20 values spliced into question strings.** In `examples/classify/no_data.py` pass the term as a JSON field (`{"question": "What is this most commonly known as?", "term": thing}` as the instructions object, or as the state) instead of the f-string. Source: [`primitives/advanced`](https://docs.typesafe.ai/primitives/advanced).

**Minor:** Model pinned (F12); Values from code are fields, not templates (F20); Untrusted text treated as data (F22); Non-English content handled (F23). These are listed fixes and don't lower the verdict.

[Full rating: every fact, its evidence and the files read →](full/jlowin__vibecheck.md)

