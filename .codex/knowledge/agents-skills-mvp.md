# Agents and Skills MVP Package — CODEX PRIME

Scope: the BLUEPRINT.md v1.2 custom-agent roster (section 2.3) and foundational skill catalog (section 3.3), with the validators
and docs they need. Built **2026-10-31** on baseline `origin/main` `2371917814bbf06f4401c29d6491db0e5a26c586`, branch
`mvp-agents-skills`, `codex-cli 0.166.0`, Windows 11 build 22631, Git Bash, `python -I`. No model session, `codex exec`, `/review`,
subagent, operator check, or credential read was done. Live assessment sheet: `live-assessment-agents-skills.md`.

Authorization: built on the project owner's direction while **Phase 1 and Phase 2 are PARTIAL**. Nothing here closes a Phase 1, 2 or 3
evidence gap; this package is static work awaiting live assessment. Sources (opened 2026-10-31 through the `openaiDeveloperDocs` MCP):
`learn.chatgpt.com/docs/agent-configuration/subagents`, `/docs/build-skills`, `/docs/agent-configuration/agents-md`. The approvals and
config-reference pages are already recorded in `native-capabilities.md` (D4, D3).

## 1. Delivered

| Item | Files | Static check |
| --- | --- | --- |
| Ten custom agents (BLUEPRINT 2.3; `reviewer` added later, section 7) | `.codex/agents/{architect,debugger,implementer,test_engineer,security_auditor,performance_engineer,integration_engineer,migration_engineer,reliability_engineer,documentation_engineer}.toml` | `validate_agents.py --self-test` 32/32 |
| Thirteen skills (BLUEPRINT 3.3; six more added later, section 7) | `.agents/skills/<name>/SKILL.md`; seven `references/*.md`; `agents/openai.yaml` for the three explicit-only skills | `validate_skills.py --self-test` 28/28 |
| Routing hook-up (BLUEPRINT 2.1, 3.5) | `AGENTS.md` "Skills and subagents": names the skills and the agents, says which skills are explicit-only, keeps delegation optional | `validate_contracts.py`, `validate_classification.py` (AGENTS.md pointers, size) |
| Records | `contracts.md` delivered-controls paragraph; `native-capabilities.md` capability 4 and 6 rows; this file; the assessment sheet | `validate_contracts.py` |

Agents: model and tool changes use only documented keys. Every agent states the five statuses, requires inspected evidence, forbids invented
APIs, and says the role grants no authority to commit, push, deploy or change secrets. `model_reasoning_effort` only; no `model`.
`sandbox_mode`, `approval_policy`, `mcp_servers`, `model_provider` and the service tier are not set (documented as ignored in an agent file);
permissions, approvals, network and MCP come from the parent session.

| Agent | Shell tool | Writes | Notes |
| --- | --- | --- | --- |
| architect | off | no (instruction) | shipped in P2-S01; one line added: no-authority sentence |
| debugger | on | no (instruction); scratch under `.codex-runtime/` | finds cause, does not fix |
| implementer | on | yes, only packet-assigned files (instruction) | exclusive file ownership comes from the parent |
| test_engineer | on | test files assigned by the parent (instruction) | classifies failures |
| security_auditor | off | no (instruction) | cannot run anything; findings are inspection-only |
| performance_engineer | off | no (instruction) | designs benchmarks; may not report unmeasured numbers |
| integration_engineer | on | no (instruction) | no external or shared environments without authorization |
| migration_engineer | on | no (instruction) | prepares and reviews; never applies |
| reliability_engineer | on | no (instruction) | local fault scenarios only |
| documentation_engineer | on | yes, only packet-assigned docs (instruction) | verifies claims against code |

Skills: ten implicit, three explicit-only (`dependency-migration`, `release-readiness`, `control-plane-audit`), matching BLUEPRINT 3.2. Each
`SKILL.md` has a quoted one-sentence description (111-164 chars) with the trigger first, states goal, constraints and return shape, says
the skill grants no new authority, and points to `references/` or to existing `.codex/knowledge/` files rather than copying them.
Catalog size from the validator: about 2.7k characters for 13 names, descriptions and paths (limit used: 6,000 of the default 8,000 budget).

## 2. Enforcement points

