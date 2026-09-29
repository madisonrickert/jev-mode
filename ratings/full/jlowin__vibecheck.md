[← Summary](../jlowin__vibecheck.md)

# vibecheck: full rating

**Verdict 2, Rework it** · library · rated 2026-09-28 at [`1011988`](https://github.com/jlowin/vibecheck/tree/1011988a5c7b71b891d3a022fdbd5745c2a36edb) · read: full · rubric 2026-09-28 (earlier) · claude-sonnet-5-5, medium effort

*Rated under an earlier rubric (2026-09-28). A re-rating is queued.*

## Summary

vibecheck (jlowin, 35 stars, no license file) is a Python library that wraps TypeSafe's System One API in four verbs: `check` (one Noul, probability against a threshold or a (low, high) band), `classify` (one Choice), `label` (one independent Noul per option), and `score` (one Score, probability-weighted position). It adds `assess` (a dataclass whose fields become questions in one request), `batch` (many questions about one state in one request), and `filter`/`group` (one request per item). The design is close to Jev's own advice: typed answers are read directly, structured data goes through as JSON, `label` and `assess` pass their inputs as JSON fields, thresholds and uncertainty bands are first-class, and the docs say to keep counting and arithmetic in code and to pin a versioned model. Two things hold it at 2 under the current anchors: the README's own batch example and a shipped example score with bare numeric levels (`range(1, 6)`), and `filter`/`group` send one request per item instead of the inverted request. It also has no measurement of its own, no guard for prompt-injection or size limits, and no handling of option order for classify calls that route work. As a library its quality depends on how callers use it, so this rates the design and the shipped guidance, not any one app built on it.

## What fails

| Fact | Finding |
|---|---|
| The right primitive (F2) | **no.** The verbs map correctly (Noul/Choice/Score, `backends.py:_to_wire`), but `score` accepts bare numbers as levels and the README ships them in its own batch example: `urgency = b.score("How urgent is this?", range(1, 6))` and `stars = await score(..., range(1, 6), review)`, plus `examples/score/numeric_levels.py`. `_plans.py:_levels` turns numbers into `str(v)` descriptions. The README says described levels "give better answers than bare numbers" but still demonstrates the bare form. |
| Batching (F4) | **no.** `batch` and `assess` send many questions over one state in one request (`_batch.py:send`), which is right. But `filter` and `group` over a dataset send one request per item (`_run.py:arun_each`; docstring: "Each item is its own request"), and the README's own claim is that batching 100 questions cost about 1% of the tokens. No inverted request (criteria in the state, rows as questions) is offered. |
| Measured in the workflow (F7) | **no.** No accuracy, cost or latency measurement on any task in the repo. The tests use `FakeBackend` and a mocked HTTP transport (`tests/test_api.py`, `tests/test_typesafe_backend.py`); they check the plumbing, not answer quality. |
| Model pinned (F12) | **no.** Default is `jev-latest` (README, Configuration); the README tells users to pin `jev-1.13.0` after tuning, and `model=` is accepted on every verb, but nothing pins by default and nothing logs the response's `model` field. |
| Choice order handled (F13) | **no.** `classify` and `group` route work and `classify` over functions runs the picked handler (`examples/classify/functions.py`, `handler(ticket)`; README "refund" handler) with no order averaging or per-item shuffling (`_plans.py:_classify` passes options in dict order). Those actions run without review. |
| Values from code are fields, not templates (F20) | **no.** The library itself is clean: `label` and `assess` build instructions as JSON objects (`_plans.py:_merge`, `assess` builds `{"task": task, "question": field_question}`). But `examples/classify/no_data.py` splices a looped data value into the question: `classify(f"What is {thing} most commonly known as?", options)`. That is the templating pattern the rubric fails, in a shipped example users copy. |
| Untrusted text treated as data (F22) | **no.** Shipped examples pass tickets, reviews and articles (user-supplied text) straight into the state with no flag and no steering test, and neither the README nor the SKILL mentions steering text. |
| Non-English content handled (F23) | **no.** Not tested and not stated as English-only; no translation option. |
| Sample size (F15) | **no.** The only claim with numbers, "In a test with a 5,000-token document, 100 questions asked together gave the same answers as 100 separate requests, for about 1% of the tokens" (README, Many Questions), gives one document and no method or script. Docs: https://docs.typesafe.ai/cookbooks/classification_using_confidence.md |

<details>
<summary><b>What passes (10) and doesn't apply (4)</b></summary>

| Fact | Finding |
|---|---|
| Atomic questions (F1) | yes. Each verb asks one property: `check` one Noul, `label` splits into one Noul per option (`_plans.py:_label`, questions `o{i}`), `assess` one question per field (`_plans.py:assess`). Shipped questions are single-property ("Is the customer asking for a human?", `examples/check/basic.py`). |
| Structured state (F3) | yes. Dicts, lists, dataclasses and Pydantic models are sent as named-field JSON (`_run.py:to_state`); a plain string is the single-text default. README: "Structure helps more than volume." The library does not add item IDs or path-pointing, which is left to callers. |
| Thresholds in code (F5) | yes. `threshold=` and `(low, high)` are code arguments with a documented default; nothing is left to the LLM (`_plans.py:_check`, `_band`). No threshold on `classify` or `score`; those are read by the caller from probabilities. |
| No invented values (F6) | yes. `score` position is computed in code from the returned level probabilities (`_plans.py:_score`); README: "Arithmetic, counting, and date comparisons belong in code." |
| Options exclusive and exhaustive (F8) | yes. Options are the caller's; the library validates count and distinct labels (`_plans.py:_options`), supports per-option descriptions, and `examples/classify/descriptions.py` exists to settle the returns/billing overlap that `examples/classify/basic.py` leaves open. Judged on the guidance, not a caller's lists. |
| An "unclear" or "other" option (F9) | yes. README, Classify: "give it a way out when your list might not cover every case. An `"other"` option works well"; `examples/classify/other.py` and the SKILL both say the same. Some README examples (the `Triage` dataclass's `team`) omit it. |
| Evidence recorded evenly (F10) | n.a.. The state is the single item being judged; the library adds no per-answer evidence. |
| Confidence drives action (F11) | yes. `check` bands return `None` for the uncertain middle and the README says to `match` on it (`examples/check/three_way.py`); `probabilities=True` on every verb, with a runner-up margin gate in `examples/classify/probabilities.py` (`best - runner_up < 0.3`). |
| Size limits respected (F14) | n.a.. No guard that trims or stops above 64k or 32k tokens (`_run.py:to_state` passes everything); the README only warns that accuracy drops with irrelevant detail. Unverified counts as n.a. |
| Typed answers read directly (F19) | yes. Every decision is read from `noul`, `choice` probabilities or `score` probabilities (`backends.py:_from_wire`); no free text is parsed. |
| No instructions in the state (F21) | yes. State is the caller's content; function-option docstrings go in option descriptions, not state (`_plans.py:_describe_callable`). |
| Independent labels (F16) | n.a.. The claim compares batched with separate runs, not against labels. |
| Held-out set (F17) | n.a.. No thresholds tuned to a reported number. |
| Fair baseline (F18) | yes. The comparison is the same document asked as 100 separate requests, which is the natural alternative; the trace is not in the repo. |

</details>

## Scores

- **Execution 1.** Anchor "two or more of F1-F6 are no": F2 (bare-number Score levels shipped in the README batch example and an example) and F4 (`filter`/`group` do one request per item). F1 and F19 hold, so it is not a 0. F20 to F22 don't lower this score; they cap the verdict.
- **Fit 2.** Anchor "exactly one mismatch": F13 fails (routing `classify` without order handling), while primitives match their decisions, confidence is used through bands and probabilities, and parallel questions are used through `batch`, `assess` and `label`. The `filter`/`group` request shape is scored under F4, not double counted here.
- **Coverage 3.** Anchor "80% or more of the stated goal": the goal is "decision models right in your Python code" with typed verbs; all four verbs, structured data, probabilities, batching, schemas and a test backend are implemented and tested. Omissions (model logging, size guard, inverted request) are not goals it states. Lineage is new; the closest TypeSafe references are [`patterns/fan-out`](https://docs.typesafe.ai/patterns/fan-out), [`patterns/confidence-routing`](https://docs.typesafe.ai/patterns/confidence-routing) and [`cookbooks/parallel_questions`](https://docs.typesafe.ai/cookbooks/parallel_questions), and it keeps their core ideas (one request per state, confidence as a gate).
- **Evidence 1.** Anchor "numbers given without method": the 1% token claim and "trained to be calibrated" appear with no method or script in the repo. It claims one result, so it isn't n.a., and it isn't 0 because the claim is narrow and disclosed with its setup.

Stages: `data-prep` (to_state serialization), `question-state` (options, descriptions, JSON instructions), `execution` (batching, backends), `decision` (thresholds, bands). It does not close the loop: nothing evaluates on labels or calibrates.

## Why this verdict

**2, Rework it.** The verdict comes from the anchor "Execution 1 or 0". Execution is 1 because F2 and F4 both fail. F2 is the more borderline reading: the library never forces bare numbers and the README calls described levels better, but it demonstrates `range(1, 6)` in its headline batch example. If F2 were read as yes, Execution would be 2, and the verdict would sit at 3 because F20 (an f-string question in `examples/classify/no_data.py`), F22 (no steering test or flag) each cap it there. Either way it isn't a 4: the library's core is sound, so most of this is a documentation-and-example fix plus one feature (the inverted request for `filter` and `group`), not a redesign.

## Fixes (from reading the code; not tested against it)

1. **F2 wrong primitive: bare numeric Score levels.** Change the README batch example and `examples/score/numeric_levels.py` to described levels (situations, no numbers in the level text), and make numeric `range` levels either warn or accept a dict of number to description only. Source: [`primitives/score`](https://docs.typesafe.ai/primitives/score), [`primitives`](https://docs.typesafe.ai/primitives).
2. **F4 one question per request over a dataset.** Give `filter` and `group` an inverted-request mode: put the criteria in the state and send each row as a question, or batch several items per request. Check it against per-item requests on a small sample first. Source: [`patterns/fan-out`](https://docs.typesafe.ai/patterns/fan-out), [`cookbooks/parallel_questions`](https://docs.typesafe.ai/cookbooks/parallel_questions).
3. **F20 values spliced into question strings.** In `examples/classify/no_data.py` pass the term as a JSON field (`{"question": "What is this most commonly known as?", "term": thing}` as the instructions object, or as the state) instead of the f-string. Source: [`primitives/advanced`](https://docs.typesafe.ai/primitives/advanced).
4. **F22 untrusted text not treated as data.** Add a README section on user-supplied text: an injection-check `check` (or a flag) before the routing call, and a test with steering input, since the examples all route on customer text. Source: [`model-jaggedness/jev-1.13`](https://docs.typesafe.ai/model-jaggedness/jev-1.13), [`cookbooks/classifying_rag_passages`](https://docs.typesafe.ai/cookbooks/classifying_rag_passages).
5. **F13 Choice order unhandled.** For `classify` and `group` that route or dispatch, offer averaging over option orders or a per-call shuffle, and document it next to the function-handler example. Source: [`cookbooks/consistency_choice_cookbook`](https://docs.typesafe.ai/cookbooks/consistency_choice_cookbook).
6. **F12 model not pinned.** Log the `model` field each response returns (it is already in the wire response, `tests/test_typesafe_backend.py`) and warn when the alias is used with a threshold. Source: [`models`](https://docs.typesafe.ai/models).
7. **F7 nothing measured.** Publish the 100-question test as a script with the document, or drop the number; add a small labeled eval showing a threshold on one shipped example. **(confirm with data)** Source: [`cookbooks/classification_using_confidence`](https://docs.typesafe.ai/cookbooks/classification_using_confidence).
8. **F14 and F23** (fix-only): add a size guard for state plus questions above 32k/64k tokens, and note or test non-English input. Source: [`models`](https://docs.typesafe.ai/models), [`concepts/state`](https://docs.typesafe.ai/concepts/state).

<details>
<summary><b>Files read (34)</b></summary>

Manifest commit 1011988a5c; all 34 manifest files are listed. depth is `full`: none skipped.
- .agents/skills/vibecheck/SKILL.md: read
- AGENTS.md: read
- README.md: read
- examples/check/basic.py: read
- examples/check/no_data.py: read
- examples/check/probabilities.py: read
- examples/check/three_way.py: read
- examples/check/threshold.py: read
- examples/classify/basic.py: read
- examples/classify/descriptions.py: read
- examples/classify/enums.py: read
- examples/classify/functions.py: read
- examples/classify/no_data.py: read
- examples/classify/other.py: read
- examples/classify/probabilities.py: read
- examples/label/basic.py: read
- examples/label/probabilities.py: read
- examples/label/top_n.py: read
- examples/score/basic.py: read
- examples/score/described_levels.py: read
- examples/score/numeric_levels.py: read
- examples/score/probabilities.py: read
- pyproject.toml: read
- src/vibecheck/__init__.py: read
- src/vibecheck/_async.py: read
- src/vibecheck/_batch.py: read
- src/vibecheck/_plans.py: read
- src/vibecheck/_questions.py: read
- src/vibecheck/_run.py: read
- src/vibecheck/backends.py: read
- src/vibecheck/sync.py: read
- src/vibecheck/testing.py: read
- tests/test_api.py: read
- tests/test_typesafe_backend.py: read

</details>
