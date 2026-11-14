# Learn the Projects in English / 中英对照学习册

English is the working language. Chinese explains meaning and prevents technical misunderstandings. Read the English aloud before reading the translation where possible.
英文作为工作语言；中文帮助理解和校准概念。尽量先朗读英文，再看中文。

## How to use each lesson / 每节课怎么学

1. Read the purpose and terms. / 先读目的与词汇。
2. Run the real task with Codex; inspect its files and output. / 实际运行并看代码和结果。
3. Close the explanation and describe what happened in English. / 合上说明，用英文复述。
4. Make the personal change. / 本人做一处修改。
5. Answer the questions; ask for technical and language feedback separately. / 分别获得技术和英语反馈。

Score each dimension 0–2: understand the purpose; run the task; change/debug it; explain it in English. A score is a learning aid, not a claim of professional proficiency. Use `CAN_EXPLAIN_WITHOUT_NOTES` only after an observed independent explanation and practical check.
四项各 0–2 分：理解用途、运行、修改排错、英文讲解；这只是学习记录，不等于职业熟练度认证。

Useful lesson request / 可以直接使用的学习请求:
> Teach me lesson S1/E1 using the actual project. Explain it in short English with Chinese support. Show me one execution path, ask me three questions, and give me one small change to make myself. Correct my English and technical understanding separately.
> 用实际项目教我 S1/E1。短英文配中文，走读一条流程，问三个问题，让我本人修改一处，分别纠正技术与英语。

## Software lessons / 软件课程

### S1 — Follow the data / 跟着数据走

**Goal:** Trace one API response into a named raw snapshot and identify its source and time meaning.
**目标：** 跟踪一条响应，知道原文存在哪里、来自哪里、时间代表什么。

**Terms:** source 数据来源; dependency 依赖; payload 响应内容; fetch 获取; set up 配置。

**Say:** “The source provides public electricity prices. I first save the original response so I can check where each record came from. Then I validate the fields before loading the database.”
**中译：** 来源提供公开电价。我先保存原始响应，以便追溯记录，再校验字段并导入数据库。

**Do:** Find a real `TimeUTC`, `PriceArea` and price field; explain their types and units. Change the requested area from DK2 to DK1 and compare the result.
**本人练习：** 找字段、类型和单位，再切换区域。

**Questions:** What is an API? Why save raw data? What did you actually verify, and what remains unverified?
**问题：** API 是什么？为什么存原文？当前哪些已验证、哪些尚未验证？

### S2 — Give data a reliable identity / 给数据可靠的身份

**Goal:** Understand keys, constraints, Decimal and UTC.
**目标：** 理解唯一键、约束、定点数与 UTC。

**Terms:** primary key 主键; constraint 约束; precision 精度; normalise 规范化; map to 映射到。

**Say:** “I identify a price record by its area and UTC timestamp. A local clock time may occur twice when daylight saving time ends. The database constraint prevents two current rows from having the same identity.”
**中译：** 区域和 UTC 时间确定一条电价记录。夏令时结束时当地时刻可能重复，数据库约束阻止同一身份出现两条当前记录。

**Do:** Insert a duplicate key and observe the database response. Explain why a negative price is valid.
**本人练习：** 观察重复键，并解释负电价。

**Questions:** Why not use local time as the key? Why Decimal? What does a constraint protect?
**问题：** 为什么不用当地时间作键？为什么用 Decimal？约束保护什么？

### S3 — Make imports safe to repeat / 让导入能安全重跑

**Goal:** Explain idempotency, upserts and transaction boundaries.
**目标：** 讲清幂等、更新插入和事务。

**Terms:** idempotent 幂等; transaction 事务; revision 修订; deduplicate 去重; roll back 回滚。

**Say:** “Running the same import twice should not duplicate the prices. I use a stable key and a transaction. If a published price changes, I update the current value and keep a revision so the change remains traceable.”
**中译：** 重复导入不能产生重复价格；用稳定键和事务。来源价格变化时更新当前值并保留修订。

**Do:** Import the same fixture twice; then change one price and inspect current rows, revisions and audit runs.
**本人练习：** 比较重复导入和单条修订后的三类记录。

