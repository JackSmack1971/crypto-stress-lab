# Execution, evidence and failure branches

Read when dependencies are nonlocal, failure attribution is uncertain, or resources have meaningful side effects.

| Condition | Mandatory response |
|---|---|
| Existing test fails before change | Preserve baseline evidence; attribute failure only after comparing unchanged and changed behavior |
| Required local service/tool absent | Inspect supported setup; use authorized local alternative if semantically adequate; otherwise mark blocked or not tested |
| Shared/staging/prod endpoint or real credentials required | Check task authorization and project policy; without approval do not connect; use local isolated substitute or report block |
| Fixture disagrees with schema / API version | Determine authoritative contract; do not silently edit fixture or generated source; report unresolved drift |
| Flaky result or test times out | Collect seeded inputs, timing, logs and correlation IDs; rerun boundedly for diagnosis, not to cherry-pick a pass; report instability |
| Retry/queue delivery fails intermittently | Inspect deduplication, ack/nack, visibility timeout and exact side effects; correlate by message ID without leaking sensitive payloads |
| Partial write or crash | Verify persisted state, rollback/compensation and cleanup; do not infer atomicity from an error response |
| Cleanup cannot be confirmed | Mark incomplete, provide resource identifiers without secrets; don't claim isolation passed |
| Test would mutate external/shared state | Stop pending explicit authorization and cleanup plan; prefer reversible isolated fixture |
| Only mocked adapters pass | Distinguish adapter-unit evidence from genuine cross-boundary integration evidence |
| Repository check fails outside scope | Report whether pre-existing, unrelated, or unresolved; preserve failures and code; avoid opportunistic refactors |
| Permission or architecture contradicts proposed approach | Respect higher-priority policy, report conflict and alternative; do not bypass guards |

Use an environment label such as `local-ephemeral`, `local-simulated`, `authorized-sandbox`, or `shared` in reports. Sanitize logs and fixtures; never publish tokens or customer data. For mutable integration fixtures, use unique test identifiers and a teardown that can safely run again. If exact cleanup is impossible, request permission before creating the resource.

Evidence chain: **contract → actual exercise → observed effect → independent assertion → recorded outcome**. Failure must remain visible even when another path passes. Stop after a validated relevant result plus any required repository checks; additional sweeping is evidence-driven, not automatic.
