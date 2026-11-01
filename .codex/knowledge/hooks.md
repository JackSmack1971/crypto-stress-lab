# Hooks — CODEX PRIME

Delivered on branch `mvp-agents-skills` (BLUEPRINT.md section 4.4, 4.5, 4.6). Source for every contract below: `https://learn.chatgpt.com/docs/hooks`,
read 2026-10-31 (documentation claims). Tested Codex build: `codex-cli 0.166.0`. **No hook has been run by Codex**: nothing here is runtime-verified.
Status: static PASS (`python -I tools/control_plane/test_hook_policies.py`, 43 tests, my run, not independently reproduced); Phase 4 stays PARTIAL.

## What is delivered

`.codex/hooks.json` (one representation for this layer; `config.toml` defines no `[hooks]`) registers six handlers, all `command` type, stdlib Python,
no network, no writes except `execution_evidence.py` under `.codex-runtime/results/`.

| Handler | Event (matcher) | Enforcement point | What it does | What it cannot do |
| --- | --- | --- | --- | --- |
| `session_context.py` | `SessionStart` (`startup\|resume\|clear\|compact`) | Advisory context | Injects a short invariant paragraph; on `compact`, re-injects the newest `.codex-runtime/state/*.md` (capped at 6,000 chars, labeled as a saved summary) | Cannot reconstruct state nobody saved; never blocks |
| `pre_tool_policy.py` | `PreToolUse` (`Bash\|apply_patch`) | Hook (explicit denial, fails open on error) | Denies a narrow list: `git clean` (not dry-run), `reset --hard`/`--merge`, forced or path `checkout`, forced `switch`, `restore` of the work tree, `stash`, `branch -D`, `--no-verify`, forced or deleting `push`, recursive deletes outside generated dirs, codex bypass flags, commands that name `.codex/auth.json` or a `CODEX_HOME` auth.json (a bare `cat auth.json` after a `cd` is not seen); patches touching `.env*` (not `.example`), `.codex/{hooks,rules,config.toml,hooks.json}`, `.git/` | Not a shell parser. Deep wrapping (more than 5 levels is denied; hidden interpreters such as `python -c`, `sh` fed by a pipe or here-string, abbreviations like `git reset --ha`, and `git $(echo reset) --hard` are not seen), variables, substitution, scripts that delete indirectly, other tools, and hosted tools are not seen. Errors and malformed input let the call proceed |
| `permission_policy.py` | `PermissionRequest` (`Bash\|apply_patch`) | Hook (deny-only) | Denies escalations the project never accepts (same list, plus any command text that targets hooks/rules/config) | Runs only when Codex is about to ask for approval. Never returns allow, so the normal prompt or `auto_review` decides the rest |
| `execution_evidence.py` | `PostToolUse` (`Bash`, `async`) | Control-plane record | Appends `{schema_version, session_id, turn_id, tool_use_id, tool_name, command_class, exit_code, timestamp}` to `.codex-runtime/results/<session_id>.jsonl` | Stores no command line, output or environment. Exit code is `null` when the response shape is unknown. Not proof a test was meaningful |
| `subagent_contract.py` | `SubagentStart`, `SubagentStop` | Hook (context + one continuation) | Start: injects delegation rules. Stop: sends a subagent back **once** when its last message names none of the five statuses | Cannot check that a status is honest; `continue:false` cannot stop a start |
| `completion_gate.py` | `Stop` | Hook (one continuation) | Continues **once** when the final message claims passing tests and `.codex-runtime/results/` holds no `test`-class command for this `turn_id` | Does not judge correctness; async-write race can cause one unnecessary continuation; wording heuristics have false negatives |

`command_class` is a coarse heuristic (`test`, `build`, `lint`, `git-read`, `git-write`, `other`); a custom test runner can be classed `other`.

## Failure behavior (design; fixture-tested offline, not runtime-verified)

| Condition | Behavior |
| --- | --- |
| Malformed or oversized stdin (over 1 MB), non-object JSON | `pre_tool_policy`, `permission_policy`, `execution_evidence`: exit 0, no stdout, stderr note (PreToolUse then proceeds; documented). `session_context`, `subagent_contract`, `completion_gate`: exit 0 with valid JSON (`SubagentStop` and `Stop` require JSON on stdout) |
| Internal exception | Same as malformed. Handlers never exit 2 on their own errors. Oversized (over 200,000 characters) or too deeply nested (over 5 unwrap levels) shell commands are **denied** by `pre_tool_policy.py`/`permission_policy.py` because they cannot be evaluated |
| Timeout / missing interpreter / nonzero exit from the interpreter | Decided by Codex, not the handler. Documented for `PreToolUse`: errors and timeouts do not block the tool. Not exercised |
| Unsupported output fields | Handlers emit only `hookSpecificOutput` (`permissionDecision:"deny"` + reason; `decision.behavior:"deny"` + message), `decision:"block"` + `reason`, `additionalContext`, or `{}`. Tests assert `ask`, `updatedInput`, `suppressOutput`, `stopReason` and `allow` do not appear in the sources |
| Loop risk | `Stop` and `SubagentStop` return `{}` when `stop_hook_active` is true: at most one continuation |

What is documented and what is inferred: the hooks page states that a `PreToolUse` callback error, timeout or malformed response can fail the hook without blocking the tool (stated in its managed-hooks section) and that unsupported output fields fail the run and continue the call. That a **command** hook that crashes, times out or exits with a code other than 2 behaves the same way is an inference; it is unobserved here.

A guaranteed denial for a required protection must come from the sandbox, approvals, or an execution rule (not delivered); a hook can be skipped untrusted, can fail open, and does not see hosted tools.

## Operator trust flow (BLOCKED: operator)

1. Read the handler sources and `.codex/hooks.json` (the fixture tests are `tools/control_plane/test_hook_policies.py`).
2. Trust the project if you choose to (user config: not done here).
3. Start Codex in the repository; at startup it should warn that hooks need review. Open `/hooks`, inspect each of the seven registrations, and trust them. Every edit to a registration changes its hash and requires re-review.
4. Never use `--dangerously-bypass-hook-trust`; nothing in this repository does.

Until trusted, the hooks are skipped and the system behaves as if they were absent (the documented behavior; unobserved here).

## Windows

`command` uses `$(git rev-parse --show-toplevel)` (POSIX). `commandWindows` uses `powershell -NoProfile -Command "py -3 -B (Join-Path (git rev-parse --show-toplevel) '.codex/hooks/<name>.py')"`. Which shell and launcher Codex uses on native Windows for hooks is **unverified**: if `python3`/`py -3` is missing, or the shell differs, the hooks fail without blocking (SessionStart, PreToolUse). The blueprint's alternative is to run Codex in WSL2. `.gitattributes` keeps `*.py` LF. Handlers run with `python3 -B` / `py -3 -B` so they never write bytecode under `.codex/`.

Codex runs at most eight background hooks concurrently per session (documented); this project registers one async hook.

## Not delivered

`UserPromptSubmit`, `PreCompact`, `PostCompact`, `SessionEnd`, `Interrupt`; `mcp_tool` handlers; `.codex/rules/execution.rules` (Phase 4 rules need `codex execpolicy check` cases and an answer on whether `forbidden` applies in-sandbox); `platform-support.md`; real-event runs; the trust-behavior, forced-`/compact`, protected-path and timeout runtime checks of BLUEPRINT 4.7.
