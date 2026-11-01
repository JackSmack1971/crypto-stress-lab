# Implementation status — CODEX PRIME

State of branch `mvp-agents-skills` (baseline `origin/main` `2371917814bbf06f4401c29d6491db0e5a26c586`), `codex-cli 0.166.0`, Windows 11 / Git Bash / Python 3.14.3. Static work is built and verified by my own runs (not independently reproduced). **Runtime behavior is unverified everywhere**: no Codex session, `codex exec`, `/review`, subagent spawn or operator check was run in this work. The system is not labeled complete. Phases 1 to 6 stay `PARTIAL` (Phase 0 and 1 evidence gaps from earlier slices are unchanged and merges do not close them).

## By Blueprint area

| Area (BLUEPRINT section) | Built | Static check | Not built or not verified |
| --- | --- | --- | --- |
| Root contract, config, contracts, classification (1.x) | merged earlier; `AGENTS.md` extended with workflow, commit rule, review rules | `validate_config/contracts/classification --codex --self-test` | operator checks O-A, O-B, O-I, O-J (`BLOCKED: operator`); instruction discovery per launch directory |
| Custom agents (2.x) | ten roster agents + `reviewer` | `validate_agents.py --self-test` | spawning by role, packet use, `shell_tool = false` file reads (risk R-1), concurrency cap, Phase 2 exit gate |
| Skills and routing (3.x) | nineteen skills (three explicit-only), eleven reference files | `validate_skills.py --self-test` | live discovery, `$skill` invocation, implicit routing, unrelated skills not chosen, overhead |
| Hooks (4.4) | six handlers + `.codex/hooks.json`, fixtures, `hooks.md` | `test_hook_policies.py` (43 tests) | operator trust in `/hooks`; real events; Windows launcher; timeout/missing-interpreter behavior; forced `/compact`; `PreCompact` warning hook; `UserPromptSubmit` |
| Execution rules (4.3) | **not built** | none | needs `codex execpolicy check` cases and the in-sandbox `forbidden` question |
| Platform support doc (4.2, 4.6) | `hooks.md` Windows section only | none | `platform-support.md`, WSL runs |
| Workflows and evidence (5.x) | `task-workflow.md`; skills and references carry the lifecycle; `execution_evidence.py` writes the mechanical log | validators + fixtures | task-local `.codex-runtime/results/<task-id>.json` is a convention only; no end-to-end Codex demonstration (Phase 5 exit gate) |
| Code review (4.1, 5.2, PR path) | review rules in `AGENTS.md`; `reviewer` agent; PR template; `code-review.md` | `validate_review_rules.py --self-test` | enabling automatic review (account setting, `BLOCKED: operator`); whether cloud review follows the rules |
| Evaluation (6.x) | 38-scenario library, four fixtures, `evaluate.py` (`check`, `self-test`, `grade`, `git-facts`, `fixture`, `plan`, `template`) | `evaluate.py check`, `self-test` (537 controls), `test_evaluate.py` | any scenario run; baseline comparison; `codex exec --json` parser; metrics; fault injection of hook timeout/trust |
| CI | **none**: no workflow runs the validators | | add a CI job if wanted (not a Codex setting) |

## Deviations from the Blueprint (recorded, reversible)

- `reviewer` agent added; the Blueprint leaves review to `/review`. Six skills added beyond section 3.3 (`agents-skills-mvp.md` section 7).
- Tests live in `tools/control_plane/` as self-tests and `test_*.py` files, not a `tests/control_plane/` tree.
- Evaluation harness grades recorded runs and prints `codex exec` commands for the operator; it never runs Codex (Blueprint 6.1 describes a harness that drives `codex exec`; that needs paid runs and an event parser).
- `codex exec` has no `--ask-for-approval` option in 0.166.0 (Blueprint 6.1 says to pass it); `plan` omits it and notes unattended escalations fail.
- Nested `AGENTS.md` (`.codex/hooks/AGENTS.md`) holds review rules for cloud review; per the Blueprint's reading, local sessions load nested files only along the launch path, so it is inert locally unless Codex is launched there.

- Hook handlers were all added in one pass, not one at a time as BLUEPRINT 4.4 recommends; `commandWindows` was written before the Windows hook shell was established (BLUEPRINT 4.6), so it is unverified.
- Hook failure semantics: the old capability-register fallback said blocking hooks should exit 2 on their own internal errors; the delivered `PreToolUse` handler fails open instead (exit 0), because the documented contract does not make a hook's own error a guaranteed denial and the matcher cannot evaluate malformed input. Oversized or too-nested commands are denied. Treat this as an open design decision for the owner.
- No deployment skill or agent exists beyond explicit-only `release-readiness`; deploying is operator-controlled by design. Database/schema work routes to `backend-data-development` (implicit) and the `migration_engineer` agent; `dependency-migration` is explicit-only.
- The autonomous `reviewer` path depends on spawning by role (unverified; PR #14 conflict C14).

## Remaining external setup (all `BLOCKED: operator` unless noted)

1. Trust the project and review the seven hook registrations in `/hooks` (`hooks.md`).
2. Enable **Automatic review** for the GitHub repository in Codex settings (`code-review.md`); optional security review.
3. Run `live-assessment-full.md` and `live-assessment-agents-skills.md`; send back transcripts.
4. Decide whether to add execution rules (Phase 4.3) once the in-sandbox question is answered.
5. Decide whether to add CI that runs the validators and self-tests (static; no Codex needed).
6. Phase 1 operator checks from earlier slices (O-A, O-B, O-I, O-J).

## Known risks that decide usefulness

R-1 shell-less agents may not read files; R-2 routing and over-delegation are unmeasured; R-3 project trust gates config, hooks, agents and skills; R-4 each spawned agent is a paid run; hooks can fail open and are skipped until trusted; the `Stop` gate can race the async evidence write once; the PR #14 conflict C14 (no agent selector in the rendered `spawn_agent` schema) contradicts same-day renders here and is unresolved (`agents-skills-mvp.md` section 5).
