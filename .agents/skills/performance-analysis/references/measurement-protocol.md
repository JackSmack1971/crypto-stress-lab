# Measurement and decision reference

Read when defining a baseline, interpreting variable measurements, or deciding whether a candidate optimization is supported.

## Establish the experiment

- Specify operation and workload mix (including input cardinality, distributions and warm/hot/cold cache state); decide whether a microbenchmark, end-to-end workload, or both is needed. Protect representative data.
- Identify primary metric, unit, improvement direction, target if authorized, and guardrails such as correctness, p95/p99 latency, peak RSS, allocation count, throughput, CPU and error rate. Do not optimize an aggregate that conceals important tail failures.
- Fix or record runtime/compiler versions, OS, hardware, CPU scaling/power plan, thread count, dependency versions, build optimizations, external services, warmed caches and configuration. Warm up JITs and caches as appropriate; keep warm and cold scenarios separate.
- Prefer in-repository fixtures and harnesses. Assess baseline variability before making changes. Use repeated independent trials; avoid treating loop iterations within one process as independent runs. For very short operations, batch work and amortize measurement overhead, then report per-operation units.
- Interleave or randomize baseline/candidate executions when feasible to reduce temporal drift. For dependent benchmarks, pair observations by workload/case and repeat index; always record order. Do not discard outliers simply because they disfavor an optimization. Predefine exclusions such as machine interruptions and retain excluded raw data with reasons.

## Interpret improvement

- Compare distributions, not only the fastest result. Report sample counts, medians and dispersion. Estimate uncertainty using an appropriate method; a bootstrap interval is descriptive, not a license to ignore systematic bias or autocorrelation.
- `scripts/compare_benchmarks.py` requires matching case/run identifiers and computes a deterministic paired-bootstrap confidence interval for median per-pair relative improvement. It assumes pairs are independently sampled. It rejects invalid/mismatched CSVs. A positive interval is evidence under those assumptions, *not* proof that the entire application improved.
- Set a practical gain threshold from the user's goal, baseline variability and measurement cost before interpreting results. If none was defined, report the estimated effect and uncertainty without post-hoc claiming meaningful improvement.
- Evidence to **KEEP**: the workload is representative; reproducible comparisons show an improvement that satisfies the predefined objective; no relevant correctness/guardrail regression; no new unapproved architectural or operational cost.
- **REJECT** when behavior regresses, critical guardrails fail, or results show the candidate does not meet the required target. **INCONCLUSIVE** when uncertainty, missing baselines, drift, unavailable tools or weak coverage prevent a supported decision. Do not force a positive answer.
- If a speed gain trades memory, energy, complexity, reliability, or tail latency, state the tradeoff and obtain a decision where no agreed priority exists.

## Suggested paired CSV contract

One CSV per revision with header `case,run,value`, example:

```csv
case,run,value
search_1000,1,12.1
search_1000,2,11.8
search_1000,3,12.0
```

Values must be finite, positive numeric measurements in identical units. Pair rows on `case` and `run`; do not equate different workloads. Measure at least five independent pairs per case for this helper. Keep raw files and command/environment metadata next to them. The script reports each case separately and avoids averaging incomparable workloads.

Example:

```sh
python scripts/compare_benchmarks.py baseline.csv candidate.csv --direction lower --min-gain 0.05
```

Exit codes: `0` = supported threshold on all cases, `1` = not supported or inconclusive, `2` = malformed input. A script PASS does not override correctness checks, unsafe load, workload mismatch, or causal ambiguity.
