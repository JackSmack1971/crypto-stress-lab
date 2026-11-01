# Coordination decisions and failure contract

These rules apply when multiple specialist workflows share a task. They **do not** implement a native Codex scheduler, enforce locks, confer permission, or guarantee subagent availability. Applicable repository instructions and explicit user constraints prevail; do not replace stronger local policy.

## Decide whether to coordinate

- **Yes:** independent workstreams with integration dependencies; distinct implementation and review owners; cross-domain changes that require multiple verification disciplines; resumption of a partially completed multi-stage task.
- **No:** a single bounded edit, standalone bug diagnosis, one audit, one documentation update, simple planning, or a request already fully owned by another skill. Do not spawn a coordinator to merely route a simple task.
- **Ambiguous:** map the work and start with the narrowest owner. Introduce coordination only after identifying a real handoff, conflicting ownership, or dependent gate.

## Risk and autonomy

| Tier | Operational criterion | Minimum control |
|---|---|---|
| L0 | Read-only interpretation or exploration | Evidence provenance, no write authority |
| L1 | Reversible, scoped local modification | Baseline, single writing owner, focused verification |
| L2 | Cross-domain/interface change, broad regression surface or externally visible implementation | Dependency gates, fresh integrated diff, independent review when available; disclose absent independence |
| L3 | Destructive/security-critical, production-facing, irreversible, migration/infrastructure, or sensitive-data operation | Explicit operation-specific authorization, bounded blast radius, failure/rollback plan where feasible, independent verification, stop on uncertainty |

Choose the higher tier if uncertain; a project-specific risk policy may be stricter. Human approval remains mandatory wherever required, even if a subagent recommends proceeding. A tier is not an authorization token.

## Dependency graph, not a mandatory parade

Build a directed acyclic graph of **required outputs** rather than invoking a fixed roster. Common optional responsibilities: state reconnaissance, requirements resolution, architecture decisions, frontend/backend implementation, migration management, failure analysis, focused tests, integration, security review, performance profiling, documentation synchronization, independent verification, and release assessment. Use only roles whose output changes a consequential choice. A node is ready only if its prerequisite artifacts and approvals exist. Never use review/test as a substitute for implementation, or documentation as proof of behavior.

For each node specify: owner, inputs + revision, owned path/interface set, output, testable acceptance, dependent nodes, write permission, and whether concurrency is safe. Avoid parallel writes to overlapping files, shared generated artifacts, migrations, or common configuration. If separate worktrees exist, verify branch and merge boundaries; separate worktrees do not make integration automatic. Read-only subagent assertions are advisory unless the tool/sandbox enforces them.

## Handoff and evidence

A project-provided ledger is authoritative when it is compatible with applicable instructions. Otherwise follow `references/handoff-schema.md`. The coordinator validates that recorded commands actually ran, exit codes and outputs are known, changed paths match current diffs, and checked revision corresponds to the reported artifact. `NOT_RUN`, missing evidence and unknown state are not `PASS`.

A review is independent only if a distinct reviewer actually assessed the current change without substituting the implementer's self-assessment. If independent tools are unavailable, record `INDEPENDENCE_UNAVAILABLE`, perform available checks, and avoid claiming the independent gate passed. Where independent review is mandatory, stop short of COMPLETE.

### Revision identity

A Git SHA alone is insufficient for dirty worktrees: note staged/unstaged/untracked changes and file identities (or a task-scoped diff fingerprint) when needed. Recheck before handoff, after integration, after compaction/resume and after repair. Do not overwrite a collaborator's work from a stale snapshot. Re-run checks invalidated by edits to tested code, fixtures, configuration or generated outputs. For non-Git workspaces, use a comparable explicit snapshot or mark revision confidence reduced.

## Failure decision table

| Divergence | Required response |
|---|---|
| Required skill/agent missing | Use available owner or direct workflow; document reduced role separation; do not fabricate agent execution |
| Tool/check missing or broken | Seek valid alternate verification if permitted; record exact gap; fail required gate if no substitute demonstrates it |
| Pre-existing failure | Establish baseline and attribution; do not claim a new regression without evidence or hide an introduced failure as pre-existing |
| Stale handoff or changed revision | Stop reuse; inspect current diff and revalidate invalidated dependent work |
| Concurrent ownership conflict | Freeze overlapping writes; serialize or isolate, then reconcile source and generated files |
| Conflict with architecture or user scope | Surface decision and consequences; do not silently choose high-impact architecture |
| Missing authorization, permission denial or credential | Stop that operation; never route around the denial via another tool or agent |
| External write interrupted/unknown | Inspect downstream state read-only before any retry; do not assume idempotency |
| Secret/privacy exposure | Stop dissemination; minimize records, redact secrets, follow project incident policy |
| Required review/check inconclusive | Keep nonterminal state; describe uncertainty and feasible next verification |
| Review cap exhausted | Stop with material findings and remaining owner decisions; no unbounded repair |
| Context loss/long-running resume | Reconstruct from current repository plus evidence ledger; do not trust remembered approvals or stale completed checks |

## Lifecycle and termination

`NEW -> SCOPED -> IMPLEMENTING -> VALIDATING -> REVIEWING -> COMPLETE` is a normal path, not a rigid stage requirement. `PARTIAL` means useful output exists but required proof is absent; `BLOCKED` means dependency, decision or authority prevents safe advance; `FAILED` means attempted operation failed; `CANCELLED` means explicit cancellation. Transitions to COMPLETE require current-revision checks and applicable review gates. Halt when work exceeds the authorized task, acceptance is satisfied, or further steps would be speculative. Distinguish attempted work, observed results and independently verified results in the final handoff.
