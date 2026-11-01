---
name: implementation
description: "Implement a bounded, already-authorized repository code change when intended behavior and scope are sufficiently defined. Own edits, targeted regression checks, and final diff review; not requirements discovery, architecture-only planning, standalone review, or deployment."
---

# Bounded implementation

**Outcome:** one smallest coherent change with observable acceptance evidence. This skill does not authorize work beyond the user's request.

## 1. Qualify the slice

1. Read applicable `AGENTS.md` instructions. Inspect working-tree/index status, relevant diffs, target code, tests, and the nearest authoritative specification or acceptance criteria.
2. State the desired behavior and a check that could disprove success. Identify the smallest independently verifiable slice, affected files, and existing user changes. If the task is only exploration, design, review, or deployment, hand off to that workflow rather than making a speculative edit.
3. **Stop for a consequential decision** when the intended behavior, compatibility contract, architecture, or permission to affect existing changes is genuinely unresolved. Safe read-only investigation may continue. Do not invent a product requirement to unblock implementation.

## 2. Change only the qualified slice

- Preserve unrelated staged, unstaged, and untracked work. Never overwrite or stage someone else's changes. If edits overlap, inspect and preserve them or stop with the conflict documented.
- Follow the actual local architecture. No unrelated refactoring, dependency churn, generated-file hand edits, or weakening/deleting/skipping tests to obtain green output.
- If generated output must change, edit its authoritative source and regenerate only through an established repository procedure; if unavailable, record the inconsistency and do not claim synchronization.
- Use tests appropriate to the changed behavior. Prefer a failing regression test before a fix when feasible; do not fabricate a failure just to follow test-first ordering.
- Delegate only truly independent work when subagents are available and each has exclusive file ownership; integrate and independently verify every result. Otherwise implement directly.

## 3. Verify and stop

1. Run focused tests or checks that can catch the intended regression; inspect actual exit status and output. Expand checks when dependencies, risk, or failures justify it, including repository-required gates where applicable.
2. Inspect the final diff and status against the initial state: scope, unintended edits, tests, docs, generated output, and unresolved changes. Confirm the observed behavior against the acceptance evidence, not simply successful command execution.
3. If a check fails, distinguish a proven pre-existing failure from an introduced one; otherwise label attribution **unknown**. For tool, baseline, permission, architecture, or inconclusive-evidence problems, load `references/failure-decisions.md`.
4. Update affected documentation when the behavior or interface changes. Use complementary frontend/backend/documentation/review skills only if available and applicable; their output is not proof of verification. If a local coordination contract is present, follow it; if missing, continue safely with these boundaries.
5. Stop once acceptance is evidenced and relevant checks complete; do not expand scope to unrelated cleanup. Do not commit, push, open PRs, deploy, migrate production data, or execute external side effects without authorization for that action.

## Handoff

Report **behavior and files changed; tests changed; commands and observed outcomes; checks not run and why; blockers, regressions, and remaining uncertainty**. Distinguish implemented, verified, and unverified. Never imply that an attempt equals success.
