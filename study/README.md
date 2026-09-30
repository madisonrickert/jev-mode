# Jev Best Practices Study

A five-level course on building with Jev, TypeSafe's System One model. Each level summarizes TypeSafe's public cookbooks and docs, then you test yourself with multiple-choice quizzes on the concepts and on definitions of new glossary terms.

### [Open the Claude artifact](https://claude.ai/artifact/W1pVFeGkbcLzndA5xa1RE9)

**Recommended:** Claude reads each glossary definition you type and grades it on meaning, so a correct answer in your own words passes.

No Claude account? [The course on GitHub Pages](https://tiffygk.github.io/jev-mode/study/) has the same readings and quizzes, but its glossary uses a simple keyword check instead. It can fail a correct definition written in unusual words, and it hasn't been tested with learners. Each copy saves its own progress in your browser, so progress doesn't move between them.

## Who it's for

Developers about to write their first Jev questions, who want the patterns before the API reference.

Product and data people deciding where Jev fits, who want the vocabulary to follow an engineering conversation.

## Sample

> **Level 1: Writing Jev questions** (concept quiz)
> ### A support tool asks Jev one Choice per ticket, with three options: urgent billing, urgent other, and routine. Confidence is often low. What's the best change?
>
> - **Ask urgency and topic as two separate questions** ✓
> - Add an 'other' option so every ticket has a place
> - Raise the confidence bar on the two urgent options
> - Make it one Score that runs from routine to urgent
>
> **Why:** each option packs two judgments. Ask one property per question and let code combine the answers.
> Streak ●○ 1 of 2

## The levels

| Level | Topics | Concepts / terms |
|---|---|---|
| **1&nbsp;Writing&nbsp;Jev&nbsp;questions** | Noul, Choice and Score; state, criteria and thresholds. Start here. | 18 / 9 |
| **2&nbsp;Batching&nbsp;and&nbsp;cost** | Many questions in one call, fan-out, cascades, what a call costs | 7 / 5 |
| **3&nbsp;Classification&nbsp;and&nbsp;confidence** | Routing, category trees, repeat-run consistency, checking retrieved passages | 20 / 7 |
| **4&nbsp;Extraction&nbsp;and&nbsp;structure** | Dates, picked values, restored formatting, record matching, citation checks | 10 / 2 |
| **5&nbsp;Retrieval,&nbsp;ranking&nbsp;and&nbsp;guardrails** | Line search, reranking, skill suggestion, weighted scores, guardrails | 14 / 3 |

The whole course takes about 4.5 hours.

## How it works

1. Read the level's summary. Each recipe is taught with the source's own examples and links back to it.
2. Answer the concept quiz: short scenarios where you pick the right design or spot what's wrong, including the rubric checks for a well-built Jev project.
3. Learn the glossary. Each term appears in a sentence first; define it in your own words, then pick the sentence that uses it correctly.
4. Earn a star for each correct answer in a row. Two stars masters a concept or a term; a miss or a flag resets it to zero.
5. Check the report for your streak on every concept and term, and the ones you flagged.

Skip a question to see it later, or flag it when you don't know it and show the answer. You master a concept or term by getting it right twice in a row. Master every one in a level and its card turns gold on the start page.

## Where the rules come from

Each reading and concept cites the TypeSafe page it comes from: 18 cookbooks and 12 docs pages, all linked on the start page. General terms and the course's own labels are marked as such. The questions marked "Rubric" teach the checks [Jevaluate](../jevaluate/) uses to rate Jev projects; the sample above is the check that each question asks about one property, from TypeSafe's [How to build with System One](https://docs.typesafe.ai/concepts/how-to-build-with-system-one).

## Install and use

Nothing to install. Open either link above in a browser, on a laptop or a phone.

## Limits

The course summarizes TypeSafe's docs as of September 2026; check the linked source when a detail matters. The GitHub Pages keyword check can miss a correct definition written in unusual words and hasn't been tested with learners; use the Claude copy when you can. Progress lives in one browser: clearing site data or switching devices starts you over. Not affiliated with TypeSafe.

## License

PolyForm Noncommercial 1.0.0: free for personal and noncommercial use, with credit. Company or paid use needs a commercial license: [open an issue](https://github.com/tiffygk/jev-mode/issues).
