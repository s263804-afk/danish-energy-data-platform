# S6 — Explain the query contract

Learning status: material prepared; personal practice pending.

Workplace purpose: Explain the query contract.

Read the actual path: api.py checked_request → bound SQL → signed cursor → response.
See the corresponding tests and saved completion logs.

Five terms (including two verb phrases): endpoint; readiness; cursor; validate against; expose an endpoint.

Run: python -m pytest -v --tb=short. Observe the real result and compare with the task's known-answer tests.

Personal exercise: Change page size from two to three and show the pages contain no repeated UTC instant.

60–90-second practice script:

This task helps me explain how the energy data platform works. Its focus is: explain the query contract. I start from a documented input and follow the actual code path. I compare the observed result with an expected value, rather than treating a successful command as proof of every feature. The project keeps original source bytes, current values and run evidence so that a result can be traced back. Its tests include normal inputs and deliberately controlled failures. These tests run against PostgreSQL where database behaviour matters. I still need to perform the personal exercise and explain its result independently. AI-assisted implementation and my own demonstrated understanding are recorded separately. The next improvement should be chosen from an observed limitation, with a test that shows the intended behaviour.

Use first-person accomplishment claims only after performing the action personally.

Questions:
1. Why does health differ from ready?
2. What returns 422?
3. Why bind SQL parameters?
