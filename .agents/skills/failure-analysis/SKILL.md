---
name: failure-analysis
description: Investigate reproducible, intermittent, or environment-specific software failures to establish an evidence-backed root cause and, when authorized, verify a minimal repair. Use for failing tests, runtime crashes, regressions, and unexplained incorrect behavior. Do not use for routine implementation, speculative code review, or general performance optimization without a concrete failure symptom.
---

# Failure analysis

**Objective:** Explain a concrete observed failure with falsifiable evidence; repair it only when authorized. The skill confers no permissions beyond the user request and active repository instructions.

## 1. Establish the observation and boundary

- Record the exact symptom, expected behavior, inputs, failure output, environment, and triggering command when available. Distinguish direct observations from reports or assumptions; avoid reproducing sensitive values in evidence.
- Read applicable `AGENTS.md` instructions and relevant repository/test configuration; inspect Git status and pertinent diffs before making changes. Preserve pre-existing work.
- Determine whether the request is **diagnosis only**, **diagnosis plus repair**, or **verification of a claimed fix**. For diagnosis-only tasks, operate read-only and propose changes rather than applying them.
- Check reproduction risk before executing commands: avoid writes to live services, destructive migrations, production data, costly external calls, or sensitive-output exposure without appropriate authorization. Prefer isolated fixtures or local replicas.

**Gate:** A bounded failure statement and a safe investigation plan are identifiable. If the symptom or target cannot be established, report the missing evidence rather than inventing it.

## 2. Reproduce and establish baseline

- Run the narrowest safe reproduction; capture the command, relevant environment, exit status, and decisive output. Check whether the failure is already present in the untouched baseline when this can be established without disturbing existing work.
- For intermittent failures, vary one relevant dimension at a time, record attempts and outcomes, and consider time, ordering, concurrency, caches, resource limits, platform, or external dependencies. A passing attempt does not disprove an intermittent failure.
- If reproduction fails, attempt bounded alternative evidence (logs, existing failing CI trace, isolated fixtures, environment comparison). State **not reproduced** and the confidence limit; do not label a root cause confirmed solely from speculation.

**Gate:** Reproduction or alternative evidence is recorded with provenance; baseline status is known or explicitly unknown.

## 3. Discriminate causal hypotheses

- Trace the path from trigger to first meaningful divergence. Separate the **proximate failure mechanism** from the **underlying cause**, including missing invariants or upstream defects.
- Generate competing hypotheses only where ambiguity exists; do not invent a second hypothesis when direct evidence is decisive. For each live hypothesis, record a prediction that would distinguish it from alternatives.
- Choose the least invasive high-information test (targeted instrumentation, boundary input, controlled toggle, code/data comparison). Correlation, stack-frame location, and symptom disappearance alone do not prove causation.
- Prefer evidence that falsifies alternatives and demonstrates the causal link. Preserve diagnostic output without secrets. If evidence conflicts, revise the hypothesis or stop with explicit uncertainty.

**Gate:** Mark the cause **confirmed** only when the mechanism is explained and supported by a discriminating observation; otherwise mark **probable** or **unresolved**, with next tests.

## 4. Repair when authorized

- Change the smallest coherent cause-bearing surface, following repository patterns. Do not mask symptoms by weakening assertions, skipping tests, suppressing exceptions, or broadly refactoring unrelated code.
- Where feasible, obtain a regression demonstration that fails before the fix and passes afterward. If a red baseline cannot be safely recreated, identify alternate independent evidence and clearly label the limitation.
- Keep diagnostic instrumentation temporary and restore it without disturbing user changes. If the necessary change conflicts with architecture, requires credentials/permissions, or has significant external or irreversible effects, stop for a decision.

**Gate:** The fix is traceable to the diagnosed mechanism; no unrelated modification is included.

## 5. Verify, classify, and stop

- Run the focused regression and nearest relevant tests; broaden checks when blast radius, touched interfaces, or findings justify them. Compare against any known pre-existing failures; do not attribute unrelated failures to the repair.
- Examine the final diff, test behavior, exit codes, and relevant runtime behavior. If feasible, perform an independent check that can disprove the proposed correction, not just repeat the change command.
- Do not claim a verified fix when tests were not run, evidence is inconclusive, reproduction remains uncertain, or external behavior could not be observed. Stop after sufficient evidence; avoid further speculative changes.
- Report using `references/root-cause-report.md`. Load that template when preparing the final report; include precise evidence, confidence, verification, files changed, and unresolved blockers.

**Completion:** An evidence-backed diagnosis is delivered; if repair was authorized, the minimal change and available independent verification are reported accurately. Otherwise stop with an explicit inconclusive result and a discriminating next step.
