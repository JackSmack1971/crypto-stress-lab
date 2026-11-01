---
name: commit-preparation
description: Prepare a focused local Git commit from authorized changes. Use when asked to commit completed work, stage an intended change for a commit, or prepare a commit without publishing it. Distinguish commit preparation from general Git status review, code review, implementation, pushing, PR creation, amending, rebasing, or releasing; none of those tasks alone authorizes a commit.
---

# Commit preparation

**Boundary:** This skill owns selection, validation, and (only when requested) creation of **one new local commit**. An instruction to implement, review, test, prepare a PR, or report readiness does not authorize committing. Do not push, amend, reset, stash, rebase, merge, tag, switch branches, bypass hooks, or rewrite history under this skill. A prior instruction explicitly asking to commit the completed task counts as authorization unless subsequently withdrawn.

## 1. Establish scope and authority

1. Read applicable `AGENTS.md` instructions, the user's current request, and any relevant repository commit policy. Establish the intended change set from task evidence; do not infer ownership merely from file names or timestamps.
2. Confirm repository root and branch/HEAD; inspect `git status --porcelain=v1 -uall`, `git diff --name-status`, `git diff --cached --name-status`, and relevant untracked files, staged and unstaged diffs. Inspect recent commit subjects to infer an existing message convention, if any.
3. Distinguish **task-owned changes**, **pre-existing or foreign changes**, and **ambiguous changes**, including pre-staged content and mixed hunks in the same file. Stage or commit only demonstrably task-owned content. Where ownership or intended inclusion is unresolved, exclude it; if it prevents an accurate coherent commit, stop and report the decision needed.
4. Existing staged content is not automatically authorized. Avoid changing or clearing unrelated index entries. If the index cannot be isolated without risking other work, stop; do not use `git reset`, `git restore --staged`, or an alternate index as an improvised workaround.

## 2. Assemble a controlled candidate

1. Stage only selected paths or exact hunks using explicit Git operations (`git add -- <paths>` for wholly owned files; `git add -p` only when individual hunks can be confidently identified). A path-level add stages **all** its current changes. Never use `git add -A`, `git add .`, `git commit -a`, or blind bulk staging.
2. Review the **complete proposed commit**, not just the additions: `git diff --cached --stat`, `git diff --cached --check`, `git diff --cached --name-status`, and `git diff --cached` (inspect binary-file provenance separately). Include tracked deletions, renames, submodules, mode changes, untracked additions, and generated files in the scope check where applicable.
3. Reject unrelated, ambiguous, secret-bearing, environment-specific, generated-byproduct, or unexpectedly large artifacts unless explicitly intended and safe. If a secret may already have entered the index or history, stop and report without reproducing its value. Do not claim that text inspection reliably detects every secret.
4. Verify the selected staged changes form one coherent unit and that remaining staged or unstaged material is accounted for. For an already-staged candidate, verify every staged hunk has the same authority as a newly staged one.

## 3. Verify and commit conditionally

1. Run the applicable repository-required checks and the narrowest checks needed for the actual changes. Record exact commands and outcomes. Determine whether failures are pre-existing when evidence permits; do not make a failing check pass by weakening or skipping it. Treat unavailable/inconclusive required checks as a blocker unless the user expressly authorizes a documented exception consistent with repository policy.
2. Before any commit, recheck `git status --porcelain=v1 -uall` and the **entire** staged diff. If hooks, checks, collaborators, or tools changed the candidate, review and revalidate the new candidate; never assume the index stayed fixed. If other actors may be modifying the same index and isolation cannot be established, stop.
3. If the user did **not** explicitly authorize a commit, stop here: report the proposed changes, validation, and remaining exclusions. Do not turn preparation into a commit on your own.
4. If authorized, write a concise subject consistent with repository convention and actual scope. Use an ordinary local `git commit` with hooks enabled. Never use `--no-verify`, `--amend`, signing bypasses, or commands that implicitly publish. If signing, identity, hooks, locks, conflicts, or commit creation fail, investigate without deleting locks, overwriting state, or retrying destructively. Report the blocker.
5. Independently verify the result with `git log -1 --format='%H%n%s'`, `git show --stat --format=fuller HEAD`, `git diff-tree --no-commit-id --name-status -r HEAD` (for non-root commits), and fresh `git status --porcelain=v1 -uall`. Confirm the expected new HEAD, subject, and file/hunk scope; check remaining changes are preserved. A successful command exit alone is not proof of an acceptable commit. Report if post-commit verification is incomplete or discrepancies appear; do not silently create a corrective commit.

## Stop and report

Stop once the requested candidate is verified, or once one authorized commit is independently confirmed. Do not continue into pushing or PR operations. Report: **commit created or preparation only**, hash/subject if verified, committed or proposed paths, excluded/still-staged changes, checks with outcomes, and unresolved blockers. Never describe checks not run as passing.
