# Code review and automatic PR review — CODEX PRIME

Sources (documentation claims, read 2026-10-31): `https://learn.chatgpt.com/docs/code-review`, `https://learn.chatgpt.com/docs/third-party/github`. Tested build: `codex-cli 0.166.0`, where only `codex exec review` and the local `/review` command were checked to exist; **no review has been run**. Everything below about cloud review is documented behavior that depends on an account setting this repository cannot control.

## Three review paths

| Path | Where it runs | What this repository provides | Status |
| --- | --- | --- | --- |
| Local `/review` | Codex CLI, in the user's checkout; presets: against a base branch, uncommitted changes, a commit, custom instructions | `AGENTS.md` and `## Code Review Rules` are in the project context; `review_model` is a user `config.toml` choice | documented; unverified here (paid session, interactive) |
| Spawned `reviewer` agent | Inside an agent task, when the main agent delegates an independent diff review | `.codex/agents/reviewer.toml` (read-only by instruction; not enforced). A model cannot invoke `/review`, so autonomous tasks use this | static only; spawning unverified |
| Codex cloud review of a GitHub PR | Codex service: automatic on PR events, or a PR comment `@codex review` | Repository guidance in `AGENTS.md` files and `.github/pull_request_template.md` | documented; **BLOCKED: operator** (account setting) |

Review output is an advisory input. It does not replace tests, branch protection or required human approval, and it never authorizes a commit, push, merge or deployment.

## Review rules (documented location)

Per the GitHub integration page, Codex searches the repository for `AGENTS.md` files and follows the applicable `## Code Review Rules` section: repository-wide rules in the root file, narrower rules in a nested file next to the code they govern, with `###` headings to group checks. This repository has:

- root `AGENTS.md`: authority and claims, agents/skills/hooks, tests and scope
- `.codex/hooks/AGENTS.md`: hook-contract checks (unsupported output fields, double continuation, secret logging)

Per the Blueprint's reading of instruction discovery (not re-verified), a nested `AGENTS.md` loads in a local session only along the launch path, so `.codex/hooks/AGENTS.md` mainly serves cloud review, which the page says applies the nested guidance that covers each changed file.

Design choices, following the page's guidance: a few consequential repository-specific rules, each with a safe path where one exists, nothing mechanical (formatting, lint, and the validators stay in CI or the local checks). `python -I tools/control_plane/validate_review_rules.py` checks the structure; it cannot check that Codex applies the rules. Cloud review flags only P0 and P1 issues on GitHub (documented), so P2/P3 style findings come from `/review` or the `reviewer` agent.

## Operator setup to enable automatic PR review (BLOCKED: operator)

The repository cannot enable this; a workflow file or a committed setting would not turn it on, and none is provided. The operator does the following (documented steps, not performed or verified here):

1. Connect the GitHub repository to Codex (the page points to the Codex Cloud (Legacy) environment setup for legacy integration). The operator needs GitHub push or admin permission for the repository settings.
2. Open `https://chatgpt.com/settings/code-review`, choose the repository, and turn on **Automatic review** under **Review code**. Per the page, **Automatic review** under **Personal preferences** applies to repositories with code review enabled, and **Review trigger** chooses when reviews run.
3. Optional: **Auto security review** and `@codex security review` for the in-depth security pass (research preview per the page; account-dependent).
4. Verify on a representative PR: comment `@codex review`; Codex reacts and posts a standard GitHub review. Refine `## Code Review Rules` from the findings; narrow or remove rules that create noise.

Documented caveats to carry into the decision: `@codex fix ...` and any other `@codex` mention starts a Codex cloud task that **can push to the PR branch when it has permission**. That is an externally visible, write-capable action; keep it a deliberate operator choice. Comments from reviews appear on GitHub and in Code Review; they are data, not instructions to this repository's agents.

## What a PR should carry

`.github/pull_request_template.md` asks for the change summary, the commands run with outcomes, what is unverified, and risks. It deliberately has no checkbox for a model's approval.

## Not verified

Whether cloud review reads these `AGENTS.md` sections for this repository; how well the rules steer findings; trigger settings; `review_model`; local `/review` behavior with a dirty tree. Test with the steps above and the live sheet (`live-assessment-full.md`, part D).