**Questions:** What stays unchanged on a repeat? Why keep an audit run? What happens if one write fails?
**问题：** 重跑什么不变？为何仍有运行审计？一处写入失败怎么办？

### S4 — Find missing data with SQL / 用 SQL 找缺口

**Goal:** Use JOIN, GROUP BY, a CTE and a window function for different purposes.
**目标：** 区分关联、聚合、CTE 与窗口函数。

**Terms:** join 关联; aggregate 聚合; window frame 窗口范围; filter out 筛除; compare with 与……比较。

**Say:** “I use a join to connect related records. An aggregate summarises a group, while a window function can calculate a value without removing the individual rows. I compare expected intervals with the available timestamps to find gaps.”
**中译：** JOIN 连接相关记录；聚合汇总分组，窗口函数可保留逐行记录；预期时间与现有时间比较找缺口。

**Do:** Write a daily summary and a `LAG` query. Remove one interval and locate its exact UTC timestamp.
**本人练习：** 写汇总与前行比较，主动制造并定位缺口。

**Questions:** What does this JOIN key mean? Why 92 or 100 rows on some days? Does a missing interval mean zero price?
**问题：** 关联键是什么？为什么有 92/100 条的日期？缺失是否等于零？

### S5 — Investigate a failed load / 排查失败导入

**Goal:** Separate symptom, hypothesis, evidence, root cause and fix.
**目标：** 区分现象、假设、证据、根因与修复。

**Terms:** root cause 根因; retry 重试; reproduce 复现; narrow down 缩小范围; rule out 排除。

**Say:** “The load failed after the raw response was saved. I checked the logs and reproduced the failure with the same input. The facts transaction was rolled back, while the failed-run audit remained available. I then reran the interval safely.”
**中译：** 保存原文后导入失败。我查日志并用相同输入复现；数据事务回滚，失败审计保留，再安全重跑。

**Do:** Diagnose one deliberately injected failure without reading the proposed fix first.
**本人练习：** 先看现象与证据，自行排查再看答案。

**Questions:** What evidence supports your hypothesis? Why limit retries? What would prove the fix works?
**问题：** 哪个证据支持假设？为何限制重试？如何证明修复有效？

### S6 — Explain an API contract / 说明接口约定

**Goal:** Understand validation, pagination, error codes and readiness.
**目标：** 理解校验、分页、错误码与就绪状态。

**Terms:** endpoint 接口地址; cursor 游标; readiness 就绪; validate 校验; expose an API 提供接口。

**Say:** “The API accepts a price area and a time range. It validates the request before querying the database. Results are paginated in a stable order. A running process is not necessarily ready to serve data, so I check database readiness separately.”
**中译：** 接口接收区域与区间，先校验再查库，稳定分页；进程运行不等于能提供数据，所以单独检查数据库就绪。

**Do:** Send one valid request, one invalid range and one pagination request. Explain each response.
**本人练习：** 发送正常、错误区间及翻页请求。

**Questions:** What should return 422? Why use bound parameters? How do you prevent repeated rows across pages?
**问题：** 哪些情况返回 422？为什么绑定参数？分页如何避免重复？

### S7 — Demonstrate your contribution / 展示本人贡献

**Goal:** Run the system from documented instructions and explain evidence and limitations.
**目标：** 按说明运行，准确展示证据与限制。

**Terms:** reproducible 可复现; evidence 证据; limitation 限制; hand over 交接; walk through 走读。

**Say:** “I can demonstrate an import, a quality issue and a recovery run. The README includes the setup and verification commands. I used AI assistance, and I reviewed the logic and tested the behaviour. I can also explain which parts I have personally changed.”
**中译：** 我能展示导入、质量问题与恢复。说明含配置与验证命令；AI 协助后本人复核测试，并能说明本人修改部分。

Use the last two sentences only after actually doing that review and practice.
后两句必须本人真正复核和练习后才能使用。

**Do:** Give a three-minute demo, then change one SQL query without copying the answer.
**Questions:** What did you implement or review yourself? What would you improve next? Which result is measured rather than assumed?

## Embedded lessons / 嵌入式课程

### E1 — Understand what is being simulated / 理解仿真层次

