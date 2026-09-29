# Jev project ratings

Jev, which TypeSafe launched on September 15, 2026, makes decisions instead of writing text. It answers typed questions with calibrated probabilities, and we're all still working out the frameworks for building with it. TypeSafe has documented a lot of what works. I downloaded and indexed all of its documentation, cookbooks and patterns, and I rate community projects against them.

## How projects are rated

These ratings follow TypeSafe's guidelines, not my taste. Every problem cites the code at a pinned commit and links the TypeSafe page it departs from, along with the fix that page recommends. A few rules come from my own testing; those are marked.

## If your project is here

The fixes are yours. Everything in this folder is released under CC0: use it, change it, ship it, no credit needed. The fixes come from reading your code and haven't been tested against it.

Open an issue if you disagree with a rating, if you've shipped improvements and want a re-rating, or if you'd like help fixing your project.

## Still learning

The rating skill is early, and it learns from this report: each new rating is checked against the ones here, and every disagreement sharpens the rubric. As I keep improving it, some ratings will be redone. If one reads as too harsh or too generous, I'm sorry. Tell me in an issue, and it will help the next version.

The goal is a Jev community that uplevels itself, sharing resources built on the best practices TypeSafe has already laid out.

## Ratings

| Project | Type | Verdict | Why | Rated |
|---|---|---|---|---|
| [Fox-Islam/jevlint](Fox-Islam__jevlint.md) | workflow | **4 Use it** | Atomic, batched checks gated in code, with evidence tested on material it didn't write. | 2026-09-27 † |
| [qkal/Canny](qkal__Canny.md) | workflow | **4 Use it** | Two well-chosen Jev decisions, batched and gated by thresholds in code; Jev stays advisory. | 2026-09-27 † |
| [valentynkit/jev-belay](valentynkit__jev-belay.md) | workflow | **4 Use it** | One Jev call, only for the judgment code can't make; a code veto Jev can't override. | 2026-09-27 † |
| [RileyCarney/JevTools](RileyCarney__JevTools.md) | demo | **3 Use with a fix** | Batched, typed and in code; one two-part question and overlapping topic options. | 2026-09-28 |
| [jkudish/jev-mcp](jkudish__jev-mcp.md) | agent tool | **3 Use with a fix** | Sound design, but claim and query text is spliced into question wording with no injection check. | 2026-09-28 † |
| [superagents-lab/jev-search](superagents-lab__jev-search.md) | workflow | **3 Use with a fix** | No fatal flaw; one Choice lacks "none of these" and one top answer skips a confidence check. | 2026-09-28 † |
| [jlowin/vibecheck](jlowin__vibecheck.md) | library | **2 Rework it** | Its examples use bare-number Score levels, and filter and group send one request per item. | 2026-09-28 † |
| [Jev-Omni](hf__akhilaaa3__Jev-Omni.md) | jev alternative | **1 Not a Jev integration** | An open classifier model that never calls Jev. | 2026-09-28 † |

† Rated under an earlier rubric; a re-rating is queued.
