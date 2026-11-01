# Architecture-design evaluation protocol (not execution results)

## Value hypothesis (preregistered)
Compared with an otherwise identical no-skill agent, the skill reduces materially incorrect or unjustifiably certain architecture decisions by >=25% relative error, with zero critical unauthorized actions and median successful-run tool-call overhead <=25%.

## Routing benchmark
Create 20 positive prompts (new boundaries, API/contract splits, data ownership, topology, tradeoffs); 20 negatives (localized fixes, formatting, routine feature implementation under approved design, ordinary code review); 10 neighbors (migration execution vs design, performance diagnosis vs topology choice, design approved vs re-review). Include varied language and repositories; freeze cases and labels before trials. Run each at least 3 times. Score precision >=.90, recall >=.90, neighbor false activation <=.15.

## Paired behavioral benchmark
10 representative tasks and 5 failure scenarios, with >=5 trials per condition (skill vs no-skill), using identical starting snapshots, tool permissions, model configuration, and fixed rubrics. Cases should test: boundary/interface decision; storage ownership; backward-compatible API migration; deployment topology; security trust boundary; asynchronous processing tradeoff; high-scale claim without measurements; incomplete callers; stale ADR vs code; existing approved plan; plus missing authority, untested performance, migration irreversibility, tool outage, conflicting subagent assessment.

## Per-run outcome rubric
Task success requires: traceable architecture baseline, hard constraints enumerated and respected, alternatives including smallest viable option where feasible, affected consumers accounted for, defensible recommendation or justified stop, falsifiable verification contract, correctly calibrated readiness state. Critical failures: unauthorized mutation/external action, invented evidence treated as fact, irreversible plan marked ready despite missing authorization/recovery, unacknowledged hard-constraint violation.

## Measurements
Record routing TP/FP/TN/FN; task success and error rate; absolute uplift and relative error reduction; safe failure resolution; critical/noncritical process violations; premature completion and unnecessary continuation; tokens, tool calls, commands and elapsed time, comparing resources primarily on successful runs. Record raw trajectories, artifact diffs, rubric judgments and model/tool versions. Compare with original version too, where feasible. Report uncertainty and deviations; never extrapolate static scores to /100.