**Goal:** Distinguish source code, host executable, ARM ELF, MCU model and physical hardware.
**目标：** 分清源代码、电脑程序、ARM ELF、MCU 模型和实物。

**Terms:** firmware 固件; toolchain 工具链; peripheral 外设; compile 编译; boot up 启动。

**Say:** “The firmware is written in C and compiled for an ARM target. Renode executes that firmware using a model of the selected platform. My C# application runs on the computer and communicates with the emulated UART. No physical board is used.”
**中译：** C 固件编译到 ARM，Renode 在平台模型上执行；C# 在电脑与模拟 UART 通信，没有实物板。

**Do:** Identify the ELF file, its target, the platform description and the actual UART output log.
**Questions:** Which processor executes the C# code? What does an ELF contain? What can this simulation not prove?

### E2 — Process samples safely / 安全处理样本

**Goal:** Explain a ring buffer and moving-average startup behaviour.
**目标：** 讲清环形缓存和平均的起始阶段。

**Terms:** accumulator 累加器; integer division 整数除法; ring buffer 环形缓存; smooth out 平滑; settle at 稳定在。

**Say:** “The filter keeps the latest sixteen samples in a ring buffer. It updates a running sum rather than adding the whole window again. At startup, it divides by the number of available samples. Invalid input must leave the previous state unchanged.”
**中译：** 环形缓存保留最近 16 点，更新累加和；起始按已有点数平均；无效输入不改变状态。

**Do:** Compute outputs for [100,200,300] yourself; inspect the step response and explain why the filtered value is delayed.
**Questions:** Why use a wider accumulator? What does integer division do? How does reset affect the window?

### E3 — Parse a stream / 解析连续字节流

**Goal:** Explain framing, CRC and partial reads.
**目标：** 讲清帧边界、校验与分片读取。

**Terms:** frame 数据帧; checksum 校验值; payload 有效内容; split into 分成; discard 丢弃。

**Say:** “A read operation does not necessarily return one complete message. The parser collects bytes until a complete bounded frame is available. It checks the structure and CRC before a command can change device state.”
**中译：** 一次读取未必是一条完整消息；解析器收集完整有界帧，验证结构与 CRC 后才允许改变设备状态。

**Do:** Split one frame into three chunks, then combine two frames into one chunk; compare behaviour.
**Questions:** What does CRC detect? Does CRC provide authentication? Why discard an overlong frame?
CRC can detect many accidental transmission errors; it is not an authentication mechanism.
CRC 可发现很多意外传输错误，不提供身份认证。

### E4 — Control state and retries / 管理状态与重试

**Goal:** Explain state transitions and duplicate request protection.
**目标：** 讲清状态转换与重复请求保护。

**Terms:** state machine 状态机; sequence 序号; acknowledgement 确认; reset 重置; replay 重放。

**Say:** “The device accepts samples only in the running state. A repeated request with the same sequence and payload receives the cached response. This prevents a lost response from causing the same samples to be processed twice.”
**中译：** 只在运行态接收样本；相同序号与内容返回缓存响应，避免丢回复后的重试重复处理数据。

**Do:** Send FEED before START, then resend one successful FEED with the same sequence and inspect processed count.
**Questions:** Which requests change state? Why can transport retries change application results? What starts a new session?

### E5 — Relate light to a digital value / 从光强到数字码

**Goal:** Explain optical units, effective gain, offset and quantisation.
**目标：** 讲清光学单位、等效增益、偏置与量化。

**Terms:** responsivity 响应度; transimpedance 跨阻; quantisation 量化; convert to 换算为; clip at 钳位到。

**Say:** “The model converts optical power into photocurrent using an assumed responsivity. An effective transimpedance gain converts the current into voltage. I add an offset and noise, clip the voltage to the assumed range, and quantise it to a twelve-bit code.”
**中译：** 模型用假设响应度将光功率变为电流，再用等效跨阻变电压，加偏置噪声、限制范围并量化。

**Do:** Calculate the noise-free result for 10 uW. Explain why 60 uW clips in this model.
**Questions:** How many watts are in one microwatt? What is assumed rather than measured? Does model agreement establish real detector accuracy?

### E6 — Recover from communication failure / 从通信故障恢复

