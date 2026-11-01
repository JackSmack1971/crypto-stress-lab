---
name: integration-testing
description: "Design, implement, or diagnose integration tests across module, process, service, database, or message boundaries. Use when a change needs verification of interacting components, protocol contracts, retries, transactions, or failure propagation. Not for isolated unit tests, standalone contract documentation, load benchmarking, or full user-journey E2E testing unless an integration boundary is the actual concern."
---

# Integration testing

This skill exists to verify interactions across component boundaries when independent component tests cannot establish correctness. It grants no new permission to access remote systems or modify persistent state.

## Boundary and evidence selection

1. Read applicable `AGENTS.md`, inspect relevant code, tests, configuration, Git status/diff, and the existing integration harness. Preserve pre-existing changes. Identify the requested behavior and the *actual* boundary crossed; do not fabricate architecture or assume a service is available.
2. Build a compact boundary matrix: producer/consumer, transport or storage boundary, contract and version, relevant invariant, planned observation, isolation/cleanup, and evidence status. Include only boundaries affected by the task plus adjacent ones needed to make failures diagnosable.
3. Prefer the smallest realistic integration slice that exercises the actual adapter, serialization, database access, network protocol, or queue handoff. Fake *outside* the targeted boundary, not the behavior under test. For each substituted dependency state what is real, simulated, and unverified. Consult [boundary selection](references/boundary-selection.md) for database, messaging, HTTP, and distributed cases.
4. Choose normal and consequential failure cases from observed contracts: malformed/versioned payload, null/optional fields, timeout, partial failure, rollback, retry, duplicate, reordering, race, or idempotence **only where applicable**. Define the precise assertion and failure signal before running. Prefer observable postconditions over implementation-call counts. Check both directions of compatibility only when both directions are supported or promised.

## Execution and diagnosis

5. Establish the relevant baseline before editing or attributing a failure to the change. Prefer repository-supported harness/fixtures and scoped commands; do not invent commands. For an existing code change, begin with focused tests, then expand to impacted boundaries and repository-required checks based on risk.
6. Isolate test resources with unique names and controlled setup/teardown. Require explicit authorization before accessing shared/external systems, using production data or credentials, mutating shared schemas, or performing destructive operations. Read [execution and failure branches](references/execution-and-failures.md) whenever a nonlocal dependency, flaky test, cross-process failure, or nontrivial cleanup is involved.
7. Capture command, environment classification, exit code, relevant assertions, and observable resulting state. A command succeeding alone does not prove the intended boundary was exercised. If a test fails, distinguish pre-existing failure, introduced regression, test/harness defect, unavailable dependency, and nondeterminism through independent evidence. Do not weaken assertions or hide flakes to obtain green output.
8. Verify isolation and cleanup. Check the actual resulting state (stored records, emitted messages, client-visible responses, rollback/compensation) separately from the action that produced it. Expand checks only when changed risk or failure evidence warrants it.

## Completion contract

Report the matrix with `verified`, `failed`, `blocked`, or `not tested` per boundary; commands and outcomes; real versus simulated dependencies; baseline attribution; cleanup state; and unresolved risk. Declare **verified** only for boundaries with a passing relevant assertion **and** independent observable evidence in the tested environment. Otherwise report partial or inconclusive validation. Stop once required evidence and repository gates are satisfied; do not claim untested deployment environments are covered.

For a repeatable structured evidence record, use `scripts/check_evidence.py` with the format in [evidence schema](references/evidence-schema.md); this verifies record completeness and consistency, **not** application correctness.
