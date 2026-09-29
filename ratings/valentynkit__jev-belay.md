[← All ratings](README.md)

*Rated under an earlier rubric (unrecorded). A re-rating is queued.*

> **valentynkit/jev-belay** at [`ef719db`](https://github.com/valentynkit/jev-belay/tree/ef719db7eaadc56aa4def86c4da4ffff5bcbca35) · workflow
> ### Verdict 4: Use it
> Execution ●●● · Fit ●●○ · Coverage ●●● · Evidence ●●○
>
> - jev-belay is a Claude Code `Stop` hook that refuses to let a turn end on an unverified "done."
> - Two free, local regex belts read the transcript for whether a runner was named or a runner's own summary appears in the output; only when files changed and nothing fresh passed does it spend one Jev call (`jev-1.13.0`, four batched questions: three Nouls — `claims_done`, `claims_verified`, `verification_applies` — and one Choice, `outcome`) to judge whether the closing message is a false claim of completion.
> - A hard code-side veto (a fresh passing check) can never be overridden by Jev's answer.
>
> **Top fix:** Average `outcome` over 2-4 option orderings (or randomize per call) before reading `pick.choice`/`pick.confidence`, since `outcome === "blocked"` can veto the entire decision.

## What holds it back

- **Choice order handled** (F13): `outcome` is high-stakes (a `blocked` pick vetoes the whole decision, [`belay.mjs:568`](https://github.com/valentynkit/jev-belay/blob/ef719db7eaadc56aa4def86c4da4ffff5bcbca35/belay.mjs#L568)) but nothing in `belay.mjs`, `tui.mjs`, or `tools/measure.mjs` averages it over option orders or randomizes the order per item. `OUTCOME_FLOOR` gates on confidence, which is a different mitigation than order-stability.
- **Held-out set, or data not used for tuning** (F17): CHANGELOG 0.2.0: "the `claims_done` threshold is 0.70... on the re-extracted corpus... 0.70 is the lowest cutoff holding wrong blocks under 2%... [same measurement] same 100-stop audit slice with 12 false dones... AUROC 0.976." The operating threshold was swept and the headline metric was reported on the identical audit slice, not a held-out split.

## Fixes (from reading the code; not tested against it)

1. **F13 — Choice order unhandled on a high-stakes pick.** Average `outcome` over 2-4 option orderings (or randomize per call) before reading `pick.choice`/`pick.confidence`, since `outcome === "blocked"` can veto the entire decision. **(confirm with data:** measure how often reordering the four options flips which one wins on borderline stops.) Source: [`cookbooks/consistency_choice_cookbook`](https://docs.typesafe.ai/cookbooks/consistency_choice_cookbook).
2. **F17 / loop not fully closed — retune on a fresh slice.** Draw a second, disjoint audit slice (a new random seed over stops not in the original 100) and re-sweep `DEFAULT_THRESHOLD` against it before trusting 0.70; report whether the held-out AUROC and the 2%-wrong-block budget still hold. Source: [`confidence`](https://docs.typesafe.ai/confidence); [`cookbooks/autoresearch_feature_discovery`](https://docs.typesafe.ai/cookbooks/autoresearch_feature_discovery).

[Full rating: every fact, its evidence and the files read →](full/valentynkit__jev-belay.md)

