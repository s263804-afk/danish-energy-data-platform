# S3 — Make imports safe to repeat

Learning status: material prepared; personal practice pending.

Workplace purpose: Make imports safe to repeat.

Read the actual path: cli.py → source.fetch → ingestion.ingest → repository.persist.
See the corresponding tests and saved completion logs.

Five terms (including two verb phrases): idempotency; revision; snapshot; roll back; trace back to.

Run: python -m pytest -v --tb=short. Observe the real result and compare with the task's known-answer tests.

Personal exercise: Run the same saved interval twice, then change one price in a labelled copy and inspect revisions.

60–90-second practice script:

This task helps me explain how the energy data platform works. Its focus is: make imports safe to repeat. I start from a documented input and follow the actual code path. I compare the observed result with an expected value, rather than treating a successful command as proof of every feature. The project keeps original source bytes, current values and run evidence so that a result can be traced back. Its tests include normal inputs and deliberately controlled failures. These tests run against PostgreSQL where database behaviour matters. I still need to perform the personal exercise and explain its result independently. AI-assisted implementation and my own demonstrated understanding are recorded separately. The next improvement should be chosen from an observed limitation, with a test that shows the intended behaviour.

Use first-person accomplishment claims only after performing the action personally.

Questions:
1. What increases on repeat?
2. What creates a revision?
3. Why reject conflicting duplicates?
