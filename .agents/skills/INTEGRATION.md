# Skill routing map

This is the single routing map for project skills and workflows. For operating rules and authority boundaries, see [`AGENTS.md`](../../AGENTS.md); this file does not duplicate them. Repository instructions are guidance, not proof that a skill, hook, or subagent is active at runtime.

## Application context

Crypto Stress Lab is a browser-only JavaScript application. It has no EVM or smart-contract component. Portfolio and stress calculations should remain deterministic and reproducible, use explicit units, document assumptions and limits, and keep data local without telemetry. Treat persisted and imported portfolio data as untrusted input and use XSS-safe DOM writes.

Inherited CODEX PRIME-era reference files under `.codex/knowledge/` are indexed in `.codex/knowledge/crypto-stress-lab-index.md`.

## Routing

| Work | Skill |
| --- | --- |
| Triage scope, consequence, and workflow | `task-triage` |
| Explore an unfamiliar repository area | `repository-recon` |
| Evaluate a consequential architecture choice | `architecture-design` |
| Implement a bounded authorized change | `implementation` |
| Diagnose an unexplained failure | `failure-analysis` |
| Select and run focused regression checks | `regression-testing` |
| Review trust boundaries and security risks | `security-review` |
| Analyze measured performance | `performance-analysis` |
| Design or diagnose integration tests | `integration-testing` |
| Verify completion claims and evidence | `evidence-verification` |
| Develop a product idea into a bounded specification | `idea-to-spec` |
| Implement frontend UI behavior | `frontend-development` |
| Implement backend or data behavior when present | `backend-data-development` |
| Synchronize documentation with behavior | `documentation-update` |
| Independently review and repair a material diff | `review-and-repair` |
| Prepare a local commit when explicitly requested | `commit-preparation` |
| Coordinate a multi-stage engineering task | `workflow-coordination` |
| Validate quantitative portfolio and stress calculations | `quantitative-risk-validation` |

## Explicit-only skills

Invoke these only when the user explicitly requests them:

- `dependency-migration`
- `release-readiness`
- `control-plane-audit`

The remaining skills above are eligible for ordinary routing when their descriptions match. Eligibility does not guarantee runtime invocation. Hooks and subagents are **configured, not runtime-verified** unless current-session evidence establishes otherwise.
