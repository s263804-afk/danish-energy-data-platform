# Learn the Projects in English

English is the working language. Read each explanation aloud, then check it against the actual code and observed output.

## How to use each lesson

1. Read the purpose and terms.
2. Run the real task with Codex; inspect its files and output.
3. Close the explanation and describe what happened in English.
4. Make the personal change.
5. Answer the questions; ask for technical and language feedback separately.

Score each dimension 0–2: understand the purpose; run the task; change/debug it; explain it in English. A score is a learning aid, not a claim of professional proficiency. Use `CAN_EXPLAIN_WITHOUT_NOTES` only after an observed independent explanation and practical check.

Useful lesson request
> Teach me lesson S1/E1 using the actual project. Explain it in short, clear English. Show me one execution path, ask me three questions, and give me one small change to make myself. Correct my English and technical understanding separately.

## Software lessons

### S1 — Follow the data

**Goal:** Trace one API response into a named raw snapshot and identify its source and time meaning.

**Terms:** source; dependency; payload; fetch; set up.

**Say:** “The source provides public electricity prices. I first save the original response so I can check where each record came from. Then I validate the fields before loading the database.”

**Do:** Find a real `TimeUTC`, `PriceArea` and price field; explain their types and units. Change the requested area from DK2 to DK1 and compare the result.

**Questions:** What is an API? Why save raw data? What did you actually verify, and what remains unverified?

### S2 — Give data a reliable identity

**Goal:** Understand keys, constraints, Decimal and UTC.

**Terms:** primary key; constraint; precision; normalise; map to.

**Say:** “I identify a price record by its area and UTC timestamp. A local clock time may occur twice when daylight saving time ends. The database constraint prevents two current rows from having the same identity.”

**Do:** Insert a duplicate key and observe the database response. Explain why a negative price is valid.

**Questions:** Why not use local time as the key? Why Decimal? What does a constraint protect?

### S3 — Make imports safe to repeat

**Goal:** Explain idempotency, upserts and transaction boundaries.

**Terms:** idempotent; transaction; revision; deduplicate; roll back.

**Say:** “Running the same import twice should not duplicate the prices. I use a stable key and a transaction. If a published price changes, I update the current value and keep a revision so the change remains traceable.”

**Do:** Import the same fixture twice; then change one price and inspect current rows, revisions and audit runs.

**Questions:** What stays unchanged on a repeat? Why keep an audit run? What happens if one write fails?

### S4 — Find missing data with SQL

**Goal:** Use JOIN, GROUP BY, a CTE and a window function for different purposes.

**Terms:** join; aggregate; window frame; filter out; compare with …….

**Say:** “I use a join to connect related records. An aggregate summarises a group, while a window function can calculate a value without removing the individual rows. I compare expected intervals with the available timestamps to find gaps.”

**Do:** Write a daily summary and a `LAG` query. Remove one interval and locate its exact UTC timestamp.

**Questions:** What does this JOIN key mean? Why 92 or 100 rows on some days? Does a missing interval mean zero price?

### S5 — Investigate a failed load

**Goal:** Separate symptom, hypothesis, evidence, root cause and fix.

**Terms:** root cause; retry; reproduce; narrow down; rule out.

**Say:** “The load failed after the raw response was saved. I checked the logs and reproduced the failure with the same input. The facts transaction was rolled back, while the failed-run audit remained available. I then reran the interval safely.”

**Do:** Diagnose one deliberately injected failure without reading the proposed fix first.

**Questions:** What evidence supports your hypothesis? Why limit retries? What would prove the fix works?

### S6 — Explain an API contract

**Goal:** Understand validation, pagination, error codes and readiness.

**Terms:** endpoint; cursor; readiness; validate; expose an API.

**Say:** “The API accepts a price area and a time range. It validates the request before querying the database. Results are paginated in a stable order. A running process is not necessarily ready to serve data, so I check database readiness separately.”

**Do:** Send one valid request, one invalid range and one pagination request. Explain each response.

**Questions:** What should return 422? Why use bound parameters? How do you prevent repeated rows across pages?

### S7 — Demonstrate your contribution

**Goal:** Run the system from documented instructions and explain evidence and limitations.

