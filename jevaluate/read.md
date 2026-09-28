# Jevaluate: read mode

Rate one project. Work through the phases in order; each phase's output goes into the rating file. Keep reads capped: never load a whole repo or long page into context.

## 1. Intake
Record: project name, URL, **owner** (the GitHub owner, or the publisher of a post), today's date, and the **commit or version rated** (`git ls-remote <url> HEAD`, or the post's date). A rating without a commit can't be compared later.

Then record the **project type** (`rubric.md`, "Before the facts"): exactly one of `app`, `library`, `plumbing`, `agent-tool`, `demo`, `jev-like-model`. Decide it from what the code does, not from what the README calls it.

## 2. Read
- `python3 scripts/coverage_manifest.py <owner/repo> <tmpdir>` writes `manifest.md` (every file that could hold Jev calls, decisions or evaluation), `meta.json` and the files themselves in `files/`. Read every file in the manifest that could change a fact or the verdict, and list each one in the rating's `## Coverage` section as `read` or `skipped: <reason>` (a binary, a lockfile, a generated file). `library.py check` refuses a rating whose Coverage leaves out a manifest file. Copy the manifest into the evidence folder with `library.py add --evidence <tmpdir>`.
- **Estimate the cost before reading.** The manifest's first line gives the kept files' size (`~N tokens`). A rating costs about 45k tokens plus N (measured 2026-09-28 on two repos; an estimate). Tell the user the figure. Above 200k, stop and ask before reading. If N is over 150k, a full read won't fit in one pass: say so, and offer a rating scoped to the files that hold the Jev calls, questions and decisions, recorded as `depth: extract` with every other file `skipped: scoped` in Coverage. Only full ratings are published.
- For a quick first look before the manifest, `python3 scripts/fetch_repo.py <owner/repo> --out <tmpdir> --files 4 --cap 4000` (the defaults) writes `meta.json` (owner, stars, dates, license, commit), `extract.md` (the file list, the README, and matching lines from the 4 files most likely to hold Jev calls, capped at 4,000 characters each), and the full text of those files in `files/`.
- Read the file list first. If Jev code sits in files the extract didn't pick (a JSON check catalogue, a second source file), rerun with `--also <path>,<path>`; don't fetch whole files into context. Files that hold the decision logic (thresholds, routing, confidence) count even when the extract shows 0 Jev keywords for them.
- For a post, a docs page or a product without code, read the page itself (capped).
- To screen a whole curated list before choosing what to rate, use `python3 scripts/screen_list.py <list README> --known-yes <owner/repo> --known-no <owner/repo>`: it classifies each repo by grepping its raw files, never GitHub code search.
- **Record the depth read:** `full` (every manifest file read in full, none skipped for length), `extract` (capped extracts, or any file read selectively), or `readme-only`. A Coverage line that says skimmed, selective or partial means the depth isn't `full`; `check` refuses the mismatch. Readme-only ratings are usually "Can't rate yet."

## 3. Stats
`python3 scripts/jev_callsites.py <tmpdir>/files` reports `mentions` and `hosted_calls`. Only `hosted_calls` counts as Jev being called; `mentions` includes docs, tests, fixtures and code that imitates Jev's API. It counts these (or run it on a local clone). **Never run it on `extract.md`:** the extract keeps only matching lines, so calls that span lines get miscounted. Check its output against what you read:
- `hosted_calls`, and **requests per item** (one batched request, or several in a row)
- **Atomic questions**: the total, and the average per request
- Question types: Nouls, Choices, Scores; options per Choice
- Whether confidence or probabilities drive an action
- Thresholds: how many, and whether they live in code or prose
- Model: pinned to a version (`jev-1.13.0`) or an alias (`jev-latest`, or none)
- Approximate state size

Then record **F0** (`rubric.md`): the one `file:line` that traces a hosted call, or the capture that does for a hosted site. If `hosted_calls` is 0, check for a call the script can't see (a wrapper, an MCP tool, a server behind the site's own `/api`) before recording no. F0 no means verdict 1, labeled "False marketing: Jev in name only" when the project claims to use Jev, and "Not a Jev integration" when it doesn't.

## 4. Lineage
Classify the project as one of:
- **Remix of a TypeSafe cookbook or pattern.** Find it in `https://docs.typesafe.ai/llms.txt` (sections Cookbooks and Patterns), fetch it as `.md`, and read the parts the project uses. Condense MDX pages to prose before reading.
- **Remix of another project** (a fork, a port, or an adaptation). Fetch the upstream the same way as in phase 2.
- **New.**

For a remix, list the original's decisions or steps, and mark which the project keeps, changes or drops. That list is its **coverage**.

