# Evidence for prompt/tool iterations

Scope: system_prompt.md, tools.yaml, version_log.csv, snapshots and live base evaluation evidence. Original eval cases, tool implementations, .env and .env.example were not edited by this work.

Provider: OpenRouter / openai/gpt-4o-mini, temperature=0. Each version ran once against all 20 original cases. Single runs cannot establish statistical significance.

| Version | Case accuracy | Routing | Arguments | Multi-turn |
|---|---:|---:|---:|---:|
| v0 | 65% | 75% | 65% | 100% |
| v1 | 90% | 100% | 90% | 100% |
| v2 | 75% | 95% | 75% | 83% |
| v3 | 95% | 100% | 95% | 100% |

## Hypotheses and outcomes

- v0 baseline: 7 failures. Incorrect news arguments (R03/R13); unnecessary tools for out-of-scope math/code (R08/R14); guessed missing account/URL (R10/R11); attempted send without confirmation (R12). See version_failures.csv for actual calls and observed errors. The evaluator labels some argument errors as wrong_tool based on case categories; use observed_mismatch for diagnosis.
- v1: replace the starter's guessing, immediate-send and single-step behavior with explicit boundaries. 13/20 -> 18/20. Missing account and out-of-scope behavior improved; remaining failures concern clarify argument values.
- v2: add explicit source routing, argument conventions and conversation constraints. 18/20 -> 15/20: the hypothesis did not improve this run. Queries acquired extra news words and one case retrieved Twitter after the user switched to web only. This is a regression, not a successful optimization.
- v3: align all tool descriptions with the prompt and parameter conventions. 15/20 -> 19/20; routing 20/20, multi-turn 6/6. Hypothesis supported in this run; independent repeats/group evaluation are still needed for generalization.

## Remaining case

R12 expects clarify(response_type=yes_no) for a Telegram publishing request. The request contains no actual bulletin text. v3 instead calls clarify(response_type=text) to request that content. No send is executed. This fails the fixed rubric while maintaining the no-unconfirmed-send boundary. A follow-up hypothesis could separate collecting missing content from confirming the exact draft; do not mark this case as passed or claim an unauthorized send occurred.

## Verification and limits

- Preflight returned a structured timeline tool call using the live model.
- Final pytest: 62 passed, 17 skipped (existing student TODO tests); no failing tests. This does not satisfy the separate zero-skipped challenge.
- Tavily, Firecrawl and RapidAPI keys are absent. The evaluator scores tool names and arguments independently of execution errors, so these percentages are routing results, not successful end-to-end retrieval. Raw execution errors are preserved in runs/*.json.
- v0-v2 snapshots reproduce the original runs. v3 was later revised in place at user request: use the prompt hash to distinguish original v3 runs from the revised snapshot. Original v3 bytes remain in Git commit 4fcdb00.
- New tool/unit tests, 10 group cases, UI/public link, live 3-turn transcript and REPORT/poster are separate deliverables not completed in this scope.


## Applied to v3 in place (2026-11-10)

At the user's request, the proposed scope guard was applied to both `artifacts/system_prompt.md` and `artifacts/versions/v3/system_prompt.md`, keeping the version label **v3**. No new prompt version was created. The proposal file above remains historical source material. Tools, base cases and grader are unchanged.

- New prompt SHA-256: `7958c88fd530` (prefix); tools hash unchanged: `a5d67e285198`.
- `runs/v01_B_base_openrouter.json`: all 20 requests failed with HTTP 402 because the provider default reserved 65536 output tokens. Zero measured cases; this is not 0% model accuracy.
- `runs/v02_B_base_openrouter.json`: live Gemini `google/gemini-3.5-flash-lite`, 20 measured, 0 provider errors, **19/20 (95%)**, routing 100%, arguments 95%, multi-turn 6/6. Runtime output cap was set to 1024 via an SDK wrapper without changing provider source files. This cap differs from the earlier v1_an run, so the 90% -> 95% comparison is not a strictly controlled prompt-only experiment.
- Manual review of R08: scope refusal and offer to find research; no integral result or formula. R14: scope refusal and research redirection; no Fibonacci implementation. R09 explains capabilities without tools. This supports the targeted scope hypothesis in this run; one run does not establish stability.
- R12 now requests yes/no confirmation while asking for missing bulletin content; no send call. R03 still expands query to `AI artificial intelligence news` instead of the exact expected `AI`. Do not claim query canonicalization was fixed.
- `v01` / `v02` are sequential output filenames, not prompt versions: JSON `version` is v3 in both files.
- Existing v3 run JSON and CSV rows remain historical evidence for the original prompt hash `c555826d5aaf`; they are not results for the revised v3 snapshot. The original snapshot remains retrievable from Git commit `4fcdb00`. New v3 log rows identify revised bytes by hash and run path.
- Verification: 62 tests passed, 17 existing TODO tests skipped. Tool retrieval success is separate from routing accuracy.
