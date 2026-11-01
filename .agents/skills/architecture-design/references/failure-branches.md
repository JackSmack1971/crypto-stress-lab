# Failure and autonomy branches

| Condition | Required response |
| --- | --- |
| Expected repository file, spec, or tool absent | Inspect nearby authoritative evidence; record gap; do not invent contract or command. Block if decisive. |
| Repository architecture contradicts stale documentation | Show both sources and their dates/paths; determine explicit priority; otherwise report unresolved authority conflict. |
| Worktree has overlapping uncommitted changes | Treat as current user work; do not overwrite or reset; limit investigation and flag decision impact. |
| Tests or experiments already fail | Establish baseline if safe/available; distinguish pre-existing failures from proposed validation; never count a proposed check as passed. |
| Feasible options all violate a hard constraint | Mark BLOCKED; expose the conflicting constraint and necessary owner tradeoff. |
| Key workload, performance, cost, or threat assumption lacks evidence | State hypothesis and a bounded falsification/measurement plan; conditional recommendation only if outcome-sensitive. |
| Source and generated artifacts differ | Find generation authority and reproducible process; do not manually alter generated outputs or assume either is correct. |
| Interface consumers or migration inventory incomplete | Report coverage gap and scope boundary; no implementation-ready status for impacted contracts. |
| Destructive migration or irreversible data/contract change | Prefer staged/reversible option; require owner approval and verified recovery/rollback plan before execution. |
| External deployment, account, infrastructure, privacy or security action needed | Architecture analysis is read-only; separate authorization and relevant verification are required before action. |
| Independent agent disagrees or tool results conflict | Reconcile against primary evidence; report unresolved disagreement, not majority vote. |
| Proposed validation unavailable or inconclusive | Distinguish unverified design hypothesis from verified current behavior; report blocked/conditional status accordingly. |
| Scope expands beyond requested decision | Record dependency and stop at the agreed boundary; propose a follow-on decision separately. |