## 5. Facts
Answer every fact in `rubric.md` that the project type leaves in play as **yes / no / not applicable**, with evidence: a `file:line` or a short quote. No evidence means "no," or "unknown" if the file wasn't read. Before recording unknown, rerun `fetch_repo.py --also` on the file that would answer it; unknown stands only if that fetch fails or no file would answer it, and the fact's line must say which (`--also <path>`, `fetch failed` or `no file would answer it`); `library.py check` refuses it otherwise. Unknowns lower the depth, not the score. Give each Jev decision its stakes (`very high`, `high` or `low`) before answering F11, F13, F20 and F22. A README's claim about the project is a claim, never a fact's evidence.

## 6. Scores and stages
- Score each dimension 0 to 3 using the anchors in `rubric.md`. Each score names its anchor and cites the facts behind it.
- Mark the **build stages** it covers, and whether it **closes the loop** (evaluates on labels, then calibrates the numbers and/or revises the questions or state).

## 7. Compare with the library
`python3 scripts/library.py similar --lineage <x> --stage <y> --exclude <owner/repo>` returns past ratings with the same lineage or stage, leaving out this project's own past ratings. Ratings marked `old rubric` were made before the current rubric (`library.py stale` lists them): read them for context, never as precedent. For a blind re-rate (a consistency test), whoever dispatches the rater runs `library.py blind --exclude <owner/repo> --out <dir>` and sets `JEVALUATE_LIBRARY=<dir>` for it; the rater's `add` lands in that copy, and the dispatcher adds it to the real library after comparing. Read up to three. If your verdict differs from a similar project's, add one sentence on why. Name only the projects you compared; don't restate scores a rating quotes for a third project. That sentence is how the library keeps ratings consistent.

## 8. Verdict and fixes
- Choose the verdict from the anchors in `rubric.md`. One fatal flaw caps the verdict, whatever the other scores are. The current anchors decide; a past rating that reads them differently is not precedent.
- For a verdict of 3 or below, list the **core fixes**: each is an entry from `fix-catalog.md`, citing the failed fact it answers and the TypeSafe page it links (`library.py add --link-docs` fills a missing link from the catalog). Put the most important fix first.
- When a fix can only be confirmed with data (is this question actually producing wrong answers?), say so. That's diagnosis work, not a design fix.
- Offer to draft the fixed version (for example, rewritten questions). Don't draft it unless asked.

## 9. Log
`python3 scripts/library.py add <rating.md> --evidence <tmpdir> --link-docs` first runs `library.py check`, which refuses a rating with a missing fact, an unknown with no `--also` fetch noted, no `rubric:` date, a verdict above what the facts allow, a missing `project_type`, `rater`, `effort` or `via`, a Coverage section that leaves out a manifest file, depth `full` with a skipped or partial read, or a failed fact with no TypeSafe page linked. A revision of a same-day rating uses `--supersedes <old file>`. Anything said privately (a call, a message) never goes in a rating: it is published by `library.py export`, which refuses lines matching the library's `private-terms.txt`. Fix what it lists and rerun. It then saves the rating as `projects/<slug>/YYYY-MM-DD.md` (a second same-day rating is `YYYY-MM-DD-2.md`, and so on) and rebuilds `index.md`. The slug comes from the frontmatter `url`: a GitHub project keeps its owner and repo case (`owner__repo`); a Hugging Face model is `hf__user__model`; anything else is `site__domain`. Use this template:

```markdown
---
project: <name>
url: <url>
owner: <github owner>
rated: YYYY-MM-DD
rubric: 2026-09-28b   # the version in rubric.md's Verdict anchors heading
project_type: app | library | plumbing | agent-tool | demo | jev-like-model
rater: <model id>   # e.g. claude-sonnet-5-5
effort: medium | high
commit: <sha or version>
depth: full | extract | readme-only
lineage: cookbook:<slug> | project:<owner/repo> | new
stages: [data-prep, question-state, execution, decision]   # only these four labels, exactly as written
closes_loop: none | calibrates | revises | both
verdict: 5 | 4 | 3 | 2 | 1 | cant-rate   # cant-rate = "Can't rate yet"
why: <at most 20 words: the one reason for this verdict, for the public index>
scores: {execution: n, fit: n, coverage: n, evidence: n}
via: direct | list:<name>   # direct = someone named it; list:<name> = it came off a curated list
---
## Summary
Three sentences: what it does with Jev; what it does well; what holds it back.
## Stats
## Facts (with evidence)
- F0 Calls hosted Jev — yes. <what the call is, in at most 20 words> (`file:line`)
- F1 <name> — no. <the finding, in at most 20 words> (`file:line`). <TypeSafe page>
# One line per fact, F0-F23: the value, one finding of at most 20 words, then the file:line.
# A no ends with its TypeSafe page. Anything that needs more words goes in Verdict and reasoning.
## Scores
- <Dimension> <n> of 3: <what that score means for this project, in plain words>, <the facts behind it, by name>.   # the anchor's meaning, never a quote of it
## Compared with
## Verdict and reasoning
At most five sentences: why this verdict and not the one above it, and any borderline call.
## Core fixes
## Coverage
- <path> — read | skipped: <reason>   # one line per manifest file
```

Report the rating to the user: the verdict, the stats line, the top fixes, and the path to the saved file.