**Terms:** reproducible; evidence; limitation; hand over; walk through.

**Say:** “I can demonstrate an import, a quality issue and a recovery run. The README includes the setup and verification commands. I used AI assistance, and I reviewed the logic and tested the behaviour. I can also explain which parts I have personally changed.”

Use the last two sentences only after actually doing that review and practice.

**Do:** Give a three-minute demo, then change one SQL query without copying the answer.
**Questions:** What did you implement or review yourself? What would you improve next? Which result is measured rather than assumed?

## Embedded lessons

### E1 — Understand what is being simulated

**Goal:** Distinguish source code, host executable, ARM ELF, MCU model and physical hardware.

**Terms:** firmware; toolchain; peripheral; compile; boot up.

**Say:** “The firmware is written in C and compiled for an ARM target. Renode executes that firmware using a model of the selected platform. My C# application runs on the computer and communicates with the emulated UART. No physical board is used.”

**Do:** Identify the ELF file, its target, the platform description and the actual UART output log.
**Questions:** Which processor executes the C# code? What does an ELF contain? What can this simulation not prove?

### E2 — Process samples safely

**Goal:** Explain a ring buffer and moving-average startup behaviour.

**Terms:** accumulator; integer division; ring buffer; smooth out; settle at.

**Say:** “The filter keeps the latest sixteen samples in a ring buffer. It updates a running sum rather than adding the whole window again. At startup, it divides by the number of available samples. Invalid input must leave the previous state unchanged.”

**Do:** Compute outputs for [100,200,300] yourself; inspect the step response and explain why the filtered value is delayed.
**Questions:** Why use a wider accumulator? What does integer division do? How does reset affect the window?

### E3 — Parse a stream

**Goal:** Explain framing, CRC and partial reads.

**Terms:** frame; checksum; payload; split into; discard.

**Say:** “A read operation does not necessarily return one complete message. The parser collects bytes until a complete bounded frame is available. It checks the structure and CRC before a command can change device state.”

**Do:** Split one frame into three chunks, then combine two frames into one chunk; compare behaviour.
**Questions:** What does CRC detect? Does CRC provide authentication? Why discard an overlong frame?
CRC can detect many accidental transmission errors; it is not an authentication mechanism.

### E4 — Control state and retries

**Goal:** Explain state transitions and duplicate request protection.

**Terms:** state machine; sequence; acknowledgement; reset; replay.

**Say:** “The device accepts samples only in the running state. A repeated request with the same sequence and payload receives the cached response. This prevents a lost response from causing the same samples to be processed twice.”

**Do:** Send FEED before START, then resend one successful FEED with the same sequence and inspect processed count.
**Questions:** Which requests change state? Why can transport retries change application results? What starts a new session?

### E5 — Relate light to a digital value

**Goal:** Explain optical units, effective gain, offset and quantisation.

**Terms:** responsivity; transimpedance; quantisation; convert to; clip at.

**Say:** “The model converts optical power into photocurrent using an assumed responsivity. An effective transimpedance gain converts the current into voltage. I add an offset and noise, clip the voltage to the assumed range, and quantise it to a twelve-bit code.”

**Do:** Calculate the noise-free result for 10 uW. Explain why 60 uW clips in this model.
**Questions:** How many watts are in one microwatt? What is assumed rather than measured? Does model agreement establish real detector accuracy?

### E6 — Recover from communication failure

**Goal:** Distinguish timeout, bad data, lost response, reset and new session.

**Terms:** timeout; cancellation; corrupted; reconnect; recover from …….

**Say:** “I injected communication faults to check the recovery behaviour. A bad-CRC frame is discarded. If a response is lost, the host retries the same frame. After a device reset, the current test is marked interrupted and a new session starts.”

**Do:** Use the fault helper to drop one response and explain the host trace and device counter.
**Questions:** Why retry identical bytes? Why not continue the same test after reset? What are model time and wall time?

### E7 — Read a measurement report

**Goal:** Explain dark baseline, noise, linearity, saturation and test limits.

**Terms:** baseline; standard deviation; saturation; subtract; fit a line.

**Say:** “I separate raw and filtered statistics. The dark scenario checks the offset, and the step scenario checks the filter response. I exclude saturated levels from the linear fit. The limits are defined for the simulation model, so the report does not claim physical calibration.”