| Safeguard | Enforcement point | State |
| --- | --- | --- |
| Agents inherit sandbox, approvals, network, MCP | Codex (documented, subagents page) | **documented**, unobserved |
| `features.shell_tool = false` removes command execution for architect, security_auditor, performance_engineer | Codex (documented capability reduction) | **documented**, unobserved; side effect on file reading unknown (R-1) |
| Read-only roles do not edit files | **Advisory** (instruction). Docs: agent instructions create no separate read-only sandbox; `shell_tool = false` does not remove editing | unenforced |
| Writable roles stay inside assigned files | **Advisory**; the parent's packet defines the scope | unenforced |
| Status line and evidence in agent replies | **Advisory**; a `SubagentStop` hook could reinforce it (Phase 4, not built) | unenforced |
| Explicit-only skills are not chosen implicitly | Codex (`allow_implicit_invocation: false`, documented) | **documented**; prompt rendering consistent (section 5); selection unobserved |
| Skills do not widen authorization | **Advisory** text; the sandbox and approvals are what bound actions | unenforced |
| Agent and skill files are well-formed, names unique, descriptions distinct, references exist | Control-plane (`validate_agents.py`, `validate_skills.py`) | static only; no CI runs them |

## 3. Blueprint items

Completed (static): 2.3 roster (10 agents); 2.7/2.8 statuses and limits in each agent; 3.3 catalog (13 skills); 3.2 explicit-only policy files;
3.4 schema and description rules; 3.6 collision checks (duplicate names, overlap heuristic, missing references, oversized text); 3.7 progressive
disclosure (short bodies, references only where useful); `validate_skills.py` (section 3 layout); section 9 rows 8 to 13 as files.

Deferred or not done, with reason:

| Item | Reason |
| --- | --- |
| Phase 2 exit gate (real delegation scenario) and 2.9 runtime criteria | needs a trusted live session |
| Phase 3 exit gate and 3.8 runtime criteria (discovery, `$skill`, implicit routing, unrelated skills not chosen, no catalog warning) | needs a live session; sheet provided |
| Hooks `SubagentStart`/`SubagentStop`, execution rules (Phase 4) | out of scope |
| `tests/control_plane/*.py` files named in section 3 | repository convention is mutation self-tests inside each validator; no separate test tree was added |
| `validate_artifacts.py`, `evaluate.py` (Phase 6 harness) | out of scope; `evaluate.py` would drive paid `codex exec` runs |
| Custom reviewer agent | Blueprint says `/review` is native; none added |
| Skill `scripts/` and `assets/` | no real benefit yet; the validator rejects them until a skill needs one |
| Measuring delegation overhead (2.9) and skill trivial-task overhead (3.8) | needs live runs |
| Routing test cases of section 3.5 | listed as live prompts in the assessment sheet; no offline model of Codex routing |

Choices where the Blueprint left room (all open to change): `model_reasoning_effort` per agent (high for architect, debugger,
security_auditor, performance_engineer, migration_engineer, reliability_engineer; medium for the rest); `performance_engineer` and
`security_auditor` take the shell-less setting the Blueprint names for analysis-only specialists even though the performance engineer then cannot
run a benchmark itself (its instructions say so); `documentation_engineer` and `implementer` are the two writable roles; skill bodies stay under
60 lines and cite `references/` only for `design-record`, `root-cause-report`, `test-matrix`, `threat-checklist`, `migration-plan`,
`readiness-checklist` and `audit-procedure`.

## 4. Risks that decide whether the package is useful

- **R-1 (carried from P2-S01).** Three agents drop the shell tool. Whether they can still read repository files is undocumented and unobserved.
  If they cannot, they return `BLOCKED` by their own instruction. Fallback: delete the `features.shell_tool = false` line from that agent and
  rely on the instruction plus the parent's sandbox. Test first (assessment sheet, step 6).
- **R-2 routing.** Neither agent selection nor skill selection is a Codex-enforced outcome of this package; both depend on descriptions and
  `AGENTS.md`. An overly eager parent could over-delegate, a conservative one never would. Unmeasured.
- **R-3 trust.** Project `.codex/config.toml`, and possibly agents and hooks, load only after the operator trusts the project; trust was not read.
- **R-4 cost.** Each spawned agent is a separate model run.

## 5. Observations on codex-cli 0.166.0 (non-model; my runs, not independently reproduced)

Command: `codex debug prompt-input` launched from the worktree root, output parsed as JSON. It renders the model-visible prompt; it is not a
documented interface and does not start a model session.

