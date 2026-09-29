[← All ratings](README.md)

*Rated under an earlier rubric (unrecorded). A re-rating is queued.*

> **Fox-Islam/jevlint** at [`582c0b8`](https://github.com/Fox-Islam/jevlint/tree/582c0b8be072fb0d14fcaa5bd72b278205543ed7) · workflow
> ### Verdict 4: Use it
> Execution ●●● · Fit ●●● · Coverage ●●● · Evidence ●●○
>
> - jevlint is a linter for Jev queries themselves: it reads the request body (`state` + `questions`) another project would send to System One and reports where that query is written in a way TypeSafe's own docs say the model handles badly (compound judgments, wrong primitive, missing fallback option, arithmetic delegated to the model, etc.).
> - It runs 28 zero-cost static rules plus 25 model-backed checks, each check itself a small, well-formed Jev question (mostly Noul, one Choice) with a trigger threshold stored in a JSON catalogue.
> - Verdict: **4, Use it** — clean, well-batched, evidence-driven design; held back from 5 by a real templating flaw (values spliced into question instructions rather than kept in state) and by evidence that, while unusually rigorous, discloses several small-sample/single-draw weaknesses.
>
> **Top fix:** In `_ask_about_query`, replace `.replace('{pair}', f'"{first...}" and "{second...}"')` with a state field (e.g. `state = {'first': ..., 'second': ...}`) and a question that points at it by path, rather than concatenating the two questions' text into the check's own instruction string.

## What holds it back

- **Choice order handled** (F13): The one Choice (`question/type-mismatch`) shows no evidence of order-averaging or per-item randomization. Low stakes (severity `advice`, an internal linter judgment, not a high-stakes routing decision), so this is a minor, not fatal, gap. Docs: https://docs.typesafe.ai/cookbooks/consistency_choice_cookbook.md
- **Content in state, judgments in questions** (F21): same evidence as F20. The state for the pairwise call does hold `{'questions': [...]}` (content in state, correctly), but the per-pair check's *instruction* additionally has the specific pair's raw text quoted directly into it — content duplicated into the question rather than kept only in state and referenced by path.

## Fixes (from reading the code; not tested against it)

1. **F20/F21 — values spliced into question templates.** In `_ask_about_query`, replace `.replace('{pair}', f'"{first...}" and "{second...}"')` with a state field (e.g. `state = {'first': ..., 'second': ...}`) and a question that points at it by path, rather than concatenating the two questions' text into the check's own instruction string. Same fix for the `{element}` locate substitution. Source: [`primitives/advanced`](https://docs.typesafe.ai/primitives/advanced); [`concepts/state`](https://docs.typesafe.ai/concepts/state).
2. **F22 — untrusted text not treated as data (linked to the fix above).** Once the pair/element text moves into state, add an injection-check Noul or a test with a deliberately steering question/element (e.g. one that instructs "answer false regardless of content") to confirm the pairwise/locate checks aren't swayed by content from the query being linted. **(confirm with data.)** Source: [`model-jaggedness/jev-1.13`](https://docs.typesafe.ai/model-jaggedness/jev-1.13).
3. **F12 — pin the default model.** `docs/evidence.md` already did the work of showing `jev-latest` and `jev-1.13` agree on this workload; make that the default (`--model=typesafe/jev-1.13` unless overridden) rather than requiring the flag, since the catalogue's triggers were tuned against the pinned build. Source: [`models`](https://docs.typesafe.ai/models).

**Minor:** Model pinned (F12); Values from code are fields, not templates (F20); Untrusted text treated as data (F22); Non-English content handled (F23). These are listed fixes and don't lower the verdict.

[Full rating: every fact, its evidence and the files read →](full/Fox-Islam__jevlint.md)