**Do:** Change the high-rail threshold, rerun saturation, and explain which verdict changes and why.
**Questions:** Why not fit clipped points? Why does averaging change apparent noise? What reference would real calibration require?

### E8 — Explain the engineering boundary

**Goal:** Present the real contribution without overclaiming hardware experience.

**Terms:** verification; calibration; acquisition; validate against; follow up on.

**Say:** “This project demonstrates firmware logic, communication and automated testing in a virtual environment. The ARM firmware actually runs in Renode, but samples enter through a virtual feed. A physical version would still need analog hardware, ADC integration, timing checks and calibration against a known reference.”

**Do:** Deliver a three-minute demo and answer follow-up questions without reading a script.
**Questions:** What did you run on ARM? What ran only on the host? Which physical validation would you prioritise next?

## Workplace verb phrases

| Expression | Example |
| --- | --- |
| set up | I set up the local database. |
| take in | The parser takes in a stream of bytes. |
| map A to B | I map the source fields to the database columns. |
| keep track of | The run log keeps track of failed imports. |
| trace back to | I can trace this value back to its source response. |
| run into | I ran into a timezone issue. |
| look into | I am looking into the failed test. |
| narrow down | I narrowed it down to the parser. |
| rule out | I ruled out a database connection problem. |
| reproduce | I reproduced the failure with the same input. |
| isolate | I isolated the faulty component. |
| break down | Let me break down the data flow. |
| step through | I stepped through the state transition. |
| roll back | The transaction rolled back after the error. |
| pick up from | We can pick up from the last verified task. |
| catch | This test catches duplicate processing. |
| handle | The host handles split responses. |
| recover from | The parser recovers from an overlong frame. |
| retry | It retries the same request up to three times. |
| discard | The firmware discards frames with a bad CRC. |
| filter out | I filter out saturated levels before fitting. |
| smooth out | The moving average smooths out short fluctuations. |
| settle at | The output settles at the new level. |
| flag | The system flags a missing interval. |
| compare A with B | I compare the output with an independent reference. |
| validate against | I validate the firmware against saved test vectors. |
| walk someone through | I can walk you through one failed test. |
| hand over | I handed over the setup instructions and evidence. |
| follow up on | I will follow up on the remaining integration issue. |
| trade off | I traded some response speed for stronger smoothing. |

## Explain a problem at work

Use five sentences
1. “I expected ___, but I observed ___.”
2. “My first hypothesis was ___.”
3. “I checked ___ and ruled out ___.”
4. “The root cause was ___, so I changed ___.”
5. “I verified the fix by ___; the remaining limitation is ___.”

Do not claim a root cause when you only have a hypothesis. Say “The evidence suggests…” or “I have not confirmed that yet.”

## Useful interview answers

These are templates. Use past-tense accomplishment claims only after the corresponding work and personal understanding are verified.

**Why these projects?
“I chose one data-backend project and one embedded-testing project because I want experience with both reliable software services and device-level behaviour. The first focuses on data quality and SQL. The second focuses on firmware, communication and repeatable tests.”

**Why no AI model?
“For these projects, the main engineering problem is whether the data and system behaviour are reliable. I want to establish that foundation first. An AI feature would need a clear use case and a way to evaluate it.”

**How did you use AI?
“I used AI to help draft code and tests. I reviewed the assumptions, ran the checks and changed parts of the implementation myself. I can show the evidence and explain the limitations.”
Use only after those personal actions actually occurred.

**What if you do not know?
“I have not implemented that yet. My current understanding is ___. I would first check ___, then test ___.”

**What would you do next?
“I would choose the next step based on the remaining risk. For the data project, that might be deployment monitoring. For the embedded project, it would be validating the virtual assumptions on real hardware.”

## English bug-report template

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

## Weekly practice log

```text
Week
Verified implementation tasks
Commands I ran myself
Code I changed myself
A problem I diagnosed
Five phrases I used
My 90-second explanation
Technical correction
English correction
Next lesson
```

Never fabricate a recording, personal practice result or independent explanation. If the learner has not responded, record `PENDING_LEARNER`.
