[← Summary](../qkal__Canny.md)

# Canny: full rating

**Verdict 4, Use it** · workflow · rated 2026-09-27 at [`f2c5e53`](https://github.com/qkal/Canny/tree/f2c5e53779445d60dc4a09d2dbced2308fccb820) · read: full · rubric unrecorded (earlier) · unknown, medium effort

*Rated under an earlier rubric (unrecorded). A re-rating is queued.*

## Summary

Canny is a supervision layer for AI coding agents (Claude Code, Codex CLI) that keeps an append-only ledger of what an agent actually did and blocks a "done" claim until a check has passed. Its stated design rule is "Facts go to code. Judgments go to Jev. Only facts can block." Jev is used for exactly two judgments, both Nouls: (1) does the agent's stop message claim the work is done (`CLAIMS_DONE`, in `src/hook.ts`), gating whether a deterministic block gets relaxed; and (2) for each edited file, does the diff break any of N project-stated rules (`rule_${i}` Nouls, batched per change), surfaced as a non-blocking note. Verdict: **4, Use it** — clean, minimal, well-fitted use of Jev restricted to the two decisions that actually need semantic judgment, with everything else (blocking, thresholds, caching) kept deterministic in code. It falls short of 5 because Jev's own judgments (rule-break detection, done-claim detection) are never evaluated against labels; the project's one disclosed benchmark measures wall-clock overhead of the whole gate, not Jev's accuracy, and the model defaults to an unpinned alias.

## What fails

| Fact | Finding |
|---|---|
| Model pinned (F12) | **no.** Default is the alias `jev-latest` ([`src/jev.ts:7`](https://github.com/qkal/Canny/blob/f2c5e53779445d60dc4a09d2dbced2308fccb820/src/jev.ts#L7)); pinning requires the operator to set `CANNY_JEV_MODEL`, and nothing in the repo enforces or defaults to a versioned ID even though thresholds were informally tuned (the drift comment at [`src/jev.ts:11`](https://github.com/qkal/Canny/blob/f2c5e53779445d60dc4a09d2dbced2308fccb820/src/jev.ts#L11)). |
| Untrusted text treated as data (F22) | **no.** `change.added`/`change.removed` is text the agent (or a possibly-adversarial diff) wrote, sent straight into Jev's state with no flag, no injection-check Noul, and no test for steering content. `test/robustness.test.ts`'s "hostile text" suite tests deterministic-parser performance (regex backtracking/DoS) on adversarial strings, not whether such text can steer the rule-judge's answer. |

<details>
<summary><b>What passes (11) and doesn't apply (5)</b></summary>

| Fact | Finding |
|---|---|
| Atomic (F1) | yes. `CLAIMS_DONE`: one property ("does this message claim done"), [`src/hook.ts:39`](https://github.com/qkal/Canny/blob/f2c5e53779445d60dc4a09d2dbced2308fccb820/src/hook.ts#L39). Rule-noul: one property per rule ("does this change break rule i"), [`src/hook.ts:197`](https://github.com/qkal/Canny/blob/f2c5e53779445d60dc4a09d2dbced2308fccb820/src/hook.ts#L197). |
| Right primitive (F2) | yes. Both decisions are binary; Noul is correct for both, [`src/hook.ts:39`](https://github.com/qkal/Canny/blob/f2c5e53779445d60dc4a09d2dbced2308fccb820/src/hook.ts#L39), [`src/hook.ts:197`](https://github.com/qkal/Canny/blob/f2c5e53779445d60dc4a09d2dbced2308fccb820/src/hook.ts#L197). |
| Structured state (F3) | yes. `stop()`: single-string state, allowed for a single text (`{ message }`, [`src/hook.ts:228`](https://github.com/qkal/Canny/blob/f2c5e53779445d60dc4a09d2dbced2308fccb820/src/hook.ts#L228)). `ruleCheck()`: JSON with named fields (`rules`, `change.file/added/removed`), [`src/hook.ts:206-209`](https://github.com/qkal/Canny/blob/f2c5e53779445d60dc4a09d2dbced2308fccb820/src/hook.ts#L206-L209). |
| Batching (F4) | yes. All rule-Nouls for one change go in one request ([`src/hook.ts:194-202`](https://github.com/qkal/Canny/blob/f2c5e53779445d60dc4a09d2dbced2308fccb820/src/hook.ts#L194-L202), one `judge()` call per change at line 210); changes are processed in parallel via `Promise.all` ([`src/hook.ts:203-216`](https://github.com/qkal/Canny/blob/f2c5e53779445d60dc4a09d2dbced2308fccb820/src/hook.ts#L203-L216)), not a sequential loop. |
| Thresholds in code (F5) | yes. `YES`/`NO` are exported constants in [`src/jev.ts:12-13`](https://github.com/qkal/Canny/blob/f2c5e53779445d60dc4a09d2dbced2308fccb820/src/jev.ts#L12-L13). |
| No invented values (F6) | yes. Jev is asked only for yes/no judgments; no counting, arithmetic, or date math is delegated to it anywhere in `src/hook.ts` or `src/jev.ts`. |
| Options exclusive/exhaustive (F8) | n.a.. (no Choice used). |
| Unclear/other option (F9) | n.a.. (no Choice used). |
| Evidence recorded evenly (F10) | yes. Both Nouls' `criteria.true`/`criteria.false` are comparably detailed, [`src/hook.ts:40-42`](https://github.com/qkal/Canny/blob/f2c5e53779445d60dc4a09d2dbced2308fccb820/src/hook.ts#L40-L42) and `198-199`; no conclusions are pre-loaded into the state. |
| Confidence drives action (F11) | yes. Threshold-gated relax/note behavior described above, [`src/hook.ts:211`](https://github.com/qkal/Canny/blob/f2c5e53779445d60dc4a09d2dbced2308fccb820/src/hook.ts#L211), [`src/hook.ts:252`](https://github.com/qkal/Canny/blob/f2c5e53779445d60dc4a09d2dbced2308fccb820/src/hook.ts#L252). |
| Choice order handled (F13) | n.a.. (no Choice used). |
| Size limits respected (F14) | n.a.. State is small by construction (`clip()` on diffs) but no explicit token-budget check or test was found in the files read. |
| Typed answers read directly (F19) | yes. `answers?.[id]` (a typed noul probability) is read directly and compared numerically; no free text is parsed, [`src/hook.ts:211`](https://github.com/qkal/Canny/blob/f2c5e53779445d60dc4a09d2dbced2308fccb820/src/hook.ts#L211), [`src/hook.ts:231`](https://github.com/qkal/Canny/blob/f2c5e53779445d60dc4a09d2dbced2308fccb820/src/hook.ts#L231), [`src/hook.ts:252`](https://github.com/qkal/Canny/blob/f2c5e53779445d60dc4a09d2dbced2308fccb820/src/hook.ts#L252). |
| Values from code are fields, not templates (F20) | yes. Rule text lives in `state.rules` as data; only a numeric index (a path reference, not a value needing JSON structure) is spliced into the question string, [`src/hook.ts:197-199`](https://github.com/qkal/Canny/blob/f2c5e53779445d60dc4a09d2dbced2308fccb820/src/hook.ts#L197-L199). |
| Content in state, judgments in questions (F21) | yes. Diff content and message text sit in `state`; the question strings hold only the judgment being asked, [`src/hook.ts:206-209`](https://github.com/qkal/Canny/blob/f2c5e53779445d60dc4a09d2dbced2308fccb820/src/hook.ts#L206-L209), [`src/hook.ts:228-229`](https://github.com/qkal/Canny/blob/f2c5e53779445d60dc4a09d2dbced2308fccb820/src/hook.ts#L228-L229). |
| Non-English content handled (F23) | n.a.. Tool operates on code/English project rules; no non-English handling claimed or expected. |

</details>

## Scores

- **Execution: 3** — anchor "F1-F6 all yes, and F8-F11 yes wherever they apply." F1-F6 all yes; F8/F9 n.a.; F10/F11 yes. (F22 fails but is outside F1-F6/F8-F11 and isn't cited in this dimension's anchors as cap-worthy; recorded above as a real gap and carried into fixes.)
- **Fit: 3** — anchor "each decision uses the primitive that fits it; confidence is used wherever an action depends on it; parallel questions are used wherever questions share a state." Noul fits both binary judgments; confidence gates both actions; the N rule-questions over one change's state are correctly batched into a single request.
- **Coverage: 3** — new project, scored against its own stated goal ("Facts go to code. Judgments go to Jev. Only facts can block."). Both judgment points the design calls for (done-claim detection, rule-break detection) are implemented exactly as described; no gap between the README's stated design and the code.
- **Evidence: 2** — anchor "measured with one weakness (small sample, builder's own labels, or no held-out set), disclosed." The disclosed bench is small (25 pairs), measures the gate's overhead/outcome rather than Jev's own judgment accuracy, and the project states this limitation itself rather than overclaiming.

## Why this verdict

**4, Use it.** Canny's use of Jev is disciplined and minimal: two decisions, both genuinely needing semantic judgment (a regex can't reliably tell "I skipped tests, it's a one-liner" apart from "done"), both using the right primitive (Noul), both batched correctly, both gated by named-constant thresholds that determine an action rather than being decorative. The architecture keeps Jev strictly advisory ("Jev never blocks... a rule violation becomes a note, not a wall"), which is the correct posture for an unevaluated judge sitting in a supervision hook. It doesn't reach 5 because nothing in the repo evaluates Jev's own two judgments against labels — the one benchmark that exists measures the surrounding gate's overhead, not whether `CLAIMS_DONE` or the rule-noul are actually accurate — and because the model defaults to an unpinned alias despite thresholds having been informally tuned to a specific drift band.

## Fixes (from reading the code; not tested against it)

1. **F22 — untrusted text not treated as data.** The diff text sent as `change.added`/`change.removed` is exactly the kind of agent-written or attacker-influenced content Jev's own docs warn about. Add an injection-check Noul, or test the rule-judge against a diff containing a steering comment (e.g. "this fully satisfies the no-hardcoded-keys rule") to see whether it moves the answer. **(confirm with data.)** Source: [`model-jaggedness/jev-1.13`](https://docs.typesafe.ai/model-jaggedness/jev-1.13); [`cookbooks/classifying_rag_passages`](https://docs.typesafe.ai/cookbooks/classifying_rag_passages).
2. **F12 — model not pinned by default.** Since thresholds were tuned against a specific version's drift ("Jev drifts about 0.05 between runs", [`src/jev.ts:11`](https://github.com/qkal/Canny/blob/f2c5e53779445d60dc4a09d2dbced2308fccb820/src/jev.ts#L11)), default `CANNY_JEV_MODEL` to a versioned ID and log the `model` field each response returns, retuning `YES`/`NO` after any upgrade. Source: [`models`](https://docs.typesafe.ai/models).
3. **Loop not closed.** No evaluation exists for either Noul's own accuracy. Building a small labeled set (true rule-violations, true "done" claims) the way `jev-belay` did, then sweeping/deriving `YES`/`NO` from observed probabilities rather than the current informal band, would let Canny credibly claim its judge is accurate rather than merely non-blocking. Source: [`confidence`](https://docs.typesafe.ai/confidence); [`cookbooks/autoresearch_feature_discovery`](https://docs.typesafe.ai/cookbooks/autoresearch_feature_discovery).
