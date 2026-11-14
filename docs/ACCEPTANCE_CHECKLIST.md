# Acceptance Checklist / 验收工作单

All boxes start unchecked. This workbook contains plans, not completed project tests.
初始全部未勾选；工作单不是项目测试已通过的证明。

## Shared / 共同要求

- [ ] Two independent local project folders and repositories; unrelated work preserved. / 两个独立目录与仓库。
- [ ] Exact dependency/tool versions and setup paths recorded. / 版本与配置路径。
- [ ] Required commands actually run; failures and remaining blockers stated. / 真实运行与失败记录。
- [ ] Reproduction attempted in a fresh environment. / 干净环境复现。
- [ ] English README with setup, demo, architecture, evidence and limitations. / 英文说明。
- [ ] Short English demonstration script with Chinese learning support. / 英文演示稿配中文。
- [ ] One meaningful English incident/bug report per project. / 每项一个有意义的故障报告。
- [ ] AI-assistance disclosure and learner contribution described accurately. / AI 协助与本人贡献准确。
- [ ] Technical and learning progress tracked separately. / 技术与学习分开。
- [ ] Local commits focused on the intended repository; no unrelated files staged. / 提交范围准确。
- [ ] No credentials, private certificates, home address or application documents in public project assets. / 求职隐私材料不进入公开作品。
- [ ] Public publication remains unperformed until separately instructed. / 未另行指示前不公开发布。

## Software / 软件

- [x] S1: Source schema, paging, areas, timezone and cadence checked. / 来源约定。
- [x] S1: Real PostgreSQL ready check succeeds. / 真数据库。
- [ ] S2: Keys, Decimal and UTC correct; negative prices accepted. / 数据结构。
- [ ] S3: Same content loaded twice → unchanged facts and zero extra revisions. / 幂等。
- [ ] S3: One changed price → one current update and one revision. / 修订。
- [ ] S3: Conflicting same-response duplicate rejected without partial facts. / 冲突。
- [ ] S4: Known DST counts 92/96/100 checked for 15-minute intervals. / 夏令时。
- [ ] S4: Missing interval is identified by its exact UTC instant. / 缺口。
- [ ] S4: JOIN, CTE, aggregate and window query have checked answers. / SQL。
- [ ] S5: Timeout/429/5xx have at most three total attempts. / 有界重试。
- [ ] S5: Failed facts transaction rolls back; failed-run audit survives. / 回滚与审计。
- [ ] S5: Concurrent run rejected cleanly. / 并发。
- [ ] S6: Query API, stable pagination, 422 validation and 503 readiness checked. / 接口。
- [ ] S7: At least 30 historical days loaded for DK1/DK2 if access permits; exact source/range/counts recorded. / 真实数据。
- [ ] S7: Offline demo provenance clear; no synthetic-as-real claim. / 离线来源。
- [ ] S7: Unit and PostgreSQL integration tests pass without hidden skips. / 测试。
- [ ] S7: CI status distinguishes configured workflow from observed remote execution. / CI 状态。

## Embedded / 嵌入式

- [ ] E1: Actual MCU/platform/UART models identified; tested versions recorded. / 平台核实。
- [ ] E1/E4: Own ARM ELF compiled, loaded and actually executed in Renode. / ARM 执行。
- [ ] E2: Moving-average startup, rollover, overflow bound and invalid-input handling checked. / 滤波。
- [ ] E3: Cross-language CRC/golden frames, fragmented/coalesced frames and parser recovery checked. / 协议。
- [ ] E4: State transitions, sequence wrap, error consumption and duplicate protection checked. / 状态与序号。
- [ ] E5: Optical model assumptions and units explicit; noise-free 0/10/60 uW checks correct. / 模型。
- [ ] E5: Reference filter/calculation independent from production firmware. / 独立参考。
- [ ] E6: C# ↔ Renode communication actually runs; fake transport alone is not counted. / 通信。
- [ ] E6: Lost-response retry processes FEED only once. / 重试去重。
- [ ] E6: Reboot/disconnect interrupts current test and starts a labelled new session. / 会话。
- [ ] E6: Reset while TCP stays connected is detected through NEEDS_HELLO/ERR_SESSION. / 连接保留时仍识别复位。
- [ ] E6: Exhausted retries or post-send cancellation close/invalidate the session and report an indeterminate outcome; no cross-session replay. / 不确定结果不冒充成功或继续执行。
- [ ] E7: Dark baseline, light step, linearity, noise, saturation and communication recovery reports produced. / 六类场景。
- [ ] E7: Raw/filtered metrics, clipping exclusions, config/hash/version evidence recorded. / 报告。
- [ ] E7: An interrupted or missing required scenario cannot yield overall PASS. / 总结判定。
- [ ] E8: No physical ADC, DMA, timing, optical calibration or hardware-debugging claims from the virtual sample feed. / 能力边界。
- [ ] E8: Headless tests and reproducible demo run; exact CI state reported. / 自动化复现。

## Personal learning / 本人学习

- [ ] Learner runs a real software import and explains the row count. / 导入。
- [ ] Learner writes/changes a JOIN and a window query. / SQL。
- [ ] Learner diagnoses a missing-data case with evidence. / 软件排查。
- [ ] Learner explains UTC, idempotency and rollback in English. / 软件英文。
- [ ] Learner builds/loads the firmware or independently runs the documented emulator flow. / 固件流程。
- [ ] Learner changes one alarm limit and explains its effect. / 修改参数。
- [ ] Learner diagnoses a corrupted frame or lost-response case. / 协议排查。
- [ ] Learner explains the optical model, smoothing delay and saturation exclusion in English. / 光电英文。
- [ ] Learner clearly separates ARM execution, host calculation, virtual input and real-hardware gaps. / 验证层次。
- [ ] Learner gives two independent three-minute demos and handles follow-up questions. / 面试展示。

## Evidence entry template / 证据条目

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
学习未完成不等于技术测试失败，但不能声称本人已经独立掌握。
