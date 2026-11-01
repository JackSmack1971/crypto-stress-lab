# Choosing the real boundary

Use this reference only where the change crosses the corresponding boundary. A test is not an integration test merely because two mock objects interact.

| Boundary | Keep real in the selected slice | Possible outside substitute | Independent observation |
|---|---|---|---|
| HTTP/RPC client ↔ service | Client serialization, transport adapter, routing/handler and response deserialization as applicable | External upstream beyond the service | Wire-level status, headers and body as consumed by the real client; propagated failures |
| Application ↔ database | Real query layer/driver and engine with compatible semantics | External services supplying fixture input | Committed rows, constraints, transaction rollback and read-after-write |
| Producer ↔ queue ↔ consumer | Message encoder, broker behavior or faithful locally supported broker, and consumer decoder where targeted | Downstream side effects beyond consumer | Delivered payload, ack/retry/dead-letter state, duplicate effects |
| Component ↔ filesystem | Actual persistence APIs and file encoding | Remote cloud storage | Contents, atomicity, permissions and cleanup |
| Cross-process coordination | Actual IPC/process boundary and lifecycle | Unrelated external services | Correlated events, timing/order, exit state |

Selection rules:

- Use an ephemeral real dependency (database or broker) if its semantics determine the behavior, and a supported harness exists. An in-memory stand-in is **not** evidence for transaction isolation, lock behavior, broker delivery semantics, or vendor-specific SQL.
- If a real dependency is unavailable, test the nearest observable boundary, mark the omitted semantics `not tested` or `blocked`, and describe required follow-up verification.
- Check versioned contracts against actual supported producer/consumer versions. Record whether backward, forward, or bidirectional compatibility is explicitly required; do not assert both by default.
- For concurrency, make event ordering and final state observable. Prefer deterministic barriers/events and bounded waits to sleeps; repeated green runs alone cannot prove race freedom.
- For retry and idempotency, distinguish at-least-once delivery from exactly-once effects; explicitly test repeated inputs and side-effect count/state when guaranteed.
- For external third-party APIs, use contract fixtures with documented provenance locally unless authorized to query a suitable sandbox; never pass a stub as live compatibility proof.
- For failures spanning several boundaries, choose the narrowest experiment that can differentiate competing root causes; avoid multiplying every dimension into a huge matrix without evidence of value.
