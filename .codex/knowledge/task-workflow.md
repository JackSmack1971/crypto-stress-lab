# End-to-end task workflow — CODEX PRIME

How one engineering task moves through the control plane (BLUEPRINT.md section 5.1 state machine, sections 2, 3, 4). This is a **convention for the main agent**, carried by `AGENTS.md`, skills and agents. It is not a daemon or a native Codex workflow engine. Every step below is `GUIDANCE` unless the last column names a stronger point. Nothing here has been run in a live Codex session; routing, delegation and hook behavior are unverified until the operator runs `live-assessment-full.md`.

## The sequence

| # | State | What happens | Skill / agent | Output | Enforcement | Eval |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | RECEIVED | Classify intent, L0-L3 and risk; L0 gets no process | `task-triage` (only if unclear); `task-classification.md` | level, risk override, acceptance criteria | advisory | R-01..R-05, R-08 |
| 2 | SCOPED | Vague idea becomes requirements and a first slice | `idea-to-spec` | spec, open questions | advisory | R-06 |
| 3 | INVESTIGATING | Read only what the task needs; check `git status`; map callers and tests | `repository-recon`; built-in explorer for routine reads | files, call paths, unknowns | advisory | R-07, R-10, R-11 |
| 4 | PLANNED | L2: send a `Plan:` message before the first edit; L3: plan with failure paths and rollback; design unknowns go to `architecture-design` | `architecture-design` / `architect` | plan, decisions | advisory | P-01, P-02 |
| 5 | DELEGATED (optional) | Independent read-heavy pieces to specialists; one writer per file | `debugger`, `security_auditor`, `performance_engineer`, `integration_engineer`, `migration_engineer`, `reliability_engineer`, `test_engineer`; writers `implementer`, `documentation_engineer` | six-field packet out, status + evidence back | sandbox/approvals inherited (Codex); `SubagentStart`/`SubagentStop` hooks nudge (needs operator trust) | D-01..D-04 |
| 6 | IMPLEMENTING | Smallest coherent change; domain skills for UI, server/data, migration | `implementation`, `frontend-development`, `backend-data-development`, `dependency-migration` (explicit) | diff, tests | `workspace-write` sandbox; `PreToolUse` hook denies a narrow unsafe list | I-01..I-04 |
| 7 | VERIFYING | Narrowest check that could catch a regression; failures classified | `regression-testing`, `integration-testing`, `failure-analysis`; `test_engineer` | commands with outcomes | evidence log written by `PostToolUse` hook (needs trust) | V-01..V-04 |
| 8 | DOCUMENTING | Update docs that the change made stale; verify each claim | `documentation-update` / `documentation_engineer` | docs changed and checked | advisory | M-01, M-02 |
| 9 | REVIEWING | Claim check, then independent review (never the author): `/review` if the user runs it, else the `reviewer` agent | `evidence-verification`, `review-and-repair` / `reviewer` | findings with disposition | advisory; `Stop` hook challenges unbacked "tests passed" claims once. The autonomous `reviewer` path depends on spawning by role, which is unverified and disputed by PR #14 conflict C14 | F-01..F-03 |
| 10 | REPAIRING | Fix valid P0/P1 findings; re-review changed hunks; **at most two rounds**, then report what remains | `review-and-repair` | fixes, rechecks, open findings | bounded by instruction and `stop_hook_active` on the gates (a convention, not a counter) | B-01..B-03 |
| 11 | REPORTING | One status: `COMPLETE`, `PARTIAL`, `BLOCKED`, `FAILED`, `CANCELLED`; unrun checks cap at `PARTIAL` | root contract; `contracts.md` section 7 | final report | advisory | V-02, V-04 |
| 12 | COMMIT (only on request) | Stage named files, review staged diff, one local commit, no push | `commit-preparation` | commit hash | advisory plus `PreToolUse` denials of `--no-verify`, force and deleting pushes (needs hook trust). `git add -A` and a plain `git push` are **not** blocked by any delivered control; on a host whose user rules allow `git push` outside the sandbox (contracts.md section 4) nothing prompts. Keep `approvals_reviewer = "user"` (the default; this project does not set it) so a model reviewer never approves a commit or push escalation | C-01..C-04, G-01 |

Higher-risk work: security-sensitive, destructive, irreversible, data-migrating or production-facing changes are L3 whatever their size. They get a plan with rollback, run nothing against shared or production data without authorization, and end `BLOCKED` while the unauthorized step is unrun.

## Authority rules the workflow never relaxes

- A model's review, approval, or "ready" verdict (the `reviewer` agent, `/review`, `release-readiness`, Codex cloud review) does not authorize a commit, push, merge, deployment, or secret change. Only an explicit instruction from the user does, and the sandbox and approvals still apply.
- Subagent output is input to check, not proof. A status other than `COMPLETE` is reported as is.
- `.codex/` and `.agents/` are read-only to Codex in `workspace-write`; the workflow proposes control-plane edits and the operator applies them.

## What would show it works (not yet observed)

Offline: `python -I tools/control_plane/evaluate.py check` validates the scenario library and grades recorded transcripts (`evaluation.md`). Live: the operator runs the prompts in `live-assessment-full.md` and returns transcripts for grading. A single run is a smoke test, not a reliability measure.
