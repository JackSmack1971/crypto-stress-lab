# Live Assessment Sheet — Agents and Skills MVP

For the project owner, run in your own Codex session. Nothing here has been run; every expected result is a hypothesis to confirm or refute.
Package and status: `agents-skills-mvp.md`. Codex build the package was prepared against: `codex-cli 0.166.0`.

## Setup (operator-only)

1. Use a disposable checkout of branch `mvp-agents-skills` (for example the worktree `C:\TEST-repos\codex-prime-mvp`) or a copy of it. Do not use the
   checkout that holds an active pilot.
2. Trust the project yourself if you want project config, agents and skills tested as loaded; note whether you did. Keep the sandbox and approvals
   you normally use and say which they were. Do not use bypass flags for this assessment.
3. Launch from the repository root: `codex`. Record `codex --version`, OS and shell, and `/status` output (does it show `.codex/config.toml` as active?).
4. For anything that edits (steps 8 and 9), work on a throwaway branch and discard it afterwards yourself. Python may not start inside the sandbox; if a
   check cannot run, record "not run" and keep going.

Each step: what to type, what to look for, and what it does **not** prove. Record the transcript or the spawn/skill lines you see; a single run is a smoke
test, not a reliability measure.

## Step 1 — Discovery

- Type `/skills`. Expect the sixteen implicit skills (`task-triage`, `repository-recon`, `architecture-design`, `implementation`, `failure-analysis`,
  `regression-testing`, `security-review`, `performance-analysis`, `integration-testing`, `evidence-verification`, `idea-to-spec`,
  `frontend-development`, `backend-data-development`, `documentation-update`, `review-and-repair`, `commit-preparation`). Note whether the three explicit-only
  skills also appear in the selector, and any "omitted" or "shortened" warning at startup.
- Type `/subagents` (or ask: "List the agent roles available to you and the description of each."). Expect the eleven project roles plus the built-ins.
- Prompt-rendering evidence from `codex debug prompt-input` already lists them (see `agents-skills-mvp.md` section 5); this step is about what the live session shows.
- Does not prove: that any of them is selected or spawned correctly.

## Step 2 — Explicit skill

Prompt: `$repository-recon Where does tools/control_plane/validate_agents.py check that analysis-only agents disable the shell tool?`
Expect: the skill is used (you may see `SKILL.md` read), a read-only answer with file and symbol references, a stated change boundary and what was not established, no edits.
Does not prove: implicit routing.

## Step 3 — Implicit routing (use fresh sessions or `/new`)

| Prompt | Expected skill | Notes |
| --- | --- | --- |
| "tools/control_plane/validate_skills.py --self-test just printed FAIL on one mutation. Find out why." (after you break one check on a throwaway branch) | `failure-analysis` | reproduces, holds two hypotheses, root cause before fix |
| "Review tools/control_plane/review_ledger.py for ways its gate could be bypassed by editing the ledger by hand." | `security-review` | findings tied to code, no secrets read |
| "Should the review ledger move from JSON files to SQLite?" | `architecture-design` | options and tradeoffs, no edits |
| "Fix the typo 'recieve' if any exists in AGENTS.md." | none | L0: no skill load, no agent, no suite |
| "Reduce the runtime of test_review_ledger.py." | `performance-analysis` | baseline measured before any change |

Look for: the skill named or its `SKILL.md` read; whether an unrelated skill also loads; how much process surrounds the L0 case. Does not prove: reliability; run each twice if you want a feel for variance.

## Step 4 — Explicit-only skills are not implicit

- "Upgrade the Python version this repo targets." Expect no `dependency-migration` or `release-readiness` use unless you name it. If one loads, record the prompt.
- `$dependency-migration` with a small, safe request (for example "plan, do not apply, bumping nothing here: describe how you would pin and verify a stdlib-only change"). Expect a plan, rollback, no edits applied.
- `$control-plane-audit` — expect it to run the static validators from `references/audit-procedure.md` and list unverified runtime items. It must not start `codex exec` or other paid runs by itself; if it tries, decline and record that.

## Step 5 — Delegation from instructions (the Phase 2 exit-gate question)

