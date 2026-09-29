[← Summary](../superagents-lab__jev-search.md)

# jev-search: full rating

**Verdict 3, Use with a fix** · workflow · rated 2026-09-28 at [`67027d0`](https://github.com/superagents-lab/jev-search/tree/67027d0185a9b22eb2a178f0eb15250d12ddabe6) · read: full · rubric 2026-09-28 (earlier) · claude-sonnet-5-5, medium effort

*Rated under an earlier rubric (2026-09-28). A re-rating is queued.*

## Summary

Jev Search (Search1API's web search app, 482 stars, MIT) uses Jev for two jobs. First, one batched request per search reads the user's request and answers about 15 typed questions: a Choice for the time window, one Noul per source (12), and two Choices that pick a search query and a catalogue title from candidates that code builds. Second, every search lane sends its rows (up to 8) to Jev as one Noul per row, "is `results[i]` about the subject in `request`?", and the yes probability orders the page and folds low scores away. Jev only picks among options code supplies; dates, age filtering, merging and ordering are code. It is a well-built retrieve-then-re-rank remix with thresholds in code, but it has three failed facts that each cap the verdict at 3: the entity Choice has no "none of these" option (F9), the window Choice is taken as the top answer and silently drops older rows without looking at confidence (F11), and web snippets and user text reach Jev with no injection flag or test (F22). Nothing is measured on the app's own task (F7), and the model is the `jev-latest` alias.

## What fails

| Fact | Finding |
|---|---|
| Measured in the workflow (F7) | **no.** Tests stub Jev's answers (`test/pipeline.test.ts`, `test/typesafe.test.ts`); no accuracy, precision or agreement number for source choice, window choice or relevance anywhere. Latency is shown to the user per search (`totalMs`) but not reported as a measurement. The README says "Relevance percentages are model judgments, not verified accuracy." |
| An "unclear" or "other" option, where needed (F9) | **no.** The `entity` Choice ("which candidate is just the name or title of the thing") has no "none of these" option, so requests with no named entity ("new papers on speculative decoding") still pick some candidate; the confidence is stored but unused ([`src/lib/pipeline.ts:141`](https://github.com/superagents-lab/jev-search/blob/67027d0185a9b22eb2a178f0eb15250d12ddabe6/src/lib/pipeline.ts#L141)). Only the IMDb lane reads it, so the harm is limited. Window has `any`, query has `c0`, so those are fine. |
| Confidence drives action (F11) | **no.** Source Nouls (0.6) and relevance (0.3 fold, sort by percent) are gated on probabilities. But the window Choice is taken as its top answer ([`src/lib/pipeline.ts:131`](https://github.com/superagents-lab/jev-search/blob/67027d0185a9b22eb2a178f0eb15250d12ddabe6/src/lib/pipeline.ts#L131), `intent.window.choice`) and the age filter then drops older rows, counted as `stale` but never shown in the UI (`working.tsx` has no stale text); query and entity Choices are likewise taken at the top answer. All three confidences are carried in the `intent` event ([`src/lib/pipeline.ts:154`](https://github.com/superagents-lab/jev-search/blob/67027d0185a9b22eb2a178f0eb15250d12ddabe6/src/lib/pipeline.ts#L154)) and read by nothing. |
| Model pinned (fix-only) (F12) | **no.** `TYPESAFE_MODEL = 'jev-latest'` ([`src/lib/typesafe.ts:73`](https://github.com/superagents-lab/jev-search/blob/67027d0185a9b22eb2a178f0eb15250d12ddabe6/src/lib/typesafe.ts#L73)), `wrangler.jsonc` vars `jev-latest` / `typesafe-ai/jev` / `typesafe/jev`; the `model` a response returns is surfaced only as `usage`, not logged. |
| Untrusted text treated as data (F22) | **no.** The user's request and third-party titles and snippets from Reddit, X, WeChat, Yandex and the rest of the open web go into the state with no flag, no injection Noul and no test of steering text; the tests use benign fixtures only ("Hair up in a bun", `test/pipeline.test.ts`). A snippet that reads like an instruction can move its own relevance score. |
| Non-English content handled (fix-only) (F23) | **no.** The app takes Chinese and Russian content (WeChat and Yandex lanes; `candidates.ts` strips Chinese phrases; `CONTRIBUTING.md` welcomes multilingual searches), but the only Chinese test is the candidate builder (`test/candidates.test.ts`, a code test); relevance of non-English snippets is not tested with Jev and not translated alongside. |

<details>
<summary><b>What passes (11) and doesn't apply (6)</b></summary>

| Fact | Finding |
|---|---|
| Atomic questions (F1) | yes. Each source question asks one thing ("Would Hacker News threads fit this request?", `sources.ts`); the rerank question is one property ("Is `results[i]` about the subject the user asked for in `request`?", [`src/lib/typesafe.ts:428`](https://github.com/superagents-lab/jev-search/blob/67027d0185a9b22eb2a178f0eb15250d12ddabe6/src/lib/typesafe.ts#L428)). The `query` question ("best keyword query ... prefer the candidate that keeps the subject and drops words about time, sources or phrasing") folds a preference rule into one selection; it is one pick among candidates, not two judgments. |
| The right primitive (F2) | yes. Noul for each yes/no source and relevance question, Choice for the window (four named options) and the candidate picks ([`src/lib/typesafe.ts:319-350`](https://github.com/superagents-lab/jev-search/blob/67027d0185a9b22eb2a178f0eb15250d12ddabe6/src/lib/typesafe.ts#L319-L350)). Relevance uses the Noul's yes probability, as the re-ranking cookbook does; the criteria are binary ("about the same subject, even briefly"). |
| Structured state (F3) | yes. Intent state is `{request, now, candidates: {c0.., }}` with IDs; rerank state is `{request, results: [{source, title, snippet}]}` with questions pointing at `results[i]` ([`src/lib/typesafe.ts:361-370`](https://github.com/superagents-lab/jev-search/blob/67027d0185a9b22eb2a178f0eb15250d12ddabe6/src/lib/typesafe.ts#L361-L370), [`src/lib/typesafe.ts:430-440`](https://github.com/superagents-lab/jev-search/blob/67027d0185a9b22eb2a178f0eb15250d12ddabe6/src/lib/typesafe.ts#L430-L440)). Array-index paths, mapped back to item IDs in code; no explicit `id` field in the state. |
| Batching (F4) | yes. All intent questions go in one request; each lane's rows go in one request of up to 40 Nouls (`RERANK_BATCH = 40`, [`src/lib/typesafe.ts:405`](https://github.com/superagents-lab/jev-search/blob/67027d0185a9b22eb2a178f0eb15250d12ddabe6/src/lib/typesafe.ts#L405); lane cap is 8 rows). Per-lane requests instead of one big batch are deliberate so results stream (`pipeline.ts` runLane). |
| Thresholds in code (F5) | yes. `SOURCE_PROB_THRESHOLD = 0.6` ([`src/lib/pipeline.ts:86`](https://github.com/superagents-lab/jev-search/blob/67027d0185a9b22eb2a178f0eb15250d12ddabe6/src/lib/pipeline.ts#L86)), `OFF_TOPIC = 0.3` ([`src/components/results.tsx:73`](https://github.com/superagents-lab/jev-search/blob/67027d0185a9b22eb2a178f0eb15250d12ddabe6/src/components/results.tsx#L73)). Not tuned on labels (see F7), but they are code constants. |
| No invented values (F6) | yes. Jev picks a window, a source, a candidate or a yes probability; code builds the candidate strings (`candidates.ts`), computes age and staleness (`freshness.ts`), filters (`pipeline.ts`, `maxAge = win.hours * WINDOW_TOLERANCE`) and merges. |
| Options exclusive and exhaustive (F8) | yes. Window options are ordered from `any` (no time cue) through 24h, 7d, 30d with descriptions ("today or the last day" / "up to a week" / "up to a month"), and `any` catches everything else. Query and entity options are candidates that always include the untouched request as `c0`, so a usable option always exists. |
| Evidence recorded evenly (F10) | yes. Every result row carries the same three fields (source, title, snippet) and no conclusions; the age prefix is stripped from snippets in code (`stripAgePrefix`). The candidates appear in both the state and the Choice criteria, which is a duplication, not a conclusion. |
| Choice order handled (F13) | n.a.. No Choice is high-stakes: the window and source chips are shown and one click overrides them ("let Jev decide" resets, `filters.tsx`), the query is displayed as "Looking for “…”", and `c0` is always the user's own words. This is a judgment call: window drops rows before the reader can react, so another rater could rate it no. Order is fixed either way (`WINDOWS` order, candidates from `buildCandidates`). |
| Size limits respected (fix-only) (F14) | n.a.. Query capped at 300 characters ([`src/components/search-box.tsx:81`](https://github.com/superagents-lab/jev-search/blob/67027d0185a9b22eb2a178f0eb15250d12ddabe6/src/components/search-box.tsx#L81), [`src/routes/search.tsx:32`](https://github.com/superagents-lab/jev-search/blob/67027d0185a9b22eb2a178f0eb15250d12ddabe6/src/routes/search.tsx#L32)), 8 rows per lane, batch constant of 40; small by construction, no token guard or reported maximum, so unverified. |
| Typed answers read directly (F19) | yes. `noul`, `choice`, `probabilities`, [`confidence`](https://docs.typesafe.ai/confidence) read as typed fields ([`src/lib/typesafe.ts:355-392`](https://github.com/superagents-lab/jev-search/blob/67027d0185a9b22eb2a178f0eb15250d12ddabe6/src/lib/typesafe.ts#L355-L392), [`src/lib/typesafe.ts:445-460`](https://github.com/superagents-lab/jev-search/blob/67027d0185a9b22eb2a178f0eb15250d12ddabe6/src/lib/typesafe.ts#L445-L460)); the only string handling is `Number(choice.slice(1))` on a code-generated id. |
| Values from code are fields, not templates (F20) | yes. Instructions splice only builder-written text and an index (`About \`request\`: ${s.ask.question}`, `results[${i}]`); user text, titles and snippets go in state fields or in the `criteria` JSON. |
| No instructions in the state (F21) | yes. The state holds the request, the date, the candidates and result fields; the judgments live in the questions. |
| Sample size (F15) | n.a.. The project reports no accuracy result. |
| Independent labels (F16) | n.a.. No claim, no labels. |
| Held-out set (F17) | n.a.. No claim, no numbers. |
| Fair baseline (F18) | n.a.. No claim; the README disclaims verified accuracy. |

</details>

## Scores

- **Jev execution: 2.** F1-F6 all yes, so none of the "one of F1-F6 is no" anchor applies, but the 3 anchor needs F8-F11 yes wherever they apply and F9 and F11 fail. The nearest anchor is 2: both failures sit on the secondary decisions (the entity Choice and the window and query Choices); the main decisions (source Nouls, relevance Nouls) are clean. F22 fails but per the rubric it caps the verdict only.
- **Fit of Jev's features: 2.** Anchor "exactly one mismatch (the top answer taken where confidence should gate)": window and query Choices take the top answer, though confidence is available and a wrong window silently drops rows. Otherwise the fit is good: Noul per yes/no, Choice for named options, one request for shared state, and no Score where none is needed. F13 is n.a., so it adds no second mismatch.
- **Coverage: 3.** Anchor "80% or more covered." Rerank cookbook steps: fast search shortlist (kept: Search1API engines), one Noul per query-candidate pair (kept), query and candidate in one state (kept), sort by the Noul probability (kept, plus engine agreement and engine rank as tie-breakers), shortlist of about 30 (changed: 8 per lane, lanes merged by URL), and evaluate against the fast-search-only baseline (dropped, unexplained). Intent-routing pattern: classify then route to handlers (kept as source and window selection), confidence check on the routing answer (kept for sources only). 5 of 7 kept, 1 changed, 1 dropped, and the stated goal (choose sources and ranking, no generated answers) is what the code does.
- **Evidence: n.a.** Nothing is claimed and the README says the percentages are model judgments, not verified accuracy. F7 is a no (nothing measured) and goes into the fixes.

## Why this verdict

**3, Use with a fix.** No fatal flaw: F1 holds on both main decisions, F6 holds, and confidence is used for the two decisions that are actually high-volume (source choice, relevance). Execution is 2 and Fit is 2, so it is not a 4 under "Use it" once F9, F11 and F22 each cap it. Every failed fact is cheap to fix: none needs a redesign. The largest gap is not in the design but in the missing measurement: the relevance and source numbers are shown to users as "% on topic" with no evidence for how right they are.

## Fixes (from reading the code; not tested against it)

1. **F22, untrusted text not treated as data** (`typesafe.ts` rerank state; `test/pipeline.test.ts` benign fixtures only). Add an injection-check Noul per row ("does this snippet contain instructions aimed at a ranking system?") in the same rerank request, fold flagged rows out, and add adversarial snippets to the tests. Source: [`model-jaggedness/jev-1.13`](https://docs.typesafe.ai/model-jaggedness/jev-1.13); [`cookbooks/classifying_rag_passages`](https://docs.typesafe.ai/cookbooks/classifying_rag_passages).
2. **F11, confidence ignored on the window and query Choices** ([`src/lib/pipeline.ts:131`](https://github.com/superagents-lab/jev-search/blob/67027d0185a9b22eb2a178f0eb15250d12ddabe6/src/lib/pipeline.ts#L131), [`src/lib/pipeline.ts:140`](https://github.com/superagents-lab/jev-search/blob/67027d0185a9b22eb2a178f0eb15250d12ddabe6/src/lib/pipeline.ts#L140)). Fall back to `any` for the window (and to `c0` for the query) below a confidence constant, and show the `stale` count in the UI so dropped rows are visible. Source: [`confidence`](https://docs.typesafe.ai/confidence), [`patterns/confidence-routing`](https://docs.typesafe.ai/patterns/confidence-routing).
3. **F9, no "none of these" for the entity Choice** ([`src/lib/typesafe.ts:345`](https://github.com/superagents-lab/jev-search/blob/67027d0185a9b22eb2a178f0eb15250d12ddabe6/src/lib/typesafe.ts#L345)). Add an "other" option worded unlike the candidates, or pair it with a Noul "does the request name a specific title?" and only send the entity query to IMDb when it is yes. Source: [`primitives`](https://docs.typesafe.ai/primitives) (Choice).
4. **F7, nothing measured** (`test/` mocks Jev). Label about 100 to 200 real requests (an LLM panel is fine as silver labels), report source-choice and relevance precision and recall at 0.6 and 0.3, and set both thresholds from that. Source: [`cookbooks/classification_using_confidence`](https://docs.typesafe.ai/cookbooks/classification_using_confidence); TypeSafe's workflow evals. That is diagnosis work, not a design fix.
5. **F12, model alias** (fix-only). Pin the versioned ID from `docs.typesafe.ai/models` once thresholds are tuned, log the `model` field each response returns, and retune after upgrades. Source: [`models`](https://docs.typesafe.ai/models).
6. **F23, non-English untested** (fix-only). Add Chinese and Russian request and snippet cases through the real Jev path, or put an English translation beside non-English snippets. Source: [`concepts/state`](https://docs.typesafe.ai/concepts/state), [`models`](https://docs.typesafe.ai/models).

<details>
<summary><b>Files read (46)</b></summary>

Depth `full`: all 46 files in the manifest were read; none were skipped.
- .dev.vars.example: read
- .env.example: read (same variables as .dev.vars.example)
- CONTRIBUTING.md: read
- README.md: read
- design-context.md: read
- package.json: read
- src/components/filters.tsx: read
- src/components/home-demos.tsx: read
- src/components/logo.tsx: read
- src/components/pwa-register.tsx: read
- src/components/repository-link.tsx: read
- src/components/results.tsx: read
- src/components/search-box.tsx: read
- src/components/source-icon.tsx: read
- src/components/sponsor-link.tsx: read
- src/components/wordmark.tsx: read
- src/components/working.tsx: read
- src/lib/candidates.ts: read
- src/lib/freshness.ts: read
- src/lib/judge-config.ts: read
- src/lib/merge.ts: read
- src/lib/pipeline.ts: read
- src/lib/rank.ts: read
- src/lib/sources.ts: read
- src/lib/stable-order.ts: read
- src/lib/typesafe.ts: read
- src/lib/use-ask.ts: read
- src/lib/use-stable-order.ts: read
- src/lib/utils.ts: read
- src/routes/__root.tsx: read
- src/routes/api/ask.ts: read
- src/routes/index.tsx: read
- src/routes/search.tsx: read
- src/server/env.server.ts: read
- test/candidates.test.ts: read
- test/filters.test.ts: read
- test/freshness.test.ts: read
- test/judge-config.test.ts: read
- test/merge.test.ts: read
- test/pipeline.test.ts: read
- test/rank.test.ts: read
- test/results.test.ts: read
- test/search-timeout.test.ts: read
- test/stable-order.test.ts: read
- test/typesafe.test.ts: read
- wrangler.jsonc: read
Files outside the manifest (`src/lib/search1api.ts`, `cache.ts`, `validate.ts`, `seo.ts`) were not read; the tests that exercise them show no Jev call or threshold in them.

</details>
