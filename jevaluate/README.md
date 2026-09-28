# Jevaluate

Jevaluate reads a Jev project's code and rates how well it uses Jev. Every finding carries its provenance: a file and line in the project, and the TypeSafe doc or cookbook behind the rule it checks.

It's built for projects that call Jev, TypeSafe's System One model. A project counts as calling Jev only when the rating can point to the line in its code that sends a request to Jev. Its name, its README or code that imitates Jev's API doesn't count. A project that doesn't call Jev gets a 1, labeled by whether it claims to.

Two Jev tools can look identical from the README. In the code, one asks atomic questions (one property each) and gates on confidence; the other just parses a prompt. Jevaluate separates them for you.

## Who it's for

- Developers adopting a Jev tool: know whether it gets the most out of Jev before you build on it.
- Enterprise teams: compare open-source Jev integrations on one scale. 
- Builders publishing their own: rate your project first and ship with the fixes in.

## What you get

> **valentynkit/jev-belay** at `ef719db`
> ### Verdict 4: Use it
> Execution ●●● · Fit ●●○ · Coverage ●●● · Evidence ●●○
>
> - One batched request, four atomic questions, pinned to `jev-1.13.0`
> - Thresholds live in code; a fresh passing check is a veto Jev can't override
> - Measured: AUROC 0.976 on 100 labeled stops
>
> **Top fix:** the threshold was tuned on the sample it reports on. Re-check it on a fresh slice.

Each dimension scores 0 to 3. The verdict comes from these rules, never an average:

| Verdict                                    | Definition                                             | Set by                                                                                                   |
| ------------------------------------------ | ------------------------------------------------------ | -------------------------------------------------------------------------------------------------------- |
| **5&nbsp;Learn&nbsp;from&nbsp;it**         | Reference-grade: follows the rules, measured on labels | Execution, Fit and Evidence all 3, and it retuned its thresholds or rewrote its questions based on those results                                                |
| **4&nbsp;Use&nbsp;it**                     | Correct use, minor gaps                                | Execution and Fit 2 or better, no failed core fact                                                       |
| **3&nbsp;Use&nbsp;with&nbsp;a&nbsp;fix**   | Right idea, fixable flaws                              | A failed core fact, or results claimed with no measurement. Unguarded user text counts only when the project acts on personal data, money or access with no review |
| **2&nbsp;Rework&nbsp;it**                  | Core rules broken; results likely unreliable           | Execution 1 or 0, or a fatal flaw: Jev computes values, or confidence is ignored on a high-stakes action |
| **1&nbsp;False&nbsp;marketing:&nbsp;Jev&nbsp;in&nbsp;name&nbsp;only** | Claims Jev, doesn't call it | No traced request to Jev, despite the claim |
| **1&nbsp;Not&nbsp;a&nbsp;Jev&nbsp;integration** | Never claims to call Jev, or its answers drive nothing | A Jev-like model, for example |
| **Can't&nbsp;rate&nbsp;yet**               | Too little visible to judge                            | README only, or the Jev code isn't public                                                                |

## How it works

1. Pins the commit, fetches every file that could change the verdict, and tells you what the rating will cost. Above 200k tokens it asks before going on.
2. Traces the request that proves the project calls Jev, names the project type (app, library, agent tool, demo and so on), then counts questions, thresholds and model pinning.
3. If the project remixes a TypeSafe cookbook, checks it against the original: what it kept, what it dropped.
4. Answers 24 facts, each yes, no or n.a., citing a file:line or quote. Each decision gets a stakes level, so a flaw costs more where a wrong answer moves money or personal data.
5. Scores four dimensions and sets the verdict. A checker script rejects any verdict the facts don't allow.
6. Traces each fix to the failed fact behind it and the TypeSafe page that shows the remedy, and flags fixes only your data can confirm.
7. Compares the verdict with similar ratings in your library, explains any difference, then logs it. Past ratings anchor new ones, so the scale holds as the library grows.

Blind re-rates keep the rules tight: fresh raters rate the same commit without seeing past ratings. In the latest round two matched on all four scores and 19 of 23 facts. The rules behind the other four are now tighter, and each round of use tightens them further.

## What it checks

First, F0: does the project call Jev at all? Then 23 facts in four groups:

- **Core principles:** one property per question, the right question type, structured input, batched requests, thresholds in code, measured on its own task.
- **Question design:** options that cover every case without overlap, an "unclear" option where one is needed, confidence deciding the action.
- **Execution:** a pinned model version, option order, size limits, user text kept out of question wording and tested for injection.
- **Evidence behind claims:** sample size, independent labels, a held-out test set, a fair baseline.

The full list, with the TypeSafe source behind each rule, is in [`rubric.md`](rubric.md).

## Every score shows its work

- **Rules from the source:** every rule and fix cites TypeSafe's docs or one of its 18 cookbooks, dated, in `jev-rules.md`. An unhandled Choice order, for example, gets its fix from TypeSafe's consistency cookbook.
- **Scores cite their facts:** each score names the rule it meets and the facts behind it.
- **Claims get checked:** Evidence earns full marks only with a stated sample, independent labels, a held-out set and a fair baseline.

## Install and use

Needs Claude Code, git and Python 3.8+. No API key.

```
git clone https://github.com/tiffygk/jev-mode
cp -r jev-mode/jevaluate ~/.claude/skills/
```

Then ask Claude Code: `jevaluate https://github.com/valentynkit/jev-belay`. Use a Sonnet-class model at medium effort every time, so ratings stay comparable. A rating reads every file that could change its verdict, so it isn't cheap: about 45k tokens plus the size of those files, typically 100-160k for a small repo. Ratings save to `~/.claude/jevaluate-library/` (or `$JEVALUATE_LIBRARY`), never into the skill.

## Published ratings

Ratings of community projects are in [`ratings/`](../ratings/), under CC0.

## Limits

Jevaluate reads public repos; it doesn't run them. Diagnose mode, which finds root causes in your own pipeline on your own data, isn't included yet. Not affiliated with TypeSafe.

## License

PolyForm Noncommercial 1.0.0: free for personal and noncommercial use, with credit. Company or paid use needs a commercial license: [open an issue](https://github.com/tiffygk/jev-mode/issues).
