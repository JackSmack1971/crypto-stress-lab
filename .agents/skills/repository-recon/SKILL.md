---
name: repository-recon
description: "Trace an unfamiliar repository area before planning a code change: locate entry points, runtime/data paths, contracts, ownership boundaries, and relevant tests when affected components are unknown. Use for impact discovery and change-boundary mapping; not for implementation, known-file fixes, standalone bug diagnosis, or broad architecture audits."
---

# Repository reconnaissance

**Outcome:** an evidence-backed map of the smallest plausible change boundary. This is read-only discovery; it does not authorize code edits, network calls, commits, or changes to external systems.

## 1. Establish the baseline

- Establish the repository root, current branch, `git status --short`, and applicable `AGENTS.md` / `AGENTS.override.md` instructions before inspecting task code. Preserve and identify pre-existing work; do not alter it.
- Write the task's observable entry point or behavior as a **search hypothesis**, not a conclusion. If the request already identifies the files, boundary, and relevant constraints, return control to the calling workflow; do not perform redundant recon.
- Prefer repository-provided indexes, manifests, and documented entry points. Treat comments, documentation, and names as leads until corroborated by implementation or tests.

## 2. Trace the minimum useful path

- Search from task-specific terms, symbols, commands, endpoints, events, or data artifacts. Inspect nearby definitions and uses. Follow only the producer → transformation → consumer edges needed to explain the requested behavior. For dynamic registration, generated code, dependency injection, or configuration-based routing, see [trace branches](references/trace-branches.md) **when encountered**.
- Record each decisive claim with a `path:line` (or inspectable command/result) and label it **observed**, **inferred**, or **unverified**. Do not treat search absence as proof that a component does not exist.
- Identify the likely source of truth; distinguish handwritten files from generated/vendor files and point to the generation source if known. Identify ownership from verified repository evidence, not presumed team names.
- Locate contracts crossed by a proposed change: inputs/outputs, interfaces, schemas, callers, error behavior, state changes, external boundaries, and tests. Prefer focused test targets and record commands only when established from repository configuration or documentation. Do not run commands with side effects; tests that write or contact external services require independent authorization.

## 3. Challenge the boundary, then stop

- Check at least one plausible alternative entry/path and one upstream/downstream dependency that could expand the proposed edit. If either changes the boundary, trace that edge; otherwise stop. **Do not escalate to a repo-wide scan by default.**
- A boundary is established only if entry path, behavior path, authoritative edit surface, affected contracts, relevant verification targets, and remaining uncertainty are accounted for. If evidence is inaccessible or contradictory, mark the boundary **provisional**, state the missing proof and narrow next investigation. Never claim complete coverage from partial searches.
- For missing files/tools, monorepos, stale docs, pre-existing failures, or dangerous discovery commands, apply [failure branches](references/failure-branches.md) **only as relevant**. Do not silently substitute guesses for evidence.

## Output contract

Return a compact **Recon Map**:

1. **Status:** established / provisional / unnecessary; baseline working-tree state.
2. **Observed path:** entry → key hops → effects, each with evidence links (`path:line`).
3. **Change boundary:** minimal source files/symbols and why; generated or owned boundaries when verified.
4. **Contracts and verification:** affected interfaces, callers, focused existing tests and evidenced commands; explicitly distinguish *located* from *executed*.
5. **Alternative checked and gaps:** other plausible path, counterevidence, uncertainty and narrow next step.

End after producing the map. Do not design or implement the change under this skill.
