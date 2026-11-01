---
name: regression-testing
description: "Select, run, and assess change-focused regression tests when a code fix or feature needs evidence that intended behavior works without breaking existing contracts. Use for regression risk assessment, reproducing a fixed defect, or verifying impacted behavior across boundaries. Not for writing a whole test harness, general test-suite setup, performance benchmarking, or independent code review."
---

# Regression testing

**Workflow:** Establish whether a specific change preserves relevant existing behavior while satisfying its new or corrected contract. This skill supplies no new authorization to edit, deploy, or use external services. Follow repository `AGENTS.md` and existing test conventions.

## 1. Bound the change and evidence

- Inspect relevant diff, status, impacted callers/contracts, tests, and available verification commands. Preserve unrelated working-tree changes.
- Identify each changed behavior, existing invariant at risk, and acceptance criterion. Derive risk from observable change surface (public API, persisted data, concurrency, security, integrations, error paths), not changed-line count alone.
- Select the smallest credible regression set: direct behavioral tests, at-risk integration boundaries, and broader checks only when coupling, failed evidence, or repository policy warrants them. Do not treat coverage percentage or a green broad suite alone as proof of relevant behavior.
- Use `references/selection-and-failures.md` when choosing scope or classifying uncertain failures. Use `references/test-matrix.md` for the evidence matrix.

## 2. Establish a trustworthy baseline

- For defect fixes, prefer a focused reproducer that demonstrates the original defect on the pre-fix implementation, then passes after the fix. Test against the old implementation only when the comparison is safe and feasible without disturbing user changes; otherwise record baseline **not established** and why. Never revert or overwrite unrelated edits to obtain a baseline.
- For other changes, capture relevant pre-change results when available; if unavailable, distinguish unobserved baseline from evidence of a clean baseline.
- Require a regression test to fail for the intended *behavioral* reason, not an import error, missing fixture, configuration issue, or unrelated assertion. Existing appropriate tests can be reused rather than duplicated.

## 3. Exercise the risk surface

- Map each relevant contract to a positive case, meaningful rejection/error case, and boundary or transition case **where applicable**. Prefer discriminating assertions about outputs, side effects, persistent state, sequencing, and contract preservation; avoid tests that merely confirm code executes.
- Check integration edges and state transitions proportionately to impact. Do not create artificial negative cases when the contract has none; explain the omission.
- Use existing test runner and project setup. Do not introduce a dependency or new harness merely to run regression tests. Do not weaken/delete assertions, manipulate skip markers, alter unrelated imports, or update snapshots blindly to make results green.
- If tests or fixtures must change, keep edits limited to the requested scope, and inspect the diff for assertion weakening and unintended artifacts.

## 4. Observe, diagnose, and calibrate

- Record **exact executed commands**, exit status, counts when available, and relevant failing test identities. A command attempted without observable results is **inconclusive**, not passed.
- Distinguish `passed`, `failed`, `blocked`, and `not_run`. Classify failures as introduced, pre-existing (with comparable evidence), flaky (with reproduction evidence), environmental, or unresolved. Do not label a failure pre-existing or flaky from intuition alone.
- Rerun a suspect test with controlled inputs and inspect causal evidence; retries may diagnose nondeterminism but must not erase an initial failure. If failures involve new behavior, fix within authorized task scope and rerun affected checks; otherwise surface the blocker.
- For absent infrastructure, unavailable commands, missing secrets, unsafe external side effects, or inconclusive tests: seek an authorized local alternative or report a coverage gap. Do not make production calls, alter CI policy, relax safety checks, or initiate deployments without separate authorization.

## 5. Verify and stop

- Independently compare observed results to expected contracts and inspect test/code diff. Each relevant contract must have a passing check or explicitly reported gap; no unexplained failures or misleading success claims.
- If producing a machine-readable evidence manifest, use `references/evidence-record.md`; optionally run `python scripts/validate_evidence.py path/to/evidence.json` to check record consistency. This validates **record structure**, not whether testing was sufficient or correct.
- Stop after sufficient evidence for the scoped change, or when further verification is blocked or requires new authorization. Do not broaden the suite by default after a supported conclusion.

**Report:** impact/risk boundary; test matrix; actual commands and outcomes; baseline status; failures and classification evidence; coverage gaps; conclusion `verified`, `not_verified`, or `inconclusive` with reasons. `verified` requires observed passing evidence for all required contracts and no unresolved relevant failures.
