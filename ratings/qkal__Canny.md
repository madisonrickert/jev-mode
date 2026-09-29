[← All ratings](README.md)

*Rated under an earlier rubric (unrecorded). A re-rating is queued.*

> **qkal/Canny** at [`f2c5e53`](https://github.com/qkal/Canny/tree/f2c5e53779445d60dc4a09d2dbced2308fccb820) · workflow
> ### Verdict 4: Use it
> Execution ●●● · Fit ●●● · Coverage ●●● · Evidence ●●○
>
> - Canny is a supervision layer for AI coding agents (Claude Code, Codex CLI) that keeps an append-only ledger of what an agent actually did and blocks a "done" claim until a check has passed.
> - Its stated design rule is "Facts go to code. Judgments go to Jev. Only facts can block."
> - Jev is used for exactly two judgments, both Nouls: (1) does the agent's stop message claim the work is done (`CLAIMS_DONE`, in `src/hook.ts`), gating whether a deterministic block gets relaxed; and (2) for each edited file, does the diff break any of N project-stated rules (`rule_${i}` Nouls, batched per change), surfaced as a non-blocking note.
>
> **Top fix:** Add an injection-check Noul, or test the rule-judge against a diff containing a steering comment (e.g. "this fully satisfies the no-hardcoded-keys rule") to see whether it moves the answer.

## What holds it back

Nothing that lowers the verdict.

## Fixes (from reading the code; not tested against it)

1. **F22 — untrusted text not treated as data.** The diff text sent as `change.added`/`change.removed` is exactly the kind of agent-written or attacker-influenced content Jev's own docs warn about. Add an injection-check Noul, or test the rule-judge against a diff containing a steering comment (e.g. "this fully satisfies the no-hardcoded-keys rule") to see whether it moves the answer. **(confirm with data.)** Source: [`model-jaggedness/jev-1.13`](https://docs.typesafe.ai/model-jaggedness/jev-1.13); [`cookbooks/classifying_rag_passages`](https://docs.typesafe.ai/cookbooks/classifying_rag_passages).
2. **F12 — model not pinned by default.** Since thresholds were tuned against a specific version's drift ("Jev drifts about 0.05 between runs", [`src/jev.ts:11`](https://github.com/qkal/Canny/blob/f2c5e53779445d60dc4a09d2dbced2308fccb820/src/jev.ts#L11)), default `CANNY_JEV_MODEL` to a versioned ID and log the `model` field each response returns, retuning `YES`/`NO` after any upgrade. Source: [`models`](https://docs.typesafe.ai/models).
3. **Loop not closed.** No evaluation exists for either Noul's own accuracy. Building a small labeled set (true rule-violations, true "done" claims) the way `jev-belay` did, then sweeping/deriving `YES`/`NO` from observed probabilities rather than the current informal band, would let Canny credibly claim its judge is accurate rather than merely non-blocking. Source: [`confidence`](https://docs.typesafe.ai/confidence); [`cookbooks/autoresearch_feature_discovery`](https://docs.typesafe.ai/cookbooks/autoresearch_feature_discovery).

**Minor:** Model pinned (F12); Untrusted text treated as data (F22). These are listed fixes and don't lower the verdict.

[Full rating: every fact, its evidence and the files read →](full/qkal__Canny.md)

