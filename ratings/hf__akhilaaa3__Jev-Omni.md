[← All ratings](README.md)

*Rated under an earlier rubric (2026-09-28). A re-rating is queued.*

> **Jev-Omni** at [`5addda8`](https://huggingface.co/akhilaaa3/Jev-Omni/tree/5addda86ddee081a68fb067477ea100c221b8917) · jev alternative
> ### Verdict 1: Not a Jev integration
> Execution ○○○ · Fit ○○○ · Coverage ●●○ · Evidence ●●○
>
> - Jev-Omni is an open Gemma-4-12B-it fine-tune with a 256-slot linear classifier head that returns a probability per user-supplied option, for text, image, audio and video.
> - It never calls TypeSafe's Jev: no `api.typesafe.ai` call, no SDK, no `jev-X.Y.Z` model ID anywhere in the files (only the name and a disclaimer).
> - Under the rubric, Jev not called gives verdict 1, Not a Jev integration.
>
> **Top fix:** Call Jev and pin a versioned ID (F12; [`models`](https://docs.typesafe.ai/models)), with one request carrying many Nouls, Choices and Scores over a JSON state (F3, F4; [`patterns/fan-out`](https://docs.typesafe.ai/patterns/fan-out)).

## What holds it back

- **Confidence drives action** (F11): [`confidence`](https://docs.typesafe.ai/confidence) is returned ([`jev_omni.py:108`](https://huggingface.co/akhilaaa3/Jev-Omni/blob/5addda86ddee081a68fb067477ea100c221b8917/jev_omni.py#L108)) but nothing in the repo acts on it; no routing or threshold code.
- **Held-out result** (F17): The card publishes only a `test` split ("split: test", `data/medium.jsonl`) but never says it is disjoint from the 24,000 training questions ([`decision_config.json:15`](https://huggingface.co/akhilaaa3/Jev-Omni/blob/5addda86ddee081a68fb067477ea100c221b8917/decision_config.json#L15)), or whether training questions came from the same Claude Opus 5 generation. [`decision_config.json:29-30`](https://huggingface.co/akhilaaa3/Jev-Omni/blob/5addda86ddee081a68fb067477ea100c221b8917/decision_config.json#L29-L30) has train and dev fingerprints; no test fingerprint or overlap check is given. Docs: https://docs.typesafe.ai/cookbooks/classification_using_confidence.md

## Fixes (from reading the code; not tested against it)

1. Call Jev and pin a versioned ID (F12; [`models`](https://docs.typesafe.ai/models)), with one request carrying many Nouls, Choices and Scores over a JSON state (F3, F4; [`patterns/fan-out`](https://docs.typesafe.ai/patterns/fan-out)).
2. Gate on confidence in code (F5, F11; [`confidence`](https://docs.typesafe.ai/confidence), [`patterns/confidence-routing`](https://docs.typesafe.ai/patterns/confidence-routing)).
3. Evidence (F17): state that the test split is disjoint from training and add a human audit of a slice of the key; report Wilson intervals with bin counts for ECE. This is diagnosis work and needs data.

[Full rating: every fact, its evidence and the files read →](full/hf__akhilaaa3__Jev-Omni.md)

