# Release qualification matrix

First derive mandatory requirements from repository release policy, user-defined target, support contract and CI configuration. This is a **candidate gate inventory**, not universal requirements. A risk-based gate becomes required when the change or the authoritative project policy demands it. Do not infer `PASS` from absence of changes without inspecting the diff.

| Gate | When applicable | Acceptable observations | Frequent false positive |
|---|---|---|---|
| Candidate provenance and artifact | Always | Immutable SHA and artifact digest; provenance and reproducible artifact linkage | Green job for another commit or different build flags |
| Required CI checks | When project declares | Check IDs, SHA, jobs, terminal conclusions, logs as needed | PR-level green badge without job attribution |
| Build/package | When releasable binaries/images/packages | Build success against candidate and required variant(s); artifact manifest | Local build of dirty tree claimed as release build |
| Automated tests and static checks | Project-required and changed code surfaces | Commands or CI IDs, exit codes, relevant coverage and variants | Small subset called full suite |
| Compatibility and interface | Changed public interfaces/support matrix | Consumer tests, version matrix, breaking-change approval, explicit evidence | Semver inference in lieu of consumer check |
| Schema/data migrations | Changed persistent state | Idempotency, forward/rollback or restore proof in safe isolated data, downtime/data-loss review | Unexecuted rollback script treated as proof |
| Security/supply chain | Changed dependencies, auth, secrets, build chain, or required by policy | Applicable security gates, dependency/license review, credential scanning without exposing secrets | Tool not available counted as clean scan |
| Configuration and deploy prerequisites | Changed environment/runtime needs | Environment matrix, required secrets by *name only*, deployment config compatibility | Assuming staging equals production |
| Release notes/documentation | User-facing changes or project policy | Versioned notes, migration/upgrade notices and support impact | Changelog exists but omits breaking changes |
| Operational readiness | Service/production release | Monitoring, alerts, rollout controls, incident owner and rollback/restore evidence | Rollback document without executable/authorized path |
| Scope/change hygiene | Always | Compare candidate with intended base; changed files and release content traceable | Clean local tree claimed as proof SHA contains only intended changes |

For every gate capture: `Requirement | Classification (required/advisory/N/A) | Status (PASS/FAIL/UNKNOWN/N/A) | Evidence identity (SHA/digest, job, command, result) | Limitations | Owner`. Only a required gate can block readiness. Advisory risk can become release-stopping if concrete impact violates an authoritative release constraint; explain why.

A failure with enough evidence to prove `NOT READY` is sufficient for a stop; further investigation may identify the remedy but is not needed to justify the gate. A `BLOCKED` decision is not a euphemism for failure: reserve it for insufficient evidence or inaccessible qualification steps with no established disqualifying failure.
