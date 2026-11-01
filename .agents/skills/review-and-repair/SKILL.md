---
name: review-and-repair
description: "Independently review and repair a material code change through a bounded, evidence-backed review loop. Use after implementation when the user requests review-and-fix, repair of verified review findings, or independent re-review of a candidate diff. Not for review-only requests, routine formatting, initial feature implementation, or authorization to merge/deploy."
---

# Review and repair

**Purpose:** converge a specific implementation candidate toward its acceptance criteria by independently reviewing, verifying, repairing, and re-reviewing material defects. This skill gives no commit, push, merge, deployment, or risk-acceptance authority.

## Mandatory workflow

1. **Establish scope.** Read applicable `AGENTS.md`, relevant acceptance criteria, `git status --short`, the exact candidate comparison (base commit or approved equivalent versus head and working-tree delta), and existing checks. Record pre-existing edits and distinguish staged, unstaged and untracked changes. If a stable comparison cannot be determined, stop and report the missing basis; do not review an invented range.
2. **Freeze review identity.** Record repository root, base/head commits, working-tree diff digest, scope, acceptance criteria, and an immutable task identifier. A changing head or diff invalidates prior clean-review evidence. Do not discard or overwrite unrelated changes to recreate the old candidate.
3. **Select review path.** Prefer repository-mandated independent reviewer. Otherwise use supported native review or an available independent agent, with a packet containing the exact identity, diff, requirements, checks and restrictions. An author self-review is useful preliminary analysis but **not independent review**. If no independent reviewer exists, perform read-only analysis, mark independence unverified, and stop short of claiming the review gate passed.
4. **Triage before editing.** Check each material finding against the code, applicable contract and reproducible evidence when practical. Label `confirmed`, `rejected` (with disproof), or `unresolved`; preserve finding identity and classify introduced / pre-existing / uncertain. Do not treat reviewer confidence or severity alone as evidence. A security hypothesis stays unresolved until substantiated or authorized risk disposition.
5. **Repair only confirmed, in-scope defects.** Prioritize P0/P1 and defects that block agreed acceptance; use minimal edits while preserving pre-existing changes. Obtain the owner’s decision before changing semantics, architecture, compatibility, policy, or deliberately accepting consequential risk. Never weaken tests, hide failures, or modify unrelated areas to obtain a clean verdict.
6. **Verify and re-review.** Run affected tests/static checks, inspect final diff, and request independent re-review of changes since the previous pass while retaining surrounding context. Scan affected call sites for the same defect class. Do not claim a successful repair solely because a patch applied or the reviewer agreed. Handle newly discovered findings under the **same** task and review budget.
7. **Stop and hand off.** Finish only when material findings are resolved with evidence, relevant checks pass (or pre-existing failures are clearly demonstrated), review identity still matches the candidate, and required human/CI gates are separately satisfied where applicable. Otherwise stop with `BLOCKED`, `OPEN FINDINGS`, or `INCONCLUSIVE`, and describe the exact unresolved reason.

## Review budget and state

Use an existing authoritative repository review ledger and policy if available. Never bypass its stricter cap. Otherwise use `scripts/review_ledger.py` to record one task with **at most 3 independent review passes total** (initial + up to 2 follow-up passes). Run `init` once and `pass` once per actual independent review; inspect `status` before every further pass. Preserve the ledger outside disposable worktrees and across retries. The script is an advisory local accounting safeguard, **not** an authorization, an independent reviewer, or a concurrency/CI enforcement boundary. If its persistence cannot be guaranteed, stop instead of silently resetting the budget. Details: [review protocol](references/review-protocol.md).

## Output contract

Report: exact candidate identity and review source; pass count/budget; findings with evidence and dispositions; repairs; verification commands and observed results; change-induced versus pre-existing failures; remaining risks and missing approvals; final state (`VERIFIED`, `OPEN FINDINGS`, `BLOCKED`, `INCONCLUSIVE`). `VERIFIED` means this skill's bounded review evidence is sufficient, **not** permission to ship or proof of universal correctness.