| Observation | Result |
| --- | --- |
| `spawn_agent` parameters | `agent_type`, `fork_turns`, `message`, `model`, `reasoning_effort`, `task_name`; required `task_name`, `message` |
| `agent_type` text | "Agent type override for the new agent. Omit unless explicitly asked." followed by "Available roles" |
| Roles listed (this worktree, 10 project agents) | `architect`, `debugger`, `documentation_engineer`, `implementer`, `integration_engineer`, `migration_engineer`, `performance_engineer`, `reliability_engineer`, `security_auditor`, `test_engineer`, then `default`, `explorer`, `worker`; each project role shows its `description` |
| Same render from a clean detached `origin/main` worktree (only `architect`) | roles: `architect`, `default`, `explorer`, `worker` |
| Skills list in the rendered prompt | the ten implicit skills appear with their descriptions and `SKILL.md` paths; `dependency-migration`, `release-readiness` and `control-plane-audit` appear only inside the `AGENTS.md` text, not in the skills list |
| Skill-budget warning text in the rendered prompt | none found (a TUI warning would not appear here) |

Meaning and limits:

- The rendered prompt shows Codex parsed the agent files and skill metadata at that launch directory. It does **not** show that a model can spawn
  by role, that the role's `developer_instructions` apply, that routing works, or that `shell_tool = false` has its effect.
- Project trust was not read for either directory; the roster rendered from a detached worktree path, so whether trust gates it is unknown.
- **Discrepancy with PR #14 (open, not edited):** its record (conflict C14, `spawn-interface-0166.md`) says the rendered `spawn_agent` schema had no agent
  selector and none of the role names. The two runs above, made the same day on the same binary, contradict that. Cause not established (launch
  directory, session state, or the earlier probe's extraction are all possibilities, none checked). C14 should be rechecked by whoever owns that PR before it is merged.

## 6. Static results (my runs; historical, taken before the later additions in section 7, which changed the counts)

```
python -I tools/control_plane/validate_agents.py --self-test       -> 32/32 PASS
python -I tools/control_plane/validate_skills.py --self-test       -> 28/28 PASS (13 skills, catalog about 2693 chars)
python -I tools/control_plane/validate_config.py --codex --self-test        -> 15/15 PASS
python -I tools/control_plane/validate_contracts.py --codex --self-test     -> 29/29 PASS
python -I tools/control_plane/validate_classification.py --codex --self-test -> 25/25 PASS
python -I tools/control_plane/check_delegation_packets.py --self-test       -> 12/12 PASS
python -I tools/control_plane/review_ledger.py check-policy                 -> PASS
python -I tools/control_plane/test_review_ledger.py                         -> 38 tests OK
git diff --check                                                            -> clean
```

Status: **static PASS; runtime discovery, spawning, routing and invocation unverified (`BLOCKED: operator`)**. Phase 2: PARTIAL. Phase 3: PARTIAL.

## 7. Additions in the full control-plane pass (after the first MVP commit)

Deviations from BLUEPRINT.md v1.2, made on the project owner's direction to build the full end-to-end workflow (`task-workflow.md`). Each is open to reversal.

| Addition | Blueprint position | Why |
| --- | --- | --- |
| `reviewer` agent (`.codex/agents/reviewer.toml`, read-only by instruction, shell on, effort high) | Blueprint 2.3 has ten specialists and leaves review to native `/review` | a model cannot invoke `/review`, so an autonomous task needs a spawnable independent reviewer. `/review` stays the user-run path |
| Six skills: `idea-to-spec`, `frontend-development`, `backend-data-development`, `documentation-update`, `review-and-repair`, `commit-preparation` | Blueprint 3.3 lists thirteen foundational skills; 5.x places workflows inside skills | ideation, UI, server/data, docs, bounded review/repair and commit behavior had no focused trigger. All six are implicit and grant no authority; `validate_skills.py` checks overlap and catalog size |
| `AGENTS.md`: workflow sentence, commit rule, `## Code Review Rules`; `.codex/hooks/AGENTS.md` | Blueprint 1.1 root contract | documented location for Codex review rules (`code-review.md`) |

Counts now: eleven agents, nineteen skills (sixteen implicit, three explicit-only). Skill catalog about 3,970 characters against the validator's 6,000 limit. Non-model render (`codex debug prompt-input`, 0.166.0, from this worktree, JSON-parsed; my run, not independently reproduced): all sixteen implicit skills appear with descriptions, the three explicit-only skills do not, the agent role list includes the new `reviewer`, and no catalog-truncation warning text appears in the rendered prompt. Rendering is not spawning or routing.

Delivered in the same pass (see their own records): hooks (`hooks.md`), review rules and PR review path (`code-review.md`), workflow (`task-workflow.md`), evaluation (`evaluation.md`), live sheet (`live-assessment-full.md`).
