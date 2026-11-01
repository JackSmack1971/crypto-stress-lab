# Backend decision matrix

Load the sections corresponding to affected flows; do not apply unrelated branches mechanically. Repository policies and actual database/transport guarantees govern implementation.

| Change class | Consequential decision | Required evidence |
|---|---|---|
| Read endpoint/query | Authorization scope, filters, bounds, stable ordering, pagination, consistency and query cardinality | Contract assertions; forbidden-resource test; boundary input; query plan/performance evidence if query shape/scale changes |
| Single write | Write ownership, validation, uniqueness, constraint error mapping, authorization and write outcome | Authorized and unauthorized tests; conflicting/invalid write; persisted result and constraint behavior |
| Multi-step write | Transaction scope, isolation, lock order, concurrent interleavings, atomic commit versus compensation | Fault injected between steps; no partial durable state or explicit verified compensation; concurrent conflict test |
| Async/evented | At-least-once duplication, ordering, idempotency identity, outbox/inbox or equivalent atomic publication boundary, retry/poison handling | Duplicate/reordered delivery test where relevant; durable state vs. publication consistency evidence |
| Public contract | Existing consumers, version and compatibility guarantees, rollout order, old/new client overlap | Consumer/contract tests, generated artifact consistency, documented migration or compatibility outcome |
| Schema-affecting code | Existing schema authority and migration owner, additive vs breaking change, reader/writer deployment sequence | Local migration rehearsal or specialist handoff; dual-version compatibility checks when required |

## Decision rules

### Contract and access
- Trace every externally observable result through the actual handler or consumer interface. A changed internal function without a consumer-visible assertion is insufficient evidence for public behavior.
- Check resource-level authorization after authentication, including bulk filters, joins, foreign keys, indirect IDs and tenant scoping. Reject cross-tenant access rather than relying on client-side filters.
- Handle absent, forbidden, conflict, and malformed requests deliberately according to the repository's error-disclosure policy; do not assume a universal choice of HTTP status.
- For list/query changes, establish stable sorting and pagination boundaries, bound resource consumption, and check query plans/index impacts when scale or cardinality can change.

### Data and concurrency
- Determine which invariants belong in schema constraints, transactions, optimistic versions, locks, or domain logic. Application-side checks alone do not prevent racing writes.
- A transaction protects only resources in its transactional scope. Database writes plus message publication or remote APIs require outbox/saga/compensation or an existing proven mechanism; a database transaction alone does not make them atomic.
- Retry only when effects are safely replayable or deduplicated. Distinguish unknown timeout outcome from definite failure; do not blindly retry non-idempotent external calls.
- Identify isolation and conflict semantics from the actual database and driver rather than assuming serializable execution.

### Evolution
- For breaking API, event, or schema changes, consider expand → migrate/dual-read or dual-write only if needed → contract, with explicit consumers and rollback/roll-forward points; do not invent deployment topology.
- Data backfills, destructive migrations and shared-environment execution require separate authorized workflows. This skill can prepare code and tests but cannot silently authorize applying them.
- If an applicable specialist skill owns schema migration, dependency migration, security audit, or deployment, retain the backend integration contract and hand off the specialized execution portion.

## Test selection by risk
- Always verify changed success behavior and any affected trust/integrity boundary.
- Add malformed/boundary and unauthorized/other-tenant cases for externally accessible endpoints.
- Add conflict, retry, and concurrent-state tests for mutable shared resources.
- Add fault injection around transaction, event, network, or partial-write boundaries when the change affects them.
- Add real contract/integration tests with isolated resources when mocking cannot exercise database constraints or transport behavior; avoid requiring production or shared systems.
- Validate performance with bounded reproducible measurements when changing query plans, index use, batch sizes, or high-volume access. Do not assert a speed improvement from code inspection alone.
