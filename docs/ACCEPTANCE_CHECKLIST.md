# Acceptance Checklist

All boxes start unchecked. This workbook contains plans, not completed project tests.

## Shared

- [ ] Two independent local project folders and repositories; unrelated work preserved.
- [ ] Exact dependency/tool versions and setup paths recorded.
- [ ] Required commands actually run; failures and remaining blockers stated.
- [ ] Reproduction attempted in a fresh environment.
- [ ] English README with setup, demo, architecture, evidence and limitations.
- [ ] Short English demonstration script with practical learning exercises.
- [ ] One meaningful English incident/bug report per project.
- [ ] AI-assistance disclosure and learner contribution described accurately.
- [ ] Technical and learning progress tracked separately.
- [ ] Local commits focused on the intended repository; no unrelated files staged.
- [ ] No credentials, private certificates, home address or application documents in public project assets.
- [ ] Public publication remains unperformed until separately instructed.

## Software

- [x] S1: Source schema, paging, areas, timezone and cadence checked.
- [x] S1: Real PostgreSQL ready check succeeds.
- [ ] S2: Keys, Decimal and UTC correct; negative prices accepted.
- [ ] S3: Same content loaded twice → unchanged facts and zero extra revisions.
- [ ] S3: One changed price → one current update and one revision.
- [ ] S3: Conflicting same-response duplicate rejected without partial facts.
- [ ] S4: Known DST counts 92/96/100 checked for 15-minute intervals.
- [ ] S4: Missing interval is identified by its exact UTC instant.
- [ ] S4: JOIN, CTE, aggregate and window query have checked answers. / SQL。
- [ ] S5: Timeout/429/5xx have at most three total attempts.
- [ ] S5: Failed facts transaction rolls back; failed-run audit survives.
- [ ] S5: Concurrent run rejected cleanly.
- [ ] S6: Query API, stable pagination, 422 validation and 503 readiness checked.
- [ ] S7: At least 30 historical days loaded for DK1/DK2 if access permits; exact source/range/counts recorded.
- [ ] S7: Offline demo provenance clear; no synthetic-as-real claim.
- [ ] S7: Unit and PostgreSQL integration tests pass without hidden skips.
- [ ] S7: CI status distinguishes configured workflow from observed remote execution.

## Embedded

- [ ] E1: Actual MCU/platform/UART models identified; tested versions recorded.
- [ ] E1/E4: Own ARM ELF compiled, loaded and actually executed in Renode.
- [ ] E2: Moving-average startup, rollover, overflow bound and invalid-input handling checked.
- [ ] E3: Cross-language CRC/golden frames, fragmented/coalesced frames and parser recovery checked.
- [ ] E4: State transitions, sequence wrap, error consumption and duplicate protection checked.
- [ ] E5: Optical model assumptions and units explicit; noise-free 0/10/60 uW checks correct.
- [ ] E5: Reference filter/calculation independent from production firmware.
- [ ] E6: C# ↔ Renode communication actually runs; fake transport alone is not counted.
- [ ] E6: Lost-response retry processes FEED only once.
- [ ] E6: Reboot/disconnect interrupts current test and starts a labelled new session.
- [ ] E6: Reset while TCP stays connected is detected through NEEDS_HELLO/ERR_SESSION.
- [ ] E6: Exhausted retries or post-send cancellation close/invalidate the session and report an indeterminate outcome; no cross-session replay.
- [ ] E7: Dark baseline, light step, linearity, noise, saturation and communication recovery reports produced.
- [ ] E7: Raw/filtered metrics, clipping exclusions, config/hash/version evidence recorded.
- [ ] E7: An interrupted or missing required scenario cannot yield overall PASS.
- [ ] E8: No physical ADC, DMA, timing, optical calibration or hardware-debugging claims from the virtual sample feed.
- [ ] E8: Headless tests and reproducible demo run; exact CI state reported.

## Personal learning

- [ ] Learner runs a real software import and explains the row count.
- [ ] Learner writes/changes a JOIN and a window query. / SQL。
- [ ] Learner diagnoses a missing-data case with evidence.
- [ ] Learner explains UTC, idempotency and rollback in English.
- [ ] Learner builds/loads the firmware or independently runs the documented emulator flow.
- [ ] Learner changes one alarm limit and explains its effect.
- [ ] Learner diagnoses a corrupted frame or lost-response case.
- [ ] Learner explains the optical model, smoothing delay and saturation exclusion in English.
- [ ] Learner clearly separates ARM execution, host calculation, virtual input and real-hardware gaps.
- [ ] Learner gives two independent three-minute demos and handles follow-up questions.

## Evidence entry template

```text
Task:
Date and environment:
Command:
Expected result:
Observed result:
Evidence path:
Verification layer (unit/PostgreSQL/API/host C/ARM emulator/personal practice):
Limitations:
Implementation status:
Learning status:
Next action:
```

An unchecked learning item does not invalidate a verified implementation task, but it prevents a claim that the learner independently understands that item.
