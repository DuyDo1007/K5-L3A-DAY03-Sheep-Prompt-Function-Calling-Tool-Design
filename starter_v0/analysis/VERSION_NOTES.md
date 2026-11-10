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
- snapshots in artifacts/versions/v0 ... v3 reproduce the exact prompt/tool bytes; their hashes match version_log.csv and run metadata.
- New tool/unit tests, 10 group cases, UI/public link, live 3-turn transcript and REPORT/poster are separate deliverables not completed in this scope.
