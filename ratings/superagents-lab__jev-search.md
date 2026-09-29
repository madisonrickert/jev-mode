[← All ratings](README.md)

*Rated under an earlier rubric (2026-09-28). A re-rating is queued.*

> **superagents-lab/jev-search** at [`67027d0`](https://github.com/superagents-lab/jev-search/tree/67027d0185a9b22eb2a178f0eb15250d12ddabe6) · workflow
> ### Verdict 3: Use with a fix
> Execution ●●○ · Fit ●●○ · Coverage ●●● · Evidence n.a.
>
> - Jev Search (Search1API's web search app, 482 stars, MIT) uses Jev for two jobs.
> - First, one batched request per search reads the user's request and answers about 15 typed questions: a Choice for the time window, one Noul per source (12), and two Choices that pick a search query and a catalogue title from candidates that code builds.
> - Second, every search lane sends its rows (up to 8) to Jev as one Noul per row, "is `results[i]` about the subject in `request`?", and the yes probability orders the page and folds low scores away.
>
> **Top fix:** Add an injection-check Noul per row ("does this snippet contain instructions aimed at a ranking system?") in the same rerank request, fold flagged rows out, and add adversarial snippets to the tests.

## What holds it back

- **Measured in the workflow** (F7): Tests stub Jev's answers (`test/pipeline.test.ts`, `test/typesafe.test.ts`); no accuracy, precision or agreement number for source choice, window choice or relevance anywhere. Latency is shown to the user per search (`totalMs`) but not reported as a measurement. The README says "Relevance percentages are model judgments, not verified accuracy."
- **An "unclear" or "other" option, where needed** (F9): The `entity` Choice ("which candidate is just the name or title of the thing") has no "none of these" option, so requests with no named entity ("new papers on speculative decoding") still pick some candidate; the confidence is stored but unused ([`src/lib/pipeline.ts:141`](https://github.com/superagents-lab/jev-search/blob/67027d0185a9b22eb2a178f0eb15250d12ddabe6/src/lib/pipeline.ts#L141)). Only the IMDb lane reads it, so the harm is limited. Window has `any`, query has `c0`, so those are fine.
- **Confidence drives action** (F11): Source Nouls (0.6) and relevance (0.3 fold, sort by percent) are gated on probabilities. But the window Choice is taken as its top answer ([`src/lib/pipeline.ts:131`](https://github.com/superagents-lab/jev-search/blob/67027d0185a9b22eb2a178f0eb15250d12ddabe6/src/lib/pipeline.ts#L131), `intent.window.choice`) and the age filter then drops older rows, counted as `stale` but never shown in the UI (`working.tsx` has no stale text); query and entity Choices are likewise taken at the top answer. All three confidences are carried in the `intent` event ([`src/lib/pipeline.ts:154`](https://github.com/superagents-lab/jev-search/blob/67027d0185a9b22eb2a178f0eb15250d12ddabe6/src/lib/pipeline.ts#L154)) and read by nothing.

## Fixes (from reading the code; not tested against it)

1. **F22, untrusted text not treated as data** (`typesafe.ts` rerank state; `test/pipeline.test.ts` benign fixtures only). Add an injection-check Noul per row ("does this snippet contain instructions aimed at a ranking system?") in the same rerank request, fold flagged rows out, and add adversarial snippets to the tests. Source: [`model-jaggedness/jev-1.13`](https://docs.typesafe.ai/model-jaggedness/jev-1.13); [`cookbooks/classifying_rag_passages`](https://docs.typesafe.ai/cookbooks/classifying_rag_passages).
2. **F11, confidence ignored on the window and query Choices** ([`src/lib/pipeline.ts:131`](https://github.com/superagents-lab/jev-search/blob/67027d0185a9b22eb2a178f0eb15250d12ddabe6/src/lib/pipeline.ts#L131), [`src/lib/pipeline.ts:140`](https://github.com/superagents-lab/jev-search/blob/67027d0185a9b22eb2a178f0eb15250d12ddabe6/src/lib/pipeline.ts#L140)). Fall back to `any` for the window (and to `c0` for the query) below a confidence constant, and show the `stale` count in the UI so dropped rows are visible. Source: [`confidence`](https://docs.typesafe.ai/confidence), [`patterns/confidence-routing`](https://docs.typesafe.ai/patterns/confidence-routing).
3. **F9, no "none of these" for the entity Choice** ([`src/lib/typesafe.ts:345`](https://github.com/superagents-lab/jev-search/blob/67027d0185a9b22eb2a178f0eb15250d12ddabe6/src/lib/typesafe.ts#L345)). Add an "other" option worded unlike the candidates, or pair it with a Noul "does the request name a specific title?" and only send the entity query to IMDb when it is yes. Source: [`primitives`](https://docs.typesafe.ai/primitives) (Choice).

**Minor:** Model pinned (fix-only) (F12); Untrusted text treated as data (F22); Non-English content handled (fix-only) (F23). These are listed fixes and don't lower the verdict.

[Full rating: every fact, its evidence and the files read →](full/superagents-lab__jev-search.md)

