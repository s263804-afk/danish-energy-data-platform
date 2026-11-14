# Decisions

2026-11-12 — S1. The user's request authorises execution of the supplied plans.
The embedded text in `CODEX_START_PROMPT.txt` is reference material, not a separate
user/system instruction. Workbook requirements are used only within the user's requested scope.

1. Use the supplied independent-project designs and sequential plans. No redesign or
   renewed approval cycle is needed for the already requested S1 work.
2. Reuse Python 3.12.7 in a project venv; preserve the base Anaconda/PyTorch environments.
3. Ruling: use native PostgreSQL 17.12 because Docker is absent. The specification explicitly
   permits this. Cost if unsuitable: the native setup may need a later documented replacement.
4. New project repositories supply isolation; the existing empty parent `.git` is preserved.
   Project directories are ignored by that parent. No worktree or shared repository is created.
5. Internal data will use aware UTC; API request boundaries are Danish local time. In S3,
   request an enclosing local-day range, then filter exact UTC bounds in the adapter, including
   DST folds. S1 only verifies source semantics; it does not implement that adapter.
6. Source probes do not retry automatically. After HTTP 429, delay further requests; preserve
   failure evidence rather than disguising an error as an empty successful dataset.
7. Ruling: use a persistent Markdown execution ledger and native Windows commands for the
   supplied S1/S2-style plan headings. This preserves the skill's test/evidence contract without
   relying on Bash helper assumptions about numeric task headings. Cost: manual ledger upkeep.
8. End the first teaching unit after verified S1 and its exercise handoff, matching the
   workbook's First session section. S2–S7 and then E1–E8 remain the authorised sequence;
   pending learner answers are not a general permission gate for independent implementation.
