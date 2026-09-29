# Jevaluate Harness

Runs [Jevaluate](../jevaluate/) over many projects at once, tests a rubric change before it ships, and publishes the ratings.

Jevaluate rates one project on its own. This skill is the harness around it: it never judges a project or edits a rating. Without it, parallel raters collide on the shared library, a rubric change leaves every older rating stale, and nothing shows whether the change made ratings better or worse.

## Who it's for

Jevaluate users who:

- Rate a whole list of projects in one round.
- Fork Jevaluate and change its rubric.
- Publish a ratings folder.

It doesn't work without Jevaluate: every step runs Jevaluate's scripts, rubric or eval.

For a different LLM rating skill, this one won't run, but its pattern carries over: fixed test cases, one logger, a blind second opinion.

## How it works

1. Screen a list of repos against two known controls.
2. Size every repo before rating it; above about 150k tokens, agree which files to read.
3. Give every rater the same brief: its own folder, facts before the old rating.
4. Log ratings into the shared library one at a time, by one controller.
5. Send any verdict move of 2 or more points to a reviewer that sees only the facts.
6. Run the judgment eval before and after any rubric change (the eval ships in the next update); log each round in `jevaluate/CALIBRATION.md`.
7. Export a preview, check every page for private context, then push once.

## Install and use

Needs Claude Code, Python 3.8+, the GitHub CLI (`gh`, logged in) and Jevaluate itself.

```
git clone https://github.com/tiffygk/jev-mode
cp -r jev-mode/jevaluate jev-mode/jevaluate-harness ~/.claude/skills/
```

Set `$PRIVATE_TERMS` to your file of never-publish regexes (see the skill's Settings). Then ask Claude Code: `run a jevaluate re-rate round`.

## Limits

Like Jevaluate, it runs entirely on an LLM and never calls Jev, so it needs no TypeSafe API key. It rates nothing itself: each rating is a full Jevaluate run, about 45k tokens plus the files read. Not affiliated with TypeSafe.

## License

PolyForm Noncommercial 1.0.0: free for personal and noncommercial use, with credit. Company or paid use needs a commercial license: [open an issue](https://github.com/tiffygk/jev-mode/issues).
