---
name: jevaluate-maintain
description: Use when running a jevaluate rating round, re-rating projects after a rubric change, calibrating or changing the jevaluate rubric, running its judgment eval, or publishing ratings to the jev-mode ratings folder.
---

# Jevaluate: maintaining the ratings

Companion to `jevaluate`, which rates one project. This skill runs rounds of ratings and keeps the rubric honest. Read `jevaluate/read.md` for how a single rating is made; this file never repeats it.

## Settings (yours, not in this skill)
`$PRIVATE_TERMS`: a file of regexes, one per line, for lines that must never be published. `library.py export` refuses a match, but it reads only `$JEVALUATE_LIBRARY/private-terms.txt`, so point `$PRIVATE_TERMS` at that file. A pre-push hook of your own should read `$PRIVATE_TERMS` too; jev-mode doesn't ship one. Your budget levels and push cadence live in your own instructions.

## 1. Pick and screen
Screen a list with `python3 jevaluate/scripts/screen_list.py <list README> --known-yes <repo that calls Jev> --known-no <repo that doesn't>`; it refuses to run until both controls classify correctly. Quote counts from its output, never by eye. Never classify repos with GitHub code search.

## 2. Size before spending
Run `python3 jevaluate/scripts/coverage_manifest.py <owner/repo> <dir>` for every project first; the manifest's first line gives `~N tokens`. A rating costs about 45k plus N. Above 150k, a full read won't fit one pass: agree a scoped rating (the files with the Jev calls, questions and decisions) before dispatch, since an unattended rater has no one to ask.

## 3. Brief raters
Use `rater-brief.md`. Raters work only in their own folder, write facts before reading the old rating, and never run `library.py add`, commit or push.

## 4. Log one at a time
Only the controller runs `python3 jevaluate/scripts/library.py add <rating> --evidence <dir> --link-docs`, one rating at a time: `add` rebuilds the shared index and numbers same-day files. A refused rating goes back to its rater; never fix it by hand. Keep a ledger: project, verdict, tokens, flags.

## 5. Adjudicate
Send any move of 2 or more verdict points, and any rubric line a rater called ambiguous, to a `reviewer` that reads only the facts. Answer "what would X get?" from the facts or such a re-verdict, never from memory.

## 6. Calibrate
- Before and after any rubric change, run the judgment eval (`jevaluate/evals/`, see its README). Tune only on tuning-set failures; held-out cases are never tuned on.
- Where raters disagree on a fact across re-rates, tighten that fact's anchor, then re-run the eval.
- Test wording with headless calls: `claude -p --setting-sources "" --strict-mcp-config --tools "" --system-prompt-file <f> --model <m> --effort <e> --output-format json < prompt.md` (`--bare` fails on OAuth logins). These calls don't show in agent token logs; add their `usage` to your spend.
- Before building a cheaper rating mode, measure it on one real repo. A quick mode measured at 78k tokens left 10 of 24 facts unknown and was dropped.
- Record each round's findings in `jevaluate/CALIBRATION.md`.

## 7. Publish
1. Give every rating a `why:` line (20 words at most).
2. `library.py export <preview dir>`; render it and read the index, a detail page and a full page.
3. Have a reviewer read every page for private context: anything crediting a private conversation, names used without consent.
4. Re-check the README's claims against the skill's current files.
5. Export into `ratings/`, run a GitHub readiness audit, push once.

Only full or agreed-scoped ratings under the current rubric are published; evidence folders never are.