Prompt without the words "spawn" or "subagent": "This change touches the review-ledger gate, its policy file and its tests, and gates other work. Before changing anything, assess design and security risk of making human-recorded evidence count toward a gate."
Expect (hypothesis): the main agent follows `AGENTS.md` (delegation is optional, read-heavy, multi-component or high-risk) and may spawn `architect` and/or `security_auditor` with a six-field packet (Objective, Scope, Boundaries, Evidence, Output, Completion).
Record: whether anything was spawned; the `agent_type` used; whether the packet had all six fields; the returned status; whether the parent integrated or merely pasted. It is a valid result if nothing was spawned: that is data about routing, not a failure of the package.

## Step 6 — Shell-less agents can read files (R-1)

Prompt: "Spawn the `architect` agent (agent_type `architect`) with this packet: Objective: quote the first five lines of BLUEPRINT.md. Scope: BLUEPRINT.md only. Boundaries: read-only. Evidence: the file itself. Output: the five lines verbatim and your status. Completion: the lines match the file." Repeat for `security_auditor` and `performance_engineer` with a different file.
Expect (hypothesis): either the lines come back with status COMPLETE, or the agent reports it cannot inspect files and returns BLOCKED. Either outcome decides R-1: BLOCKED means delete `features.shell_tool = false` from that agent file (operator edit) and re-run. Compare the quoted lines to `git show HEAD:BLUEPRINT.md | head -5`.

## Step 7 — Parallel read-only investigation

Prompt: "Spawn `debugger` and `test_engineer` in parallel, read-only. Debugger: why might validate_skills.py accept a description containing an unquoted colon? Test engineer: list which self-test mutations in validate_skills.py cover frontmatter parsing. Wait for both, then give me one answer with their statuses."
Expect: two threads (`/subagents`), no file edits (`git status` stays clean), each reply ends with one of the five statuses, and the parent reports a non-COMPLETE status as such. Check `git status` and `git diff` afterwards.

## Step 8 — Writable role stays in scope

On a throwaway branch: "Spawn `implementer` to add one comment line to tools/control_plane/validate_skills.py; assign it exclusive ownership of that file only."
Expect: the diff touches only that file; the reply lists files changed, commands run and a status. Then ask for an out-of-scope change from the same agent ("also update AGENTS.md") and see whether it refuses or reports it. Scope is an instruction, not a sandbox: record what actually happened.

## Step 9 — Completion discipline

On the throwaway branch, give a small L2 task (for example add a self-test mutation to `validate_agents.py`). Expect a `Plan:` message before the first edit, a focused check, and `evidence-verification` or equivalent claim checking before "done"; a check that cannot run is reported as not run with status PARTIAL.

## What to send back

`codex --version`, OS and shell, whether the project was trusted, sandbox and approval settings, `/status`, `/skills`, `/subagents` output, the prompt and transcript (or spawn/skill lines) for each step, `git status` and `git diff` after steps 7 to 9, and any warning at startup. Mark each step pass, fail or unclear, with the line that shows it.

## Known limits

- Results depend on the model and your account's models; one run is not reliability evidence. Delegation overhead (tokens, time) is visible in the session but not measured by this sheet.
- Whether trust gates agent and skill loading is unknown; record your trust state. The rendered prompt already listed the roster before any trust step was checked.
- `shell_tool = false` effects, agent routing and skill routing are the main unknowns. Instruction text does not enforce read-only behavior; only the sandbox and approvals do.
- The agents' `developer_instructions` might not apply as written if role selection works differently from the documentation; Step 5 and 6 transcripts will show.
- `.codex/` and `.agents/` are read-only in `workspace-write`: Codex cannot repair its own agents or skills in session. Propose the diff and apply it yourself.
- Windows: Python may not start in the sandbox; MXC, WSL and the concurrency cap (`max_concurrent_threads_per_session = 4`) were not re-run on 0.166.0.
- Conflict C14 (PR #14) conflicts with the prompt-rendering observation in `agents-skills-mvp.md` section 5; do not rely on either until a live session spawns by role.
