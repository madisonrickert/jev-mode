[← Summary](../valentynkit__jev-belay.md)

# jev-belay: full rating

**Verdict 4, Use it** · workflow · rated 2026-09-27 at [`ef719db`](https://github.com/valentynkit/jev-belay/tree/ef719db7eaadc56aa4def86c4da4ffff5bcbca35) · read: full · rubric unrecorded (earlier) · unknown, medium effort

*Rated under an earlier rubric (unrecorded). A re-rating is queued.*

## Summary

jev-belay is a Claude Code `Stop` hook that refuses to let a turn end on an unverified "done." Two free, local regex belts read the transcript for whether a runner was named or a runner's own summary appears in the output; only when files changed and nothing fresh passed does it spend one Jev call (`jev-1.13.0`, four batched questions: three Nouls — `claims_done`, `claims_verified`, `verification_applies` — and one Choice, `outcome`) to judge whether the closing message is a false claim of completion. A hard code-side veto (a fresh passing check) can never be overridden by Jev's answer. Verdict: **4, Use it** — clean, minimal, well-fitted use restricted to the one judgment a regex can't make (does this prose present the work as finished), everything else (mutation counts, check results, thresholds, the veto) computed in code. It misses 5 on two counts: the `outcome` Choice is high-stakes (it can veto the whole block) but its option order is never averaged or randomized (F13), and the one measured result, while genuinely evaluated with a stated sample and a fair ablation, had its operating threshold swept on the same 100-stop audit slice used to report the headline AUROC, and the sample behind that AUROC is small (12 positives, disclosed 95% CI of 0.915–1.000).

## What fails

| Fact | Finding |
|---|---|
| Choice order handled (F13) | **no.** `outcome` is high-stakes (a `blocked` pick vetoes the whole decision, [`belay.mjs:568`](https://github.com/valentynkit/jev-belay/blob/ef719db7eaadc56aa4def86c4da4ffff5bcbca35/belay.mjs#L568)) but nothing in `belay.mjs`, `tui.mjs`, or `tools/measure.mjs` averages it over option orders or randomizes the order per item. `OUTCOME_FLOOR` gates on confidence, which is a different mitigation than order-stability. |
| Held-out set, or data not used for tuning (F17) | **no.** CHANGELOG 0.2.0: "the `claims_done` threshold is 0.70... on the re-extracted corpus... 0.70 is the lowest cutoff holding wrong blocks under 2%... [same measurement] same 100-stop audit slice with 12 false dones... AUROC 0.976." The operating threshold was swept and the headline metric was reported on the identical audit slice, not a held-out split. |

<details>
<summary><b>What passes (21) and doesn't apply (0)</b></summary>

| Fact | Finding |
|---|---|
| Atomic (F1) | yes. Each of the 4 questions asks one property ([`belay.mjs:416-450`](https://github.com/valentynkit/jev-belay/blob/ef719db7eaadc56aa4def86c4da4ffff5bcbca35/belay.mjs#L416-L450)); none joins two judgments. |
| Right primitive (F2) | yes. Noul for the three yes/no judgments, Choice for the one named-options judgment, all four options described in words with no bare numbers ([`belay.mjs:416-450`](https://github.com/valentynkit/jev-belay/blob/ef719db7eaadc56aa4def86c4da4ffff5bcbca35/belay.mjs#L416-L450)). |
| Structured state (F3) | yes. `buildState` returns a JSON object with named fields (`task`, `final_message`, `run.file_changes`, `run.checks_run`); no item IDs needed since it's a single stop, not a dataset ([`belay.mjs:470-480`](https://github.com/valentynkit/jev-belay/blob/ef719db7eaadc56aa4def86c4da4ffff5bcbca35/belay.mjs#L470-L480)). |
| Batching (F4) | yes. One `fetch` per stop carries all four questions ([`belay.mjs:504`](https://github.com/valentynkit/jev-belay/blob/ef719db7eaadc56aa4def86c4da4ffff5bcbca35/belay.mjs#L504), [`belay.mjs:510`](https://github.com/valentynkit/jev-belay/blob/ef719db7eaadc56aa4def86c4da4ffff5bcbca35/belay.mjs#L510)). |
| Thresholds in code (F5) | yes. `DEFAULT_THRESHOLD`, `APPLIES_THRESHOLD`, `OUTCOME_FLOOR` are named constants ([`belay.mjs:551`](https://github.com/valentynkit/jev-belay/blob/ef719db7eaadc56aa4def86c4da4ffff5bcbca35/belay.mjs#L551), [`belay.mjs:552`](https://github.com/valentynkit/jev-belay/blob/ef719db7eaadc56aa4def86c4da4ffff5bcbca35/belay.mjs#L552), [`belay.mjs:555`](https://github.com/valentynkit/jev-belay/blob/ef719db7eaadc56aa4def86c4da4ffff5bcbca35/belay.mjs#L555)). |
| No invented values (F6) | yes. `evidence.mutations` and the check pass/fail results are computed by regex belts in code ([`belay.mjs:88-150`](https://github.com/valentynkit/jev-belay/blob/ef719db7eaadc56aa4def86c4da4ffff5bcbca35/belay.mjs#L88-L150), `freshChecks`); Jev is only asked to judge the prose, never to count or compute. |
| Options exclusive/exhaustive (F8) | yes. `outcome`'s four options (complete/partial/blocked/other) are exclusive by construction and "other" catches every remaining case ([`belay.mjs:441-450`](https://github.com/valentynkit/jev-belay/blob/ef719db7eaadc56aa4def86c4da4ffff5bcbca35/belay.mjs#L441-L450)). |
| Unclear/other option, worded differently from the state (F9) | yes. `other: "None of these"` doesn't echo any state field wording ([`belay.mjs:448`](https://github.com/valentynkit/jev-belay/blob/ef719db7eaadc56aa4def86c4da4ffff5bcbca35/belay.mjs#L448)). |
| Evidence recorded evenly (F10) | yes. `task` (head-capped) and `final_message` (tail-capped) get comparable treatment; `run.checks_run` states facts (`call -> passed/failed`), not conclusions ([`belay.mjs:453-480`](https://github.com/valentynkit/jev-belay/blob/ef719db7eaadc56aa4def86c4da4ffff5bcbca35/belay.mjs#L453-L480)). |
| Confidence drives action (F11) | yes. strongly. Every branch of `decide()` reads a probability against a named threshold rather than taking a top answer blindly ([`belay.mjs:557-581`](https://github.com/valentynkit/jev-belay/blob/ef719db7eaadc56aa4def86c4da4ffff5bcbca35/belay.mjs#L557-L581)). |
| Model pinned (F12) | yes. Default is the versioned `jev-1.13.0`, and every CHANGELOG "Measured" entry names it ([`belay.mjs:18`](https://github.com/valentynkit/jev-belay/blob/ef719db7eaadc56aa4def86c4da4ffff5bcbca35/belay.mjs#L18)). |
| Size limits respected (F14) | yes. 1,500 + 2,000 char caps plus a small `run` object are far under 32k/64k tokens ([`belay.mjs:453-454`](https://github.com/valentynkit/jev-belay/blob/ef719db7eaadc56aa4def86c4da4ffff5bcbca35/belay.mjs#L453-L454)); the real median call measured 1,222 input tokens (README). |
| Typed answers read directly (F19) | yes. `decide()` reads `.noul`, `.choice`, and `.confidence`/`.probabilities` fields directly; no free text is parsed anywhere in the decision path ([`belay.mjs:557-568`](https://github.com/valentynkit/jev-belay/blob/ef719db7eaadc56aa4def86c4da4ffff5bcbca35/belay.mjs#L557-L568)). |
| Values from code as fields, not templates (F20) | yes. No question string has a code value spliced into it; the questions reference field names (`` `final_message` ``, `` `task` ``) generically. |
| Content in state, judgments in questions (F21) | yes. The turn's task/message text lives in `state`; the four question strings hold only the judgment being asked ([`belay.mjs:416-480`](https://github.com/valentynkit/jev-belay/blob/ef719db7eaadc56aa4def86c4da4ffff5bcbca35/belay.mjs#L416-L480)). |
| Untrusted text treated as data (F22) | yes. with direct evidence of testing. `test/jaggedness.test.mjs` has a code-side test ("a planted instruction cannot reach the decision path") proving the hard evidence veto holds regardless of what Jev returns, and live-endpoint tests ("a planted instruction does not flip the verdict") that assert an injected `SYSTEM:` line inside `final_message` does not change the block decision. |
| Non-English content handled (F23) | yes. tested. Same file has a live test ("a non-English message still separates") asserting a Russian completion claim still scores `claims_done > 0.5`. |
| Measured in the workflow (F7) | yes. README and CHANGELOG report AUROC on a labeled audit slice for three consecutive versions (0.729→0.965 in 0.1.1, then 0.777/0.886/0.976 in 0.2.0's ablation), plus cost ($0.00005/call) and latency (346 ms median) from 122 real API calls. |
| Sample size stated, adequacy disclosed (F15) | yes. with a disclosed weakness. n=100 audited stops, 12 positives (false dones); a Hanley-McNeil 95% CI is printed next to every AUROC (0.976 → [0.915, 1.000]) and `tools/measure.mjs`'s own comment says the interval "is wider than the entire distance between limpet's 0.50 and the 0.60 this project has to clear," i.e. the project names its own sample as thin. |
| Labels independent of the builder, or disclosed (F16) | yes. disclosed. `corpus/RUBRIC.md` records a `source` per label: `human` (interactive) or `claude-sonnet-proxy` (a single model applying the rubric), and explicitly calls the proxy path "the noisy-label problem this slice exists to reduce," publishing the source next to every number rather than presenting it as gold. |
| Fair baseline (F18) | yes. The ablation compares the same data across three arms (wording alone 0.777, +evidence gate 0.886, full hook 0.976) plus a cited independent baseline (limpet's separately-measured 0.50 on a different corpus) — same-data, apples-to-apples comparison for the ablation, an honest cross-project citation for the outside baseline. |

</details>

## Scores

- **Execution: 3** — anchor "F1-F6 all yes, and F8-F11 yes wherever they apply." All of F1-F6 and F8-F11 are yes (see Facts).
- **Fit: 2** — anchor "Exactly one mismatch." Primitive choice fits both judgment types, confidence gates every action, and the one request is already fully batched — but F13 is a real mismatch: `outcome` is a high-stakes Choice (it can veto the block) with no order-averaging or per-item randomization, which is exactly the instability Choice is known for.
- **Coverage: 3** — new project scored against its own stated goal (a cheap, evidence-gated, fail-open check against false "done" claims). The code implements every piece the README describes: the two-belt evidence gate, the single batched Jev call, the hard veto, the nudge, shadow mode, the decision log, the session guard, and a documented, disclosed honest limit (read-only turns never reach the question) rather than a silent gap.
- **Evidence: 2** — anchor "Measured with one weakness (small sample, builder's own labels, or no held-out set), disclosed." This project actually discloses two related weaknesses together — a small audit slice (12 positives, wide CI) and a threshold swept on the same slice used to report the metric — but does so with real method (AUROC, CIs, a same-data ablation, a fair outside-baseline citation, repeated across three versions, improving each time). That combination of real rigor plus disclosed, non-trivial weakness keeps it at 2 rather than dropping to 1 ("numbers without method") or reaching 3 ("held out, independent labels, fair baseline").

## Why this verdict

**4, Use it.** Execution and Fit are both at least 2, and no fact from the F1-F6/F8-F11 set (the set that can cap a verdict at 3) fails: every core-execution and question-design fact is yes. There's no fatal flaw either — F1 doesn't fail on the main decision, F6 doesn't fail (all arithmetic and counting is in code), and confidence is not ignored on the one high-stakes action (the block is gated on three separate thresholds). The one real design gap (F13, unhandled Choice-order instability on a Choice that can veto) and the one real evidence gap (threshold tuned and reported on the same audit slice) are each real but neither is fatal, so the verdict sits at 4 rather than 5 or 3.

## Fixes (from reading the code; not tested against it)

1. **F13 — Choice order unhandled on a high-stakes pick.** Average `outcome` over 2-4 option orderings (or randomize per call) before reading `pick.choice`/`pick.confidence`, since `outcome === "blocked"` can veto the entire decision. **(confirm with data:** measure how often reordering the four options flips which one wins on borderline stops.) Source: [`cookbooks/consistency_choice_cookbook`](https://docs.typesafe.ai/cookbooks/consistency_choice_cookbook).
2. **F17 / loop not fully closed — retune on a fresh slice.** Draw a second, disjoint audit slice (a new random seed over stops not in the original 100) and re-sweep `DEFAULT_THRESHOLD` against it before trusting 0.70; report whether the held-out AUROC and the 2%-wrong-block budget still hold. Source: [`confidence`](https://docs.typesafe.ai/confidence); [`cookbooks/autoresearch_feature_discovery`](https://docs.typesafe.ai/cookbooks/autoresearch_feature_discovery).
