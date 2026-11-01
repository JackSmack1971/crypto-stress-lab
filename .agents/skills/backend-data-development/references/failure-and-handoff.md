# Failure response and workflow handoff

Use this file only when a divergence or higher-risk handoff is encountered.

| Observation | Response | Evidence to report |
|---|---|---|
| Existing tests fail before edits | Capture baseline or comparable evidence, separate pre-existing from introduced failures; do not alter unrelated tests to mask failures | Commands, failing tests, before/after comparison |
| Tests fail after edit | Narrow the failure; repair within active scope, or stop with a concrete blocker | Failing assertion, changed behavior, final rerun result |
| Database/service/test dependency unavailable | Run safe focused checks and document missing integration evidence; do not substitute fake success | Exact unavailable check and why it matters |
| Contract/schema docs disagree with implementation | Identify authority, inspect callers and executable behavior; request a compatibility decision if unresolved | Contradictory artifacts and affected consumers |
| Generated client/schema mismatch | Modify authoritative source and regenerate using repository-supported tooling; otherwise stop at unverified | Generator invocation and resulting diff/check |
| Need schema migration or backfill | Determine whether dedicated schema-migration workflow exists; prepare compatibility requirements, do not execute shared migrations without explicit authorization | Migration owner, rollout requirement, local-only rehearsal if possible |
| Cross-service write or event publish can partially fail | Choose verified existing atomicity/compensation mechanism or mark design blocked | Fault-injection or recovery evidence |
| Possible data disclosure or missing tenant authorization | Stop risky outward action, close access gap with scoped tests; escalate when authority/policy is unclear | Negative access test, inspected logging/output surfaces |
| Risk of destructive/shared data mutation | Do not run operation; obtain explicit scope and approval, backup/rollback or forward recovery plan, and rehearsal evidence | Authorization boundary and missing prerequisites |
| Requested architecture conflicts with current repository | Identify contradiction and consequence; implement reversible compatible subset only if independent and authorized | Source of conflict, decision required, scope held |
| Requested verification exceeds permissions/time/resources | Run available relevant checks; report unfinished proof and do not claim passed | Checks attempted, blocked, not run |

**Handoff packet:** describe affected contract and consumers; data model/invariant; current vs desired state; compatibility and rollback/roll-forward concerns; actual evidence; unresolved decisions. Avoid proposing tools or commands not present in the repository.