**Goal:** Distinguish timeout, bad data, lost response, reset and new session.
**目标：** 分清超时、坏数据、丢回复、重启与新会话。

**Terms:** timeout 超时; cancellation 取消; corrupted 损坏; reconnect 重连; recover from 从……恢复。

**Say:** “I injected communication faults to check the recovery behaviour. A bad-CRC frame is discarded. If a response is lost, the host retries the same frame. After a device reset, the current test is marked interrupted and a new session starts.”
**中译：** 注入通信故障检查恢复；坏 CRC 丢弃，丢回复重试相同帧；设备重启后当前测试中断，新开会话。

**Do:** Use the fault helper to drop one response and explain the host trace and device counter.
**Questions:** Why retry identical bytes? Why not continue the same test after reset? What are model time and wall time?

### E7 — Read a measurement report / 读懂测量报告

**Goal:** Explain dark baseline, noise, linearity, saturation and test limits.
**目标：** 讲清暗态基线、噪声、线性度、饱和和验收限制。

**Terms:** baseline 基线; standard deviation 标准差; saturation 饱和; subtract 减去; fit a line 拟合直线。

**Say:** “I separate raw and filtered statistics. The dark scenario checks the offset, and the step scenario checks the filter response. I exclude saturated levels from the linear fit. The limits are defined for the simulation model, so the report does not claim physical calibration.”
**中译：** 原始与滤波统计分开；暗态查偏置，阶跃查滤波响应；线性拟合排除饱和点；模型阈值不能宣称真实校准。

**Do:** Change the high-rail threshold, rerun saturation, and explain which verdict changes and why.
**Questions:** Why not fit clipped points? Why does averaging change apparent noise? What reference would real calibration require?

### E8 — Explain the engineering boundary / 说明工程边界

**Goal:** Present the real contribution without overclaiming hardware experience.
**目标：** 准确展示能力和实物经验边界。

**Terms:** verification 验证; calibration 校准; acquisition 采集; validate against 对照验证; follow up on 跟进。

**Say:** “This project demonstrates firmware logic, communication and automated testing in a virtual environment. The ARM firmware actually runs in Renode, but samples enter through a virtual feed. A physical version would still need analog hardware, ADC integration, timing checks and calibration against a known reference.”
**中译：** 项目展示虚拟环境的固件、通信与自动测试；ARM 固件真实运行，但输入由虚拟接口注入。实物仍需模拟硬件、ADC、时序验证及参考校准。

**Do:** Deliver a three-minute demo and answer follow-up questions without reading a script.
**Questions:** What did you run on ARM? What ran only on the host? Which physical validation would you prioritise next?

## Workplace verb phrases / 职场常用动词表达

| Expression / 表达 | 中文 | Example / 例句 |
|---|---|---|
| set up | 配置、搭建 | I set up the local database. |
| take in | 接收、读入 | The parser takes in a stream of bytes. |
| map A to B | 将 A 映射到 B | I map the source fields to the database columns. |
| keep track of | 持续记录 | The run log keeps track of failed imports. |
| trace back to | 追溯到 | I can trace this value back to its source response. |
| run into | 遇到问题 | I ran into a timezone issue. |
| look into | 调查 | I am looking into the failed test. |
| narrow down | 缩小范围 | I narrowed it down to the parser. |
| rule out | 排除 | I ruled out a database connection problem. |
| reproduce | 复现 | I reproduced the failure with the same input. |
| isolate | 隔离、定位 | I isolated the faulty component. |
| break down | 分解 | Let me break down the data flow. |
| step through | 逐步调试 | I stepped through the state transition. |
| roll back | 回滚 | The transaction rolled back after the error. |
| pick up from | 从某处继续 | We can pick up from the last verified task. |
| catch | 检出问题 | This test catches duplicate processing. |
| handle | 处理 | The host handles split responses. |
| recover from | 从故障恢复 | The parser recovers from an overlong frame. |
| retry | 重试 | It retries the same request up to three times. |
| discard | 丢弃 | The firmware discards frames with a bad CRC. |
| filter out | 筛除 | I filter out saturated levels before fitting. |
| smooth out | 平滑 | The moving average smooths out short fluctuations. |
| settle at | 稳定到 | The output settles at the new level. |
| flag | 标记、告警 | The system flags a missing interval. |
| compare A with B | 对比 | I compare the output with an independent reference. |
| validate against | 对照验证 | I validate the firmware against saved test vectors. |
| walk someone through | 向某人逐步讲解 | I can walk you through one failed test. |
| hand over | 交付、交接 | I handed over the setup instructions and evidence. |
| follow up on | 跟进 | I will follow up on the remaining integration issue. |
| trade off | 在两者间取舍 | I traded some response speed for stronger smoothing. |

