[← Summary](../jkudish__jev-mcp.md)

# jev-mcp: full rating

**Verdict 3, Use with a fix** · agent tool · rated 2026-09-28 at [`a34db93`](https://github.com/jkudish/jev-mcp/tree/a34db9307f437b9514c0d528fe226651e284eb3f) · read: full · rubric 2026-09-28 (earlier) · claude-sonnet-5-5, medium effort

*Rated under an earlier rubric (2026-09-28). A re-rating is queued.*

## Summary

jev-mcp (v0.10.1, Node 22, MIT, 443 stars) is an MCP server that exposes Jev as 12 judgment tools over TypeSafe, OpenRouter, Cloudflare, Vercel or a compatible endpoint. The awesome-jev list says it wraps three cookbook patterns; CHANGELOG 0.1.0 names them as jev_verify (citation_check), jev_screen (llm_guardrails) and jev_find (semantic_find), and the repo has since grown to 12 tools, so the list entry is stale. The question and state design is good: one request per tool call, typed Nouls and Choices with described options, JSON state with IDs, thresholds as parameters with defaults in code, and every tool fails closed on a malformed answer. Two things hold it at 3: the caller's claim, query, proposition or purpose text is spliced into question strings in most tools (F20), and untrusted text has no steering flag outside screen, review, gate and audit (F22). There is also no accuracy measurement on any labels. Verdict: use with a fix.

## What fails

| Fact | Finding |
|---|---|
| Measured in the workflow (F7) | **no.** test/mock.test.mjs is mock-provider wire and fail-closed tests, and test/e2e.test.mjs has one to three live assertions per tool (anecdotes, gated on a key). Read in full: test/mock.test.mjs is wire and fail-closed plumbing with hand-fed answers (no golden set); the live e2e has one jev_audit case with five builder-written planted failures (test/e2e.test.mjs, AUDIT_SOURCE) asserted as pass/fail, and no run reports an accuracy, cost or latency number. No labeled evaluation and no calibration of any threshold, so the loop is not closed. The rerank description quotes TypeSafe's CLERC result ([`src/index.ts:888`](https://github.com/jkudish/jev-mcp/blob/a34db9307f437b9514c0d528fe226651e284eb3f/src/index.ts#L888)), not a measurement of this tool. Docs: https://docs.typesafe.ai/cookbooks/classification_using_confidence.md |
| The model is pinned to a versioned ID (F12) | **no.** `const MODEL = process.env.JEV_MCP_MODEL ?? "jev-latest"` (src/index.ts); the alias is the default, and the thresholds were not tuned on any version. Fix-only. |
| Choice order is handled (F13) | **no.** High-stakes Choices exist (verify relation can mark a claim contradicted and jev_gate escalates on it; find's best Choice ranks; classify routes), and no averaging over option orders or shuffle appears anywhere in src/index.ts (grep for shuffle, random, permutation: none), and no test in the full mock or e2e files exercises option order; options are keyed in caller order (c0.., option_0.., candidate ids). Docs: https://docs.typesafe.ai/cookbooks/consistency_choice_cookbook.md |
| Values from code are fields, not templates (F20) | **no.** Data text is interpolated into question strings: `` `How does the evidence relate to claim \`${claim.id}\` (${claim.text})?` `` ([`src/index.ts:205`](https://github.com/jkudish/jev-mcp/blob/a34db9307f437b9514c0d528fe226651e284eb3f/src/index.ts#L205)), `` `Which candidate contains the best answer to: "${query}"?` `` ([`src/index.ts:512`](https://github.com/jkudish/jev-mcp/blob/a34db9307f437b9514c0d528fe226651e284eb3f/src/index.ts#L512)), `` `The text is useful source material for this task: "${purpose}"` `` ([`src/index.ts:336`](https://github.com/jkudish/jev-mcp/blob/a34db9307f437b9514c0d528fe226651e284eb3f/src/index.ts#L336)), rerank `` `Candidate ${c.key}: ${c.text}` ``, noul `` `proposition \`${p.id}\`: ${p.text}` ``, compare's `aspect`. Classify passes the item as a JSON field (the good pattern). Docs: https://docs.typesafe.ai/primitives/advanced.md |
| Untrusted text is treated as data (F22) | **no.** jev_screen is itself an injection detector, and jev_review, jev_gate and jev_audit append ANTI_INJECTION to every question and test it ([`test/mock.test.mjs:1719-1741`](https://github.com/jkudish/jev-mcp/blob/a34db9307f437b9514c0d528fe226651e284eb3f/test/mock.test.mjs#L1719-L1741)), Steering tests exist only for the tools that already carry the flag: mock jev_gate ([`test/mock.test.mjs:1719`](https://github.com/jkudish/jev-mcp/blob/a34db9307f437b9514c0d528fe226651e284eb3f/test/mock.test.mjs#L1719)), live jev_review and jev_audit injection cases (test/e2e.test.mjs), and the live jev_screen injected-page case (the detector itself). The full mock file has no steering or injection test for the other eight tools. jev_verify, jev_find, jev_rerank, jev_noul, jev_classify, jev_compare, jev_extract and jev_decide send caller or web text with no flag and no steering test; verify and find splice the text into the question itself (F20). Docs: https://docs.typesafe.ai/cookbooks/classifying_rag_passages.md |
| Non-English content is handled (F23) | **no.** Inputs are not stated to be English by design, and no test in the full mock, e2e or unit files, translation step or note covers non-English text. Fix-only. Docs: https://docs.typesafe.ai/concepts/state.md |

<details>
<summary><b>What passes (12) and doesn't apply (5)</b></summary>

| Fact | Finding |
|---|---|
| Atomic questions (F1) | yes. Verify's relation Choice asks one thing (supports, contradicts, says_nothing; [`src/index.ts:205-211`](https://github.com/jkudish/jev-mcp/blob/a34db9307f437b9514c0d528fe226651e284eb3f/src/index.ts#L205-L211)), screen splits injection, substance and relevance into three Nouls ([`src/index.ts:315-340`](https://github.com/jkudish/jev-mcp/blob/a34db9307f437b9514c0d528fe226651e284eb3f/src/index.ts#L315-L340)), jev_find splits "best" from "exists". |
| The right primitive (F2) | yes. Nouls for yes/no (injection, exists, propositions, rerank pair), Choices for one of several (relation, best candidate, classify class), Score with worded levels for review rubrics. |
| Structured state (F3) | yes. State is JSON with IDs: `{ purpose, claims: claimItems, evidence }` ([`src/index.ts:229-233`](https://github.com/jkudish/jev-mcp/blob/a34db9307f437b9514c0d528fe226651e284eb3f/src/index.ts#L229-L233)), `{ query, candidates }` ([`src/index.ts:515`](https://github.com/jkudish/jev-mcp/blob/a34db9307f437b9514c0d528fe226651e284eb3f/src/index.ts#L515)), classify passes `item: { id, text }`; `ensureUniqueIds` guards ID collisions. Screen's single text is one piece of text (S1). |
| Batching (F4) | yes. One `askJev` per tool call with all questions together ([`src/index.ts:235`](https://github.com/jkudish/jev-mcp/blob/a34db9307f437b9514c0d528fe226651e284eb3f/src/index.ts#L235), [`src/index.ts:342`](https://github.com/jkudish/jev-mcp/blob/a34db9307f437b9514c0d528fe226651e284eb3f/src/index.ts#L342), [`src/index.ts:515`](https://github.com/jkudish/jev-mcp/blob/a34db9307f437b9514c0d528fe226651e284eb3f/src/index.ts#L515)); jev_gate proves a single request for 7 questions ([`test/mock.test.mjs:1737`](https://github.com/jkudish/jev-mcp/blob/a34db9307f437b9514c0d528fe226651e284eb3f/test/mock.test.mjs#L1737)). |
| Thresholds in code (F5) | yes. Parameters with defaults: `const autoAccept = auto_accept ?? 0.8` ([`src/index.ts:187`](https://github.com/jkudish/jev-mcp/blob/a34db9307f437b9514c0d528fe226651e284eb3f/src/index.ts#L187)), `block_at ?? 0.75`, `review_at ?? 0.25`; helpers in src/lib.ts (`existsVerdict(exists, found = 0.7, absent = 0.35)`, `screenRecommendation`, `reviewAction`). |
| No invented values (F6) | yes. Jev only picks among supplied options; jev_extract sends only regex candidates so values come back verbatim, and zero-match fields never reach the model (test/e2e.test.mjs jev_extract cases); composite scores are computed in code (REVIEW_WEIGHTS). |
| Options cover every case without overlapping (F8) | yes. Verify's supports, contradicts, says_nothing cover the cases (a partial claim falls to whichever dominates, no separate option); find's Choice is paired with a separate exists Noul so a no-answer case has a home; classify has an escape route via margin and review. |
| An "unclear" or "other" option, where needed (F9) | yes. Verify has says_nothing; find has the exists Noul; extract adds `none_of_them` ([`src/index.ts:1171`](https://github.com/jkudish/jev-mcp/blob/a34db9307f437b9514c0d528fe226651e284eb3f/src/index.ts#L1171)); verify's source Choice adds a `none` option ([`src/index.ts:198-209`](https://github.com/jkudish/jev-mcp/blob/a34db9307f437b9514c0d528fe226651e284eb3f/src/index.ts#L198-L209)); wording differs from any state text. |
| Evidence recorded evenly (F10) | n.a.. The state holds the items being judged, with no per-answer evidence or conclusions. |
| Confidence drives action (F11) | yes. Every tool returns an action (auto, review, escalate, block, pass, skip) from probabilities and thresholds; unknown or malformed confidence escalates ([`test/mock.test.mjs:1575`](https://github.com/jkudish/jev-mcp/blob/a34db9307f437b9514c0d528fe226651e284eb3f/test/mock.test.mjs#L1575), [`test/mock.test.mjs:1592`](https://github.com/jkudish/jev-mcp/blob/a34db9307f437b9514c0d528fe226651e284eb3f/test/mock.test.mjs#L1592)). |
| Size limits are respected (F14) | yes. Per-tool guards: MAX_CANDIDATE_CHARS truncation, MAX_NOUL_TOTAL_CHARS refusal ([`src/index.ts:421-423`](https://github.com/jkudish/jev-mcp/blob/a34db9307f437b9514c0d528fe226651e284eb3f/src/index.ts#L421-L423)), MAX_GATE_EVIDENCE_*, MAX_REVIEW_DOC_CHARS, MAX_AUDIT_REQUEST_CHARS, MAX_EXTRACT_TOTAL_CHARS, with tests that refuse over-budget batches before any request ([`test/mock.test.mjs:759`](https://github.com/jkudish/jev-mcp/blob/a34db9307f437b9514c0d528fe226651e284eb3f/test/mock.test.mjs#L759), [`test/mock.test.mjs:1700`](https://github.com/jkudish/jev-mcp/blob/a34db9307f437b9514c0d528fe226651e284eb3f/test/mock.test.mjs#L1700), [`test/mock.test.mjs:1709`](https://github.com/jkudish/jev-mcp/blob/a34db9307f437b9514c0d528fe226651e284eb3f/test/mock.test.mjs#L1709)). Fix-only. |
| Typed answers are read directly (F19) | yes. Decisions read `noul`, `choice` and probabilities via `validateNoulAnswer` and `validateChoiceAnswer`; no free-text reasoning is requested. |
| No instructions in the state (F21) | yes. State holds content; the builder-written `purpose: "Verify each claim in claims against the evidence in evidence."` ([`src/index.ts:230`](https://github.com/jkudish/jev-mcp/blob/a34db9307f437b9514c0d528fe226651e284eb3f/src/index.ts#L230)) is a fixed label. Spliced source text counts once, under F20. |
| Sample size adequate for the claim (F15) | n.a.. The repo claims no results of its own. |
| Labels independent of the builder (F16) | n.a.. No claimed results. |
| Held-out set (F17) | n.a.. No claimed results. |
| Fair baseline (F18) | n.a.. No claimed results. |

</details>

## Scores

- Execution 3: F1-F6 all yes, F8, F9, F11 yes, F10 n.a., F19 yes. F12, F14 and F23 are fix-only; the failed F20 and F22 do not lower it but cap the verdict.
- Fit 2: "Exactly one mismatch (a failed F13)". Primitives fit each decision, confidence gates every action, and questions share one request; verify, find and classify take the top Choice answer to a high-stakes route with no order handling.
- Coverage 2: "50 to 79% covered". Original decisions or steps for the three tools listed in Coverage below: 9 of 13 kept or changed with a stated reason, 4 dropped without explanation (the fabricated string-match step, the reply-side hazard battery, the harm Score, the strict and permissive policy pair). The repo extends well past them, but that does not count toward the three.
- Evidence n.a.: F7 fails, but the repo claims no results of its own, so the rubric scores n.a. (the borrowed CLERC number is attributed to TypeSafe).

## Why this verdict

3, use with a fix. Execution is a clean 3 and nothing fails F1-F6: the design is sound and the flaws are two mechanical ones. F20 alone caps it at 3: the main verify and find questions embed the claim or query text inside the question string, which lets a poisoned claim or web-page query reach the question text, and F22 confirms nothing flags it in those tools. The design itself is good enough to use once those two are fixed. Fit is 2 because the order of Choice options is never varied on a decision that can block or route.

Lineage note: jev_verify (citation_check), jev_screen (llm_guardrails), jev_find (semantic_find). Later cookbook-derived tools: jev_rerank (rerank_typesafe), jev_audit (sde_cascade), jev_extract (pre_parsed_value_extraction); jev_classify comes from a spike; jev_decide credits thesammykins/jev_ampcode; jev_review and jev_gate adapt burnigtm/jev-mcp; jev_noul and jev_compare are new. Coverage of the three originals:
- citation_check: string match for a missing quote is dropped (input is claim plus evidence, no quote, so "fabricated" never occurs); relation Choice with three options is kept; verdict mapping is kept minus fabricated; 0.8 confidence gate to review is kept.
- llm_guardrails: one Noul per hazard with code thresholds and one request are kept; the hazard set is changed (indirect injection, substance, relevance, in place of jailbreak, harm, diagnosis, self-harm); the pass, review, block, skip routing is a changed version of the two named policies; the harm Score, the reply-side battery and the strict and permissive policy pair are dropped.
- semantic_find: IDs on candidates and a Choice for the best one are kept; the exists Noul is kept; the three-state exists verdict (answered, partial, absent at 0.7 and 0.35) is kept; IDs on 218 clauses become caller-supplied candidates with a cap, changed.

## Fixes (from reading the code; not tested against it)

1. Move spliced text into JSON state fields: pass claim, query, purpose, proposition and aspect as state fields and point the question at their paths, as jev_classify already does.
2. Flag or test untrusted text (F22): add the ANTI_INJECTION sentence used in review, gate and audit to verify, find, rerank, noul, compare, extract and classify, and add a steering test for verify and find as gate has ([`test/mock.test.mjs:1719`](https://github.com/jkudish/jev-mcp/blob/a34db9307f437b9514c0d528fe226651e284eb3f/test/mock.test.mjs#L1719)); answers F22.
3. Handle Choice order (F13): for high-stakes verify, find and classify, average over two or more option orders, or randomize the option order per item.
4. Pin the model where thresholds are tuned (F12, fix-only): default to a `jev-X.Y.Z` ID from docs.typesafe.ai/models rather than `jev-latest`.
5. Diagnosis, data needed: measure verify and screen accuracy on labelled claims and injected pages (F7) to confirm the 0.8 and 0.75 defaults; that is diagnosis work, not a design fix.
6. Non-English (F23, fix-only): add one non-English case to the live tests or state that English is required.

<details>
<summary><b>Files read (18)</b></summary>

All 18 manifest files read in full.
- README.md: read
- CHANGELOG.md: read
- CONTRIBUTING.md: read
- SECURITY.md: read
- package.json: read
- skills/jev/SKILL.md: read
- skills/jev/reference/tools.md: read
- src/index.ts: read
- src/lib.ts: read
- src/provider.ts: read
- test/unit.test.mjs: read
- test/provider.test.mjs: read
- test/typesafe-abort-regression.test.mjs: read
- test/fixtures/typesafe-abort-child.mjs: read
- test/http.test.mjs: read
- test/e2e.test.mjs: read
- test/mock.test.mjs: read
- .github/workflows/ci.yml: read (hidden file .github__workflows__ci.yml; runs typecheck, build, npm test, and the live e2e only when a TYPESAFE_API_KEY secret exists; no evaluation step)

</details>
