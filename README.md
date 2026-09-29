# Jev Mode

Claude Code skills for building with Jev, TypeSafe's System One model. Not every skill calls Jev: some are guides and evaluators for building with it. The table says which, and each skill's README gives the details.

| Skill | What it does | Calls Jev | Status |
|---|---|---|---|
| [Jevaluate](jevaluate/) | Reads a Jev project's code and rates how well it uses Jev, with provenance for every finding | No: an evaluator that runs on the LLM alone | Available |
| [Jev Lens](jev-lens/) | Turns images into a neutral JSON state that Jev can read, one shared schema across the set | Only for an optional check of the finished state | Available |
| [Jevaluate Harness](jevaluate-harness/) | Runs rating rounds, re-rates and rubric calibration for Jevaluate | No | Available |

Install a skill by copying its folder into `~/.claude/skills/`:

```
git clone https://github.com/tiffygk/jev-mode
cp -r jev-mode/jevaluate ~/.claude/skills/
cp -r jev-mode/jev-lens ~/.claude/skills/
cp -r jev-mode/jevaluate-harness ~/.claude/skills/
```

The skills are written for Claude Code, but any coding harness that loads skills can run them with small changes.

Ratings of community Jev projects are in [`ratings/`](ratings/), released under CC0: use and change them freely.

Not affiliated with TypeSafe. The skills are licensed under [PolyForm Noncommercial 1.0.0](LICENSE.md): free for personal and noncommercial use, with credit. Company or paid use needs a commercial license: [open an issue](https://github.com/tiffygk/jev-mode/issues).
