---
name: frontend-development
description: "Implement or modify frontend UI behavior in an existing web app: components, pages, forms, client state, responsive styling, and accessibility. Use for user-facing UI code changes requiring implementation and verification. Do not use for design-only mockups, standalone audits, backend-only changes, deployment, or documentation-only tasks."
---

# Frontend development

This skill exists to implement a user-facing frontend change when working in an existing web application's UI code. It does not grant new permissions or replace repository instructions.

## 1. Establish scope and baseline

- Read applicable `AGENTS.md` instructions, examine Git status/diff, target components, routing/state conventions, styles and tests. Preserve unrelated staged and unstaged changes.
- Identify the observable user behavior being changed, affected routes/components, supported browsers and viewports, and the smallest coherent change. Identify where data, design tokens, and generated files originate before editing.
- Determine whether validation already fails in the affected area before attributing a failure to this change. Record relevant existing failures or state why a trustworthy baseline could not be obtained.
- Use the existing framework, design system and package tooling; do not introduce libraries, rewrite unrelated UI, or modify generated output without the repository's authorized generation workflow.

## 2. Implement through an explicit behavior contract

- For each changed interaction, identify preconditions, user action, expected visible result, and recovery/invalidation behavior. Cover only applicable states: initial, loading, empty, success, validation failure, request failure, stale/partial data, cancellation, or disabled/submitting.
- Preserve semantic elements, focus order and accessible names. A visual control must have keyboard-operable behavior and an observable focus state. When modifying dialogs, menus, forms or asynchronous updates, consult `references/interaction-accessibility.md`.
- Preserve existing client/server boundaries and contracts. Never embed secrets in client bundles, bypass authorization, or silently change API request/response semantics. If the frontend requires a missing backend contract, document the dependency rather than inventing a production endpoint.
- Check layout behavior for changed areas at narrow and wide widths, overflow and long/localized content when relevant. For affected layout or styling, consult `references/responsive-visual.md`.
- Keep edits local and reversible. Treat new dependencies, broad design-system changes, exposed private data, and destructive migrations as decision boundaries requiring justification and, when appropriate, authorization.

## 3. Verify according to change risk

Choose the narrowest checks that can falsify the requested behavior, then broaden only for shared surfaces or observed risk. Use existing project commands, not assumed commands. Follow `references/verification-matrix.md` for check selection and evidence thresholds.

1. Run focused behavioral tests for changed logic and interactions; use user-observable assertions rather than implementation-only snapshots wherever possible.
2. Run affected lint/type/build checks according to repository tooling and scope. A green build alone does **not** verify UI behavior.
3. Where a safe browser or component-render environment is available, observe the changed route/component, exercise relevant interaction and failure states, inspect relevant console/runtime errors, and check narrow/wide rendering. Record the exact states and viewports observed. Never claim browser verification if only code inspection or tests ran.
4. Check important keyboard/focus and accessible-name behavior for modified controls. Automated accessibility checks are supplemental, not proof of complete accessibility.
5. Review the final diff for unintended changes, unexpected generated assets, dependency churn and weakened tests; explain intended snapshot or screenshot baseline updates before accepting them. Do not update snapshots merely to turn failures green.

## 4. Divergence and stopping

- If tests fail, compare with the baseline when possible; repair introduced failures in scope and report unrelated pre-existing failures separately. If attribution is uncertain, report it as inconclusive.
- If browser tooling is unavailable, use applicable component/integration tests and static checks, then explicitly mark runtime visual/interaction behavior unverified. Do not install a browser, add packages, or alter the environment solely for convenience.
- If behavior depends on unavailable services or credentials, use existing supported fixtures/mocks; do not pretend a mocked path proves live integration.
- If accessibility, supported-browser behavior, or architecture conflicts with the request, preserve the constraint and surface the choice rather than silently weakening it.
- Stop after the smallest requested slice has independent evidence, the final diff has been reviewed, and remaining verification gaps are explicit. Do not expand into aesthetic redesign or unrelated optimization.

## Completion report

Report (1) user-visible behavior changed, (2) files changed, (3) exact checks and their outcomes, including observed routes/states/viewports, and (4) blockers, regressions, and behavior not verified. Distinguish implemented, tested, observed, and inferred claims.
