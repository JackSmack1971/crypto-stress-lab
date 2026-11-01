---
name: performance-analysis
description: "Diagnose and improve measured software performance regressions or bottlenecks using representative baselines, profiling, controlled changes, and repeatable benchmarks. Use for requests to reduce latency, CPU/memory use, allocations, or improve throughput in a repository. Not for general code cleanup, speculative micro-optimizations, capacity planning without executable workloads, or production load testing."
---

# Performance analysis

This skill exists to diagnose and improve a software performance bottleneck when a user requests measured optimization or regression investigation. It grants no execution, deployment, or load-testing authority beyond the user's request and repository rules.

## Decision protocol

1. **Frame the performance contract.** Identify the operation, representative workload and scale, primary metric (units and improvement direction), correctness invariants, environment and resource constraints. Establish a targeted performance objective if the user provides one; otherwise define the comparison as exploratory and do not invent an acceptance threshold. If the operation cannot be exercised, give an evidence-limited diagnostic rather than claiming speedup.
2. **Inspect before measuring.** Read applicable `AGENTS.md`, relevant code, existing benchmarks/tests, configuration, Git status/diff, and prior measurements. Preserve unrelated work. Identify whether the complaint reflects an observed regression, a suspected bottleneck, or a scaling hypothesis. Select a reproducible workload that exercises the actual slow path. See `references/measurement-protocol.md` for measurement design, comparability, and statistical treatment.
3. **Baseline first.** Run or reuse a trustworthy baseline against an identifiable revision with workload inputs, hardware/runtime/configuration, measurement command, repetitions, warmups and raw observations captured. If variance, environment drift, interference or a known test failure undermines the baseline, repair the method or stop with an inconclusive diagnosis. Do not interpret a single timing as a reliable difference.
4. **Find a causal candidate.** Profile or instrument the target under representative load; use the cheapest adequate tool already supported by the repository. Attribute cost to a code path with observed evidence. Avoid rewriting code based only on superficial complexity. Where a profiler is unavailable, use scoped timing or other observable traces and label the lower confidence.
5. **Change the smallest isolated factor.** Preserve behavior, contracts, concurrency guarantees, data ordering, numerical correctness and failure semantics. Prefer reversible local changes. Do not alter benchmarks, workloads, sampling or correctness assertions to manufacture a gain. Record why the change should affect the measured bottleneck.
6. **Compare fairly.** Repeat baseline and candidate under comparable conditions, ideally in interleaved or randomized order with warmups and independent samples. Keep machine, inputs, configuration, concurrency, caches, build mode and external dependency state consistent or report discrepancies. Use `scripts/compare_benchmarks.py` when paired CSV observations are available; its estimates support judgment but do not prove causality. Check tail latency, allocation/memory or throughput tradeoffs where consequential. Use `references/measurement-protocol.md` for the acceptance gate.
7. **Verify and decide.** Run focused correctness tests plus applicable repository checks. Reject or revert *only the optimization introduced in this run* if correctness fails, a guardrail regresses materially, or a claimed gain is not robust enough for the stated objective; preserve pre-existing changes. If results are ambiguous, report inconclusive and do not claim success. Never substitute a successful command invocation for an observed result.
8. **Stop at sufficient evidence.** Deliver the smallest validated improvement, or a reproducible diagnostic and explicit blocker. Do not expand into unrelated refactoring or repeated tuning once the defined goal and checks are satisfied.

## Autonomy and failure boundaries

- No uncontrolled load against production/shared services; obtain explicit authorization and an agreed safe load envelope before any externally consequential benchmark. Default to local/fixture/staging workloads. Respect confidentiality and avoid including secrets or sensitive payloads in benchmark artifacts.
- Tool, profiler, benchmark, or data unavailable: use a justified alternate measurement method or mark the result unverified. Do not install tools or change machine-wide configuration merely to satisfy the workflow.
- Pre-existing failures: record the failing baseline and separate them from new failures. Conflicting source/generated artifacts or architecture constraints: inspect the authoritative source; do not directly edit generated files or override constraints.
- Shared-state contention, unstable performance, or missing comparability: stop short of a performance claim. For wide-blast-radius behavior changes, require an appropriately isolated environment and stronger verification before proceeding.
- A `performance_engineer` subagent, if actually available, may propose benchmarks or review bottleneck evidence; no agent name implies that a command ran, and independent checks remain necessary.

## Completion evidence

Report the target operation, metric/direction, workload, revision and environment, exact measurement method, raw samples or reproducible artifact path, baseline and candidate summaries, uncertainty/variance, change and mechanism, correctness and regression checks with actual outcomes, and a **KEEP / REJECT / INCONCLUSIVE** decision. Distinguish measured facts from inference and list unmeasured tradeoffs. Never claim production throughput or latency from a synthetic benchmark alone.
