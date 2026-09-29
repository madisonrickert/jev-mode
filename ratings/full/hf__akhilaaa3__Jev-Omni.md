[← Summary](../hf__akhilaaa3__Jev-Omni.md)

# Jev-Omni: full rating

**Verdict 1, Not a Jev integration** · jev alternative · rated 2026-09-28 at [`5addda8`](https://huggingface.co/akhilaaa3/Jev-Omni/tree/5addda86ddee081a68fb067477ea100c221b8917) · read: full · rubric 2026-09-28 (earlier) · claude-sonnet-5-5, medium effort

*Rated under an earlier rubric (2026-09-28). A re-rating is queued.*

## Summary

Jev-Omni is an open Gemma-4-12B-it fine-tune with a 256-slot linear classifier head that returns a probability per user-supplied option, for text, image, audio and video. It never calls TypeSafe's Jev: no `api.typesafe.ai` call, no SDK, no `jev-X.Y.Z` model ID anywhere in the files (only the name and a disclaimer). Under the rubric, Jev not called gives verdict 1, Not a Jev integration. It is a separate model that imitates the shape of Jev's interface, and that is the honest reading of the project: a competitor or alternative to Jev, not a use of it.

## What fails

| Fact | Finding |
|---|---|
| Confidence drives action (F11) | **no.** [`confidence`](https://docs.typesafe.ai/confidence) is returned ([`jev_omni.py:108`](https://huggingface.co/akhilaaa3/Jev-Omni/blob/5addda86ddee081a68fb067477ea100c221b8917/jev_omni.py#L108)) but nothing in the repo acts on it; no routing or threshold code. |
| Held-out result (F17) | **no.** The card publishes only a `test` split ("split: test", `data/medium.jsonl`) but never says it is disjoint from the 24,000 training questions ([`decision_config.json:15`](https://huggingface.co/akhilaaa3/Jev-Omni/blob/5addda86ddee081a68fb067477ea100c221b8917/decision_config.json#L15)), or whether training questions came from the same Claude Opus 5 generation. [`decision_config.json:29-30`](https://huggingface.co/akhilaaa3/Jev-Omni/blob/5addda86ddee081a68fb067477ea100c221b8917/decision_config.json#L29-L30) has train and dev fingerprints; no test fingerprint or overlap check is given. Docs: https://docs.typesafe.ai/cookbooks/classification_using_confidence.md |

<details>
<summary><b>What passes (4) and doesn't apply (17)</b></summary>

| Fact | Finding |
|---|---|
| Atomic questions (F1) | n.a.. No Jev calls; the model takes one question per call ([`jev_omni.py:68`](https://huggingface.co/akhilaaa3/Jev-Omni/blob/5addda86ddee081a68fb067477ea100c221b8917/jev_omni.py#L68)). |
| The right primitive (F2) | n.a.. No Jev calls; the tool has one primitive, a numbered option list ([`jev_omni.py:31`](https://huggingface.co/akhilaaa3/Jev-Omni/blob/5addda86ddee081a68fb067477ea100c221b8917/jev_omni.py#L31)). |
| Structured state (F3) | n.a.. No Jev calls. Its own state is a plain string ([`jev_omni.py:32`](https://huggingface.co/akhilaaa3/Jev-Omni/blob/5addda86ddee081a68fb067477ea100c221b8917/jev_omni.py#L32), `{state}`). |
| Batching (F4) | n.a.. No Jev calls; README: "a classifier answers one question at a time... no discount for asking several at once". |
| Thresholds in code (F5) | n.a.. No decision code; `predict` only returns probabilities ([`jev_omni.py:107-108`](https://huggingface.co/akhilaaa3/Jev-Omni/blob/5addda86ddee081a68fb067477ea100c221b8917/jev_omni.py#L107-L108)). |
| No invented values (F6) | n.a.. No Jev calls. |
| Measured in the workflow (F7) | yes. README Results table: DecisionBench Medium "80 scenarios / 293 questions", 87.57% accuracy, plus JevBench, MMAU, MVBench; ECE 0.0400. |
| Options cover every case (F8) | n.a.. No Jev Choices; options are user-supplied. |
| "Unclear" or "other" option (F9) | n.a.. No Jev Choices. |
| Evidence recorded evenly (F10) | n.a.. No per-answer evidence state. |
| Model pinned (F12) | n.a.. Jev is not used; the checkpoint is pinned by HF commit 5addda86dd. |
| Choice order handled (F13) | n.a.. No Jev Choices (note: the tool's own prompt numbers options in the given order, [`jev_omni.py:31`](https://huggingface.co/akhilaaa3/Jev-Omni/blob/5addda86ddee081a68fb067477ea100c221b8917/jev_omni.py#L31), with no order averaging). |
| Size limits respected (F14) | n.a.. Jev is not used (no guard in `predict`; audio capped at 30 s, [`jev_omni.py:88`](https://huggingface.co/akhilaaa3/Jev-Omni/blob/5addda86ddee081a68fb067477ea100c221b8917/jev_omni.py#L88)). |
| Sample size stated and adequate (F15) | yes. 293 questions in 80 scenarios (README); adequate for the headline rate of about 87%, with the interval not reported. |
| Labels independent of builder (F16) | yes. (disclosed, weak). `files/decision-bench__README.md`, "How it was built": "Synthetic scenarios, questions and answers were generated with Claude Opus 5 across multiple domains." Tags include `synthetic`. The key is one LLM's output, not a panel or blind human labels, with no human audit or agreement figure stated; the disclosure is what satisfies the fact. |
| Fair baseline (F18) | yes. The accuracy chart puts Jev 1.13, Gemini 3.8 Flash, GPT-5.6 Luna and Claude Sonnet 5 on the same set; the README flags the pricing basis differs per shape. |
| Typed answers read directly (F19) | n.a.. No Jev calls; its own output is a typed probability dict ([`jev_omni.py:107`](https://huggingface.co/akhilaaa3/Jev-Omni/blob/5addda86ddee081a68fb067477ea100c221b8917/jev_omni.py#L107)). |
| Values from code are fields (F20) | n.a.. No Jev calls. (Its own prompt splices state and question into one string, [`jev_omni.py:32`](https://huggingface.co/akhilaaa3/Jev-Omni/blob/5addda86ddee081a68fb067477ea100c221b8917/jev_omni.py#L32), which is how a Gemma prompt works, not a Jev request.) |
| No instructions in the state (F21) | n.a.. No Jev calls. |
| Untrusted text treated as data (F22) | n.a.. No Jev calls. |
| Non-English content handled (F23) | n.a.. No Jev calls; the README does not mention language. |

</details>

## Scores

- Execution 0: "Jev is used like an LLM prompt... or not called". Not called.
- Fit 0: "Jev isn't needed... or its output isn't used". There is no Jev output.
- Coverage 2: own stated goal (README: "noul (yes/no), choice and score questions answered with calibrated probabilities"). The code covers Noul as a two-option Choice and Choice, returns probabilities, and reports ECE. It has no Score type and no parallel questions. Two of three question types: 50 to 79%.
- Evidence 2: "Measured with one weakness... disclosed". The dataset card gives the method (synthetic, generated by Claude Opus 5; 80 scenarios / 293 questions; accuracy and ECE definitions). The weakness is disclosure-poor: one-LLM answer key with no human audit, and disjointness from training never stated (F17 no).
- Stages: none. There is no data-prep, question design, execution or decision code around Jev. Loop: none.

## Why this verdict

Verdict 1, Not a Jev integration. The rubric says "Jev isn't called, or its output doesn't drive any decision", and no file references TypeSafe's API or a Jev model ID. That is not a quality judgment on the model: it is a real open classifier with a stated recipe and reported numbers. Its accuracy claim is weakly evidenced (builder-owned synthetic benchmark (one Claude Opus 5 key), disjointness from training unstated, no intervals), and by its own chart it is below Jev 1.13 and the three frontier LLMs on that benchmark. Anyone using it should treat it as a separate model to evaluate, not as a route to Jev's behavior.

## Fixes (from reading the code; not tested against it)

1. Call Jev and pin a versioned ID (F12; [`models`](https://docs.typesafe.ai/models)), with one request carrying many Nouls, Choices and Scores over a JSON state (F3, F4; [`patterns/fan-out`](https://docs.typesafe.ai/patterns/fan-out)).
2. Gate on confidence in code (F5, F11; [`confidence`](https://docs.typesafe.ai/confidence), [`patterns/confidence-routing`](https://docs.typesafe.ai/patterns/confidence-routing)).
3. Evidence (F17): state that the test split is disjoint from training and add a human audit of a slice of the key; report Wilson intervals with bin counts for ECE. This is diagnosis work and needs data.

<details>
<summary><b>Files read (12)</b></summary>

Read (12 files, 0 skipped):
- `README.md`: read. Model card, results, limits, calibration, disclaimer.
- `files/jev_omni.py`: read in full. The only inference and head code.
- `files/example.py`: read in full.
- `files/decision_config.json`: read in full. Training recipe.
- `files/verification.json`: read in full.
- `files/requirements.txt`: read.
- `files/generation_config.json`: read. Stock Gemma sampling config, unused by the classifier path (`use_cache=False`, one forward pass).
- `files/sha256.json`: read. Hash list only, no rating content.
- `files/assets__medium-accuracy.svg` and `files/assets__medium-calibration.svg`: read as text. Accuracy plotted values read (87.57, 90.48, 99.12, 98.76, 99.12). The calibration SVG has axes and legend only in text; no per-bin numbers are recoverable from the text, so the calibration curve's shape is unread.
- `files/decision-bench__README.md`: read in full. DecisionBench dataset card: synthetic origin, split, per-model tables, scoring definitions, request-shape correction. It answers F16 and F17 as recorded above; it does not state train-test disjointness.
- `api.json`: read for commit sha 5addda86dd, `base_model` google/gemma-4-12B-it and tags (`text-classification`, `multimodal`, `merged`).
- Not in the manifest and not fetched: weights (`model.safetensors`, `head.pt`, binary), the dataset's `DATASET_INFO.md` and JSONL data (might state overlap with training), `config.json` and the tokenizer files. Nothing in them would change the verdict.

</details>
