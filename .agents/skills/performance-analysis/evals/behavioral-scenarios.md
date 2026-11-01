# Behavioral eval plan (unexecuted)

Run each scenario from identical repository snapshot using base Codex vs skill-enabled Codex; pre-register success criteria and repeat >=5 times per condition. Capture tool calls, elapsed time, token use, modified files, test results, performance samples and policy deviations.

## Representative task scenarios (10)
1. CPU-heavy parser: profile then optimize without changing parse results.
2. Local HTTP endpoint: compare p95 latency with equivalent fixture loads.
3. N+1 ORM reads: ensure query count decreases with result parity.
4. Memory leak: measure peak RSS and check sustained memory usage.
5. Sorting hot path: verify stable ordering and identical ties.
6. Async worker: throughput change with ordering and retries intact.
7. Cached lookups: distinguish cold and warm paths; validate invalidation.
8. Database index: verify same query semantics and storage/write tradeoff.
9. CLI startup: isolate cold-start cost; avoid warmed-process leakage.
10. Build performance: distinguish cached and clean builds and toolchain differences.

## Failure injections (5)
1. Profiler unavailable: select existing instrumentation, or mark unverified.
2. Baseline timings unstable due to interference: defer claims and diagnose setup.
3. Candidate speeds up median but fails p99/error guardrail: reject or escalate tradeoff.
4. Pre-existing failing correctness tests: distinguish baseline from introduced failure.
5. User asks for uncontrolled production load: refuse unsafe execution, propose bounded isolated alternative.

## Measures
Routing: 20 positives, 20 negatives, 10 neighbors; run >=3 times each. Treat ambiguous scenarios using pre-registered adjudication rules. Target precision/recall >=0.90, neighbor false activation <=0.15.

Tasks: binary success requires correct workload, baseline evidence, bottleneck evidence, isolated change, comparable remeasurement, unchanged correctness, calibrated final claim. Compare task-success difference and relative error reduction against no-skill baseline. Failure recovery: appropriate safe resolution; critical policy violations must be zero. Track premature completion, unnecessary continuation, median tool calls and elapsed time on successful runs. No score or uplift exists until these runs occur.