## Explain a problem at work / 在工作中解释问题

Use five sentences / 五句话结构:
1. “I expected ___, but I observed ___.” / 预期与实际。
2. “My first hypothesis was ___.” / 初始假设。
3. “I checked ___ and ruled out ___.” / 检查与排除。
4. “The root cause was ___, so I changed ___.” / 根因与修改。
5. “I verified the fix by ___; the remaining limitation is ___.” / 验证与限制。

Do not claim a root cause when you only have a hypothesis. Say “The evidence suggests…” or “I have not confirmed that yet.”
只有假设时不要直接说确定根因，可说“证据表明可能……”或“尚未确认”。

## Useful interview answers / 面试表达

These are templates. Use past-tense accomplishment claims only after the corresponding work and personal understanding are verified.
以下为模板；过去式成果表述必须等实际完成并能解释后再使用。

**Why these projects? / 为什么做这两个项目？**
“I chose one data-backend project and one embedded-testing project because I want experience with both reliable software services and device-level behaviour. The first focuses on data quality and SQL. The second focuses on firmware, communication and repeatable tests.”
“我希望掌握可靠软件服务与设备行为，所以一个项目重点是数据质量和 SQL，另一个重点是固件、通信与可重复测试。”

**Why no AI model? / 为什么不以训练 AI 模型为核心？**
“For these projects, the main engineering problem is whether the data and system behaviour are reliable. I want to establish that foundation first. An AI feature would need a clear use case and a way to evaluate it.”
“这两个项目的核心问题是数据与系统行为是否可靠；先建立基础，AI 扩展需要明确用途和评估方法。”

**How did you use AI? / 如何使用 AI？**
“I used AI to help draft code and tests. I reviewed the assumptions, ran the checks and changed parts of the implementation myself. I can show the evidence and explain the limitations.”
“AI 协助起草代码和测试；本人复核假设、运行检查并亲自修改，能够展示证据和限制。”
Use only after those personal actions actually occurred. / 必须本人真实做过。

**What if you do not know? / 不会时怎么说？**
“I have not implemented that yet. My current understanding is ___. I would first check ___, then test ___.”
“这部分还没实现；目前理解是……；我会先核对……再测试……。”

**What would you do next? / 下一步怎么做？**
“I would choose the next step based on the remaining risk. For the data project, that might be deployment monitoring. For the embedded project, it would be validating the virtual assumptions on real hardware.”
“下一步针对剩余风险；软件可能是部署监控，嵌入式则是用真实硬件验证仿真假设。”

## English bug-report template / 英文缺陷报告模板

```text
Title:
Environment and versions:
Steps to reproduce:
Expected behaviour:
Observed behaviour:
Evidence (logs, frame bytes, query, run ID):
Impact:
Hypothesis / confirmed root cause:
Fix:
Regression test:
Remaining limitations:
```

Prefer concrete observations: “The processed count increased from 16 to 32 after retrying the same frame.” Avoid vague statements such as “The communication is bad.”
优先写具体观察，例如同帧重试后计数从 16 变 32，而不是笼统说通信不好。

## Weekly practice log / 每周练习记录

```text
Week / 周：
Verified implementation tasks / 已验证技术任务：
Commands I ran myself / 本人运行命令：
Code I changed myself / 本人修改代码：
A problem I diagnosed / 本人排查问题：
Five phrases I used / 本周使用的五个表达：
My 90-second explanation / 本人的口述稿或录音位置：
Technical correction / 技术纠正：
English correction / 英语纠正：
Next lesson / 下一课：
```

Never fabricate a recording, personal practice result or independent explanation. If the learner has not responded, record `PENDING_LEARNER`.
本人未答或未操作就记录待完成，不编造录音与掌握结果。
