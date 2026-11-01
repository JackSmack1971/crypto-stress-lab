# Portable classification and handoff reference

Use only if no applicable authoritative repository classification exists. These portable defaults are an explicit skill policy, not an assertion that a repository uses these levels. Repository-specific definitions may differ; retain their terminology and stronger controls. An unverified repository policy is not a reason to guess.

| Level | Decision criterion | Default process |
| --- | --- | --- |
| L0 | Purely informational or mechanical, no project-state edits, no consequential side effects | Answer/check directly; no extra record |
| L1 | Small, reversible, bounded edits in a well-understood surface, with a clear focused verification path | Implement and run focused checks within existing authority |
| L2 | Multi-component or interface changes, difficult rollback, uncertainty that affects design, persistent non-destructive migrations, or material correctness/security exposure | Scoped plan, targeted implementation, focused checks, independent review proportional to impact; obtain required approvals |
| L3 | Production/external mutation with material blast radius, irreversible/destructive data action, credential/authorization boundary changes, or security/privacy consequences not safely contained | Stop consequential action until authorization and explicit impact/rollback or containment/verification gates are established |

## Override rules

1. Take the highest justified level; a small code change can be L3. A hypothetical possibility with no linkage to the actual operation is not sufficient to escalate by itself.
2. A production-facing *code edit* is not automatically a production deployment: distinguish development changes from actual external mutations. Raise to L2 for material product exposure; raise to L3 when an action mutates live state with material blast radius.
3. A migration confined to disposable fixtures can be L1; a persistent compatible schema migration is normally L2; destructive or irreversible real-data migration is L3.
4. Authn/authz, secrets, privacy or security-sensitive changes are at least L2 when they materially affect protections; material exposure or uncontrolled external effects raises to L3.
5. Missing rollback/verification for a high-consequence action requires containment, independent evidence or stop; saying “we can revert Git” does not roll back databases, secrets or external operations.
6. User authorization is scoped: permission to analyze, plan, edit locally, deploy, delete data, merge, or publish are separate. Triage never elevates one into another.
7. If requested execution is unsafe or authority is unclear, classify and identify the required gate; continue with safe read-only/reversible work only if appropriate.

## Routing decision table

| Request condition | Route | Boundary |
| --- | --- | --- |
| Goal not yet testable or competing product interpretations | Specification/decision clarification | No implementation of unresolved consequential choices |
| Known defect with reproducible failing behavior | Diagnosis → smallest fix → regression verification | Do not treat test modification alone as a fix |
| Scoped feature/edit | Implementation → focused checks | Avoid architecture redesign without evidence |
| Persistence/data-model change | Migration workflow → preflight/rollback → verify data and accessors | Treat generated outputs and migrations according to repository policy |
| Security-critical or external operation | Review authorization and containment before action | Do not infer tool access grants permission |
| User requests only review/audit/triage | Report findings/handoff | No unrelated edits or side effects |

## L2/L3 handoff fields

- **Objective / task type:** measurable requested outcome and task category.
- **Evidence:** affected files/systems and what was actually inspected; existing changes and unresolved facts.
- **Level / trigger:** L2 or L3, evidence of each override, provisional flags if necessary.
- **Decision boundary:** dependencies, conflicting readings and who must decide.
- **Workflow / responsible stage:** concrete next stage, optional verified skill/agent, why appropriate.
- **Acceptance / independent verification:** observable product state, focused checks and independent check where justified; distinguish current baseline failures.
- **Authority / consequence:** permission required before side effects, security/privacy constraints and blast radius.
- **Containment / rollback:** feasible recovery or explicit irreversibility; do not assert rollback without mechanism.
- **Stop point / status:** ready for bounded execution, needs decision, blocked, or provisional, with exact next gate.

## Evidence failures

- Repository unavailable: mark provisional, provide conditional levels and next evidence needed.
- Missing referenced skill/policy: use portable reference, report missing dependency, never invent contents.
- Conflicting policy: follow applicable instruction hierarchy; flag unresolved same-level conflict.
- Pre-existing dirty worktree: preserve it, distinguish from requested changes; stop before overlapping edits lacking a safe plan.
- No focused validation available: identify alternate evidence or report inconclusive; do not declare verified.
- Requested operation exceeds authorization: hand off a safe plan, do not execute.
