# S7 — Demonstrate and explain limits

Learning status: material prepared; personal practice pending.

Workplace purpose: Demonstrate and explain limits. 工作用途：让系统行为可检查、可追溯、可解释。

Read the actual path: scripts/demo.ps1 → offline import → reports/demo/software-demo.json.
See the corresponding tests and saved completion logs.

Five terms (including two verb phrases): reproducibility; provenance; limitation; walk through; hand over.

Run: python -m pytest -v --tb=short. Observe the real result and compare with the task's known-answer tests.

Personal exercise: Run a three-minute demo, edit a JOIN/window query, and explain one actual failure.
本人练习须亲自执行并提供输出。

60–90-second practice script:

This task helps me explain how the energy data platform works. Its focus is: demonstrate and explain limits. I start from a documented input and follow the actual code path. I compare the observed result with an expected value, rather than treating a successful command as proof of every feature. The project keeps original source bytes, current values and run evidence so that a result can be traced back. Its tests include normal inputs and deliberately controlled failures. These tests run against PostgreSQL where database behaviour matters. I still need to perform the personal exercise and explain its result independently. AI-assisted implementation and my own demonstrated understanding are recorded separately. The next improvement should be chosen from an observed limitation, with a test that shows the intended behaviour.

中文提示：用途→实际输入与代码→预期与实测→故障证据→本人贡献与限制。
Use first-person accomplishment claims only after performing the action personally.

Questions:
1. What ran on a real database?
2. What did you personally change?
3. What is still unverified?
