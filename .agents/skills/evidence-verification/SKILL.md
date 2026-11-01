---
name: evidence-verification
description: Audit completion claims for consequential repository changes before declaring work done or handing it to independent review. Use at implementation, migration, release, or multi-file change checkpoints when acceptance criteria must be reconciled with actual diffs and test evidence. Not for exploratory research, routine single-answer questions, or performing the implementation itself.
---

# Evidence verification

This skill exists to **audit completion claims against reproducible evidence** when a consequential repository change reaches a completion or review checkpoint. It verifies reporting, not the implementation and not permission to deploy, merge, or publish.

## Boundary

- Apply at a completion checkpoint for consequential changes (including L2/L3 **if the repository defines those labels**), or when a user explicitly requests an evidence audit. Do not invent risk levels. Routine trivial edits use the repository's normal completion contract.
- Inspect the active instructions (`AGENTS.md` and applicable higher-priority policy), the user request, acceptance criteria, working tree/index, and any relevant baseline evidence. Preserve existing user changes; never repair unrelated work under this skill.
- A separate `review-and-repair` workflow may follow **only if it exists and is required**; this skill does not claim to have invoked it or substitute for its findings.

## Evidence gate

1. **Enumerate claims.** Extract each testable acceptance criterion and each proposed completion statement. Distinguish implementation, tests, generated artifacts, external effects, and independent review. If criteria conflict or cannot be operationalized, state the unresolved decision instead of inventing a pass condition.
2. **Establish scope and provenance.** Review `git status --short`, staged and unstaged diffs, and relevant untracked deliverables. Inspect relevant source/test/configuration files; account for pre-existing edits and baseline failures. No Git repository? Inspect supplied artifacts and say that Git-diff coverage is unavailable.
3. **Map each claim to evidence.** Record the artifact or exact command, observable result, context (target, environment, revision, time when material), and whether it directly tests the claim. A plan, tool availability, agent assertion, exit code alone, or prior run without matching inputs is **not** proof. Cite precise paths and command results, without leaking secrets.
4. **Challenge the evidence.** Look for missing paths, changed-but-untested behavior, weakened/skipped tests, ignored failures, stale output, generated/source drift, success exit with insufficient assertions, contradictory observations, and unreviewed side effects. Use focused checks that can falsify the claim. Prefer verification independent of the implementation action when practical.
5. **Close gaps safely.** Run the smallest necessary read-only or low-risk focused check when tools and authorization permit. Broaden only if risk or contradictory evidence warrants it. Do not modify code, test assertions, deployment state, or repository history to make a claim pass. If verification requires a risky action, credentials, network access, or permission not granted, mark it unverified and stop that branch. Never treat blocked checks as passes.
6. **Decide and stop.** Reconcile every criterion and material side effect. Apply the status rules in [status-and-failures](references/status-and-failures.md). Stop when all material claims have adequate evidence, or when remaining verification is blocked/out of scope. Do not continue running checks merely to accumulate reassuring output.

## Output contract

Report a concise claim ledger with **claim / status (`VERIFIED`, `FAILED`, `UNVERIFIED`, `CONFLICTED`) / evidence / gap or next check**. Separate pre-existing from introduced failures where evidence permits. State the commands actually executed and results, the file/diff coverage achieved, unexecuted checks, external effects not verified, and overall status (`COMPLETE`, `PARTIAL`, `BLOCKED`, `FAILED`, `CANCELLED`).

`COMPLETE` requires all material criteria verified, no unresolved contradicting evidence, and no mandatory pending independent review. An unrun **required** check precludes `COMPLETE`; an optional irrelevant check does not. Never promote another agent's `COMPLETE` assertion into verified evidence without inspecting its artifacts.
