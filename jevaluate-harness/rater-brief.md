This is your only task. Return your report as text; never push, commit, or run `library.py add`.

Rate PROJECT with the jevaluate skill: read ~/.claude/skills/jevaluate/SKILL.md, then read.md, rubric.md (2026-09-28b), fix-catalog.md, jev-rules.md, and follow read.md. Work only in ~/jevaluate-round2/SLUG/ (its manifest.md is already there).
- Depth: SCOPE. "full" means every manifest file that could change a fact, read in full. "scoped: <files>" means only those files, with `depth: extract` and every other file `skipped: scoped` in Coverage.
- Front matter: rater: claude-sonnet-5-5, effort: medium, via: VIA, rubric: 2026-09-28b, and a `why:` line of 20 words at most.
- Write all facts before opening the previous rating PREV; then use it only for the "Compared with" sentence.
- Nothing said privately goes in the rating.
- Save the rating as ~/jevaluate-round2/SLUG/rating.md and run `python3 ~/.claude/skills/jevaluate/scripts/library.py check ~/jevaluate-round2/SLUG/rating.md --evidence ~/jevaluate-round2/SLUG` until it passes.
Report: verdict and label, project_type, F0 line, stakes per decision, facts that changed from PREV, tokens you think you used, and any rubric line you found ambiguous (quote it).
