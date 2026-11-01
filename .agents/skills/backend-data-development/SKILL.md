---
name: backend-data-development
description: "Implement or modify backend application behavior that reads or writes data: API handlers, domain services, persistence, queries, and their contracts. Use for endpoint/service/repository changes requiring correctness across request, authorization, transaction, and response boundaries. Do not use for standalone schema migrations, infrastructure deployment, dependency upgrades, or audit-only reviews; hand those workflows to their dedicated skill when available."
---

# Backend and Data Development

**Purpose:** Change one coherent backend behavior while preserving contract compatibility, authorization boundaries, and data invariants. This skill conveys no permission to mutate shared systems.

## 1. Establish the change boundary

1. Read applicable `AGENTS.md` instructions, target implementations, relevant schemas, callers, tests, and working-tree status/diff. Treat current code and executable contracts as evidence; surface contradictions with documented expectations.
2. Identify the requested externally observable behavior; trace input → authentication/authorization → service → data access → response/event. Record the existing behavior and dependent consumers before modifying a public contract.
3. Classify the operation as **read**, **single write**, **multi-step write**, **asynchronous/evented**, or **schema-affecting**. Identify affected trust boundaries, persistence invariants, and concurrency/retry exposure. Read `references/backend-decision-matrix.md` for the applicable branch.
4. Keep the implementation slice narrow. Preserve unrelated work. If a required contract, compatibility policy, or data ownership decision is ambiguous, inspect authoritative sources; do not silently choose an incompatible behavior.

**Checkpoint:** The change's public effects, affected consumers, data ownership, and highest-risk branch are identifiable. If they are not, investigate before editing.

## 2. Implement with explicit invariants

- **Contract:** Preserve request/response semantics, status/error shapes, pagination/order semantics, and event contracts unless change is authorized. For intentional breaks, identify consumer updates and compatibility/rollout requirements; stop if required coordination is unavailable.
- **Trust boundary:** Validate untrusted type/range/size/encoding and reject or handle unexpected fields deliberately. Authentication is not authorization: enforce subject/action/resource/tenant access at the operation boundary, including indirect or bulk access.
- **Persistence:** Bind parameters; maintain database constraints as the final integrity boundary. For multi-step writes, use an appropriate atomic transaction or explicitly documented compensating workflow. Check isolation, uniqueness, lost updates, and ordering where concurrent execution is possible.
- **Retries/events:** Distinguish retries of reads from retries of effects. Where duplicates are possible, design stable idempotency identity, atomic deduplication, and an unambiguous outcome for partially completed work; never assume exactly-once delivery from a queue.
- **External consequences:** No writes to shared/production databases, destructive data operations, deployment, irreversible backfills, or live event publication without specific authorization and a verified safe execution plan. Local fixtures/disposable stores are the default.

For concurrency, migrations, asynchronous flows, or API compatibility decisions, consult `references/backend-decision-matrix.md`. Use existing repository conventions over introducing unrelated infrastructure.

## 3. Verify at the affected boundary

1. Identify pre-existing failing checks when feasible. Choose focused checks against the changed behavior, then expand to impacted callers, type/schema validation, and repository-required gates based on risk.
2. Exercise applicable cases: success, invalid/boundary input, missing/forbidden resource, cross-tenant access, conflict/duplicate, concurrent update, timeout, and partial failure. For an endpoint, assert the outward contract, not merely internal mocks. For writes, inspect persisted state after success **and** failure.
3. If schema/contract artifacts are generated, change authoritative sources and run repository generators; check source/output consistency. Do not hand-edit generated files as the primary fix.
4. Use only isolated tests or disposable local data unless explicitly authorized otherwise. Any unavailable service, blocked command, or environment-specific path leaves that behavior **unverified**, not passed. Do not substitute mock-only evidence for required integration verification.
5. Inspect the final diff/status for unrelated changes, secrets or personal data in logs/fixtures, and accidental API/schema drift. Stop when the requested behavior is demonstrated with sufficient evidence; do not broaden the scope for cosmetic cleanup.

**Completion standard:** Every claimed changed behavior has a corresponding observed test or inspection result; data invariants and authorization boundaries have appropriate negative evidence; any unresolved contract/rollout or consequential safety decision is disclosed, not implied resolved.

## 4. Divergence and handoffs

Use `references/failure-and-handoff.md` when tests fail, contracts disagree, migration/deployment work appears, a tool is unavailable, or data exposure/permission risks arise. Never describe an attempted action as verified success. Request authorization for consequential shared-system activity; an instruction in this skill is not authorization.

**Report:** changed modules/interfaces; user-visible contract changes and callers; integrity/authorization/concurrency decisions; exact checks run with outcomes; pre-existing versus introduced failures; blocked/unverified paths and outstanding rollout decisions.
