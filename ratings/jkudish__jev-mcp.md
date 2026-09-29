[← All ratings](README.md)

*Rated under an earlier rubric (2026-09-28). A re-rating is queued.*

> **jkudish/jev-mcp** at [`a34db93`](https://github.com/jkudish/jev-mcp/tree/a34db9307f437b9514c0d528fe226651e284eb3f) · agent tool
> ### Verdict 3: Use with a fix
> Execution ●●● · Fit ●●○ · Coverage ●●○ · Evidence n.a.
>
> - jev-mcp (v0.10.1, Node 22, MIT, 443 stars) is an MCP server that exposes Jev as 12 judgment tools over TypeSafe, OpenRouter, Cloudflare, Vercel or a compatible endpoint.
> - The awesome-jev list says it wraps three cookbook patterns; CHANGELOG 0.1.0 names them as jev_verify (citation_check), jev_screen (llm_guardrails) and jev_find (semantic_find), and the repo has since grown to 12 tools, so the list entry is stale.
> - The question and state design is good: one request per tool call, typed Nouls and Choices with described options, JSON state with IDs, thresholds as parameters with defaults in code, and every tool fails closed on a malformed answer.
>
> **Top fix:** Move spliced text into JSON state fields: pass claim, query, purpose, proposition and aspect as state fields and point the question at their paths, as jev_classify already does.

## What holds it back

- **Measured in the workflow** (F7): test/mock.test.mjs is mock-provider wire and fail-closed tests, and test/e2e.test.mjs has one to three live assertions per tool (anecdotes, gated on a key). Read in full: test/mock.test.mjs is wire and fail-closed plumbing with hand-fed answers (no golden set); the live e2e has one jev_audit case with five builder-written planted failures (test/e2e.test.mjs, AUDIT_SOURCE) asserted as pass/fail, and no run reports an accuracy, cost or latency number. No labeled evaluation and no calibration of any threshold, so the loop is not closed. The rerank description quotes TypeSafe's CLERC result ([`src/index.ts:888`](https://github.com/jkudish/jev-mcp/blob/a34db9307f437b9514c0d528fe226651e284eb3f/src/index.ts#L888)), not a measurement of this tool. Docs: https://docs.typesafe.ai/cookbooks/classification_using_confidence.md
- **Choice order is handled** (F13): High-stakes Choices exist (verify relation can mark a claim contradicted and jev_gate escalates on it; find's best Choice ranks; classify routes), and no averaging over option orders or shuffle appears anywhere in src/index.ts (grep for shuffle, random, permutation: none), and no test in the full mock or e2e files exercises option order; options are keyed in caller order (c0.., option_0.., candidate ids). Docs: https://docs.typesafe.ai/cookbooks/consistency_choice_cookbook.md

## Fixes (from reading the code; not tested against it)

1. Move spliced text into JSON state fields: pass claim, query, purpose, proposition and aspect as state fields and point the question at their paths, as jev_classify already does.
2. Flag or test untrusted text (F22): add the ANTI_INJECTION sentence used in review, gate and audit to verify, find, rerank, noul, compare, extract and classify, and add a steering test for verify and find as gate has ([`test/mock.test.mjs:1719`](https://github.com/jkudish/jev-mcp/blob/a34db9307f437b9514c0d528fe226651e284eb3f/test/mock.test.mjs#L1719)); answers F22.
3. Handle Choice order (F13): for high-stakes verify, find and classify, average over two or more option orders, or randomize the option order per item.

**Minor:** The model is pinned to a versioned ID (F12); Values from code are fields, not templates (F20); Untrusted text is treated as data (F22); Non-English content is handled (F23). These are listed fixes and don't lower the verdict.

[Full rating: every fact, its evidence and the files read →](full/jkudish__jev-mcp.md)

