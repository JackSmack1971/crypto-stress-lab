---
name: documentation-update
description: "Synchronize repository documentation after changes to behavior, APIs, configuration, CLI, schemas, or user-visible workflows. Use when an implementation diff or completed change may have made existing docs, examples, comments, or help text stale. Also use for explicit documentation-drift audits against current code. Do not use for standalone tutorials, editorial rewrites, planning-only proposals, or implementation changes where no documentation synchronization is requested or implied."
---

# Documentation synchronization

**Purpose:** reconcile descriptions of existing behavior with authoritative implementation evidence. This skill provides no authorization to change implementation code, publish docs, or perform external actions.

## 1. Establish the change and authority

- Read applicable `AGENTS.md` instructions and inspect Git status/diff (including staged changes); preserve unrelated edits. Identify the user's target change, branch/baseline, and affected interfaces. If no trustworthy change baseline exists, inspect the specified implementation surfaces and report that the inventory is baseline-limited.
- Distinguish **implemented**, **planned**, **deprecated**, and **unknown** behavior. Prefer current executable behavior and implementation/configuration over stale prose; treat tests as evidence of intended behavior, not proof that code ran. If code, tests, generated output, and authoritative specifications disagree, do not silently choose a winner: identify the inconsistency and withhold disputed claims.
- Discover documentation conventions and authoritative source-of-truth files in the repository before modifying docs. Do not replace repository policy with this skill.

## 2. Build a coverage inventory

- Trace each changed contract to its likely consumers: README, user guides, API/CLI references, configuration and environment examples, migration and compatibility notes, inline comments/docstrings, examples, help strings, release notes (only if repository convention or request requires them), and generated documentation sources.
- Search for old **and new** names, commands, flags, defaults, paths, behavior descriptions, aliases, and related concepts. When a diff is available, `python scripts/doc_candidates.py --repo . --base <ref>` can produce a *candidate* inventory; review it manually and do not infer exhaustiveness from its output. See `references/coverage-and-evidence.md` for search branches and evidence classifications when nontrivial.
- Maintain a compact ledger per affected contract: change, affected surfaces, decision (`update`/`checked-unchanged`/`not-applicable`/`blocked`), evidence. A negative search is not proof that no docs exist.

## 3. Apply the minimum documentation patch

- Update only statements affected by the change. Preserve authorial style, links, structure, pre-existing user edits, and generated-file conventions. Edit the source for generated docs and regenerate using the repository's documented command; never hand-edit generated outputs as the sole fix.
- Write actual current behavior, limits, prerequisites, errors and defaults. Avoid presenting future behavior as shipped, inferred examples as tested, or advisory controls as guarantees. Preserve necessary historical/migration distinctions rather than rewriting history.
- If an example requires secrets, external services, destructive operations, money, or production access, do not execute it merely to verify documentation. Use static checks or an approved isolated environment and mark residual uncertainty.

## 4. Verify claims and stop

- Independently check changed commands, paths, flags, defaults, API shapes, links and examples against authoritative source or safe execution. Prefer focused repository checks; broaden only when risk or a failure justifies it. Distinguish **source-checked**, **executed**, **unverified**, and **conflicted**. Running a command is not enough unless its result supports the claim.
- Review the final diff for unrelated edits, misleading deletions, unsupported claims, unintentional generated artifacts, and unresolved stale references. If checks fail, determine whether failure existed before the patch where feasible; do not alter unrelated code/tests to force success.
- Stop when each identified changed contract has a documented disposition and modified claims have supporting evidence or explicitly reported limitations. A blocked or conflicting claim prevents an unqualified completion declaration. Do not continue unrelated cleanup.

## Output

Report: (1) documents updated and why, (2) relevant documents checked but unchanged, (3) claim-to-evidence checks and command outcomes, (4) unresolved gaps/blocked or unverified claims. Identify scope/baseline limits. A delegated documentation agent may edit only assigned files; its claims and diffs still require independent review.
