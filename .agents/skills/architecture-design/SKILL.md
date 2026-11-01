---
name: architecture-design
description: "Evaluate and record a consequential software architecture choice before implementation when a change introduces or revises component boundaries, interfaces, data ownership, cross-service behavior, deployment topology, or significant nonfunctional tradeoffs. Compare feasible alternatives against repository evidence and define verification and migration consequences. Do not use for routine localized code changes, mechanical refactors, implementation-only tasks with an already approved design, or standalone code review."
---

# Architecture design

**Purpose:** Resolve one consequential structural decision into an evidence-backed, implementation-ready recommendation, without changing implementation or granting authority for consequential actions.

## 1. Bound the decision

- Read applicable `AGENTS.md` instructions and the relevant repository design authority. Inspect Git status/diff and preserve existing work. Establish the requested outcome, decision owner, system boundary, and whether design-only or implementation is explicitly requested. This skill produces design analysis; implementation remains a separate authorized workflow.
- Confirm that a genuine architecture choice remains. If the design is already authoritative, check whether new evidence invalidates it; otherwise refer execution to the implementation workflow. If the change is localized and has no meaningful structural tradeoff, say that no architecture decision is needed and stop.
- State the decision as a falsifiable question. Identify hard constraints, desired qualities, operational limits, and explicitly out-of-scope concerns. Distinguish documented requirements from assumptions and proposed requirements.

## 2. Establish the architecture baseline

- Inspect only evidence relevant to the decision: actual code and callers, types/contracts, tests, configuration, persistence schemas, operational/deployment topology, and applicable ADRs/specifications. Record paths and symbols or exact source references; do not infer that a document reflects runtime behavior without checking.
- Trace the affected producer-to-consumer flow and identify invariants, ownership, failure boundaries, compatibility commitments, and pre-existing constraints. Note existing worktree modifications that overlap the decision.
- Resolve contradictions by following the repository's explicit authority hierarchy; otherwise mark the conflict **unresolved**, present its impact and the decision owner, and avoid treating either source as authoritative by guesswork.

## 3. Compare feasible designs

- Include the smallest viable change and at least one genuinely different feasible alternative when alternatives exist. A no-change option is appropriate when the requirement can already be met. Do not fabricate an alternative merely to satisfy a count.
- Evaluate each option against the *same* hard constraints and decision criteria. Use the matrix in `references/decision-method.md` when there are multiple cross-cutting qualities, complex migration paths, or substantial uncertainty.
- Distinguish evidence, inference, and unknowns. Do not present untested performance, scalability, security, reliability, or cost claims as facts. Identify how the option changes contracts, data semantics, security/trust boundaries, fault isolation, observability, operations, and rollback, as applicable.
- Eliminate options violating hard constraints. Among feasible choices, prefer the smallest reversible solution that satisfies the objective, unless a documented requirement justifies more complexity. State what evidence would reverse the recommendation.

## 4. Resolve decision and consequence boundaries

- **Mandatory:** Define the selected option, affected components/interfaces/consumers, compatibility and data migration policy, implementation sequencing dependencies, acceptance criteria, and how to independently verify them. Explicitly distinguish design evidence already observed from future checks proposed for implementation.
- **Prohibited:** Invent APIs, repository rules, measurements, tool results, or compatibility guarantees; silently settle disputed authority; mutate code or infrastructure as a byproduct of analysis; use external write actions or irreversible changes without separate authorization.
- **Judgment:** Choose depth proportional to blast radius, irreversibility, criticality, and evidence quality. Optional read-only independent architect/subagent review is justified for cross-cutting or high-consequence tradeoffs when available; the main agent must reconcile findings against source evidence. Subagent agreement is not independent runtime verification.
- If key requirements, ownership, or unavoidable migration/security tradeoffs are unresolved, present a **conditional recommendation** or **decision blocked** with the exact owner decision/evidence required. Do not label it approved or implementation-ready.

## 5. Verify and stop

- Check that every asserted current-state fact is traceable to inspected evidence, every hard constraint is addressed, every affected consumer is accounted for within the declared scope, and every proposed acceptance criterion is testable and tied to a risk.
- Use `references/design-record.md` to format the decision. Load `references/failure-branches.md` when evidence is contradictory, tests or tools are absent, migration is risky, compatibility is ambiguous, or authorization is unclear.
- Stop once the decision and its verification contract are sufficient for the requested scope. Do not expand into speculative redesigns or implementation. Report **READY FOR OWNER REVIEW**, **CONDITIONAL**, **BLOCKED**, or **NO ARCHITECTURE DECISION NEEDED**; never equate a proposed design with a validated implementation.
