# S2 — Give data a reliable identity

Learning status: material prepared; personal practice pending.

Workplace purpose: Give data a reliable identity.

Read the actual path: normalise.py → PriceRecord → migrations/versions/0001_core.py.
See the corresponding tests and saved completion logs.

Five terms (including two verb phrases): primary key; precision; UTC; map to; round to.

Run: python -m pytest -v --tb=short. Observe the real result and compare with the task's known-answer tests.

Personal exercise: Change one synthetic price to NaN and predict rejection before running its unit test.

60–90-second practice script:

This task helps me explain how the energy data platform works. Its focus is: give data a reliable identity. I start from a documented input and follow the actual code path. I compare the observed result with an expected value, rather than treating a successful command as proof of every feature. The project keeps original source bytes, current values and run evidence so that a result can be traced back. Its tests include normal inputs and deliberately controlled failures. These tests run against PostgreSQL where database behaviour matters. I still need to perform the personal exercise and explain its result independently. AI-assisted implementation and my own demonstrated understanding are recorded separately. The next improvement should be chosen from an observed limitation, with a test that shows the intended behaviour.

Use first-person accomplishment claims only after performing the action personally.

Questions:
1. Why use area plus UTC as the key?
2. Why preserve Decimal?
3. What does HALF_EVEN change?
