# Compatibility, supply-chain, and rollout decision guide

Load this reference when a migration crosses a major, runtime, API, peer/transitive, security, licensing, generated-output, or stateful boundary. This file supplies decision criteria, **not** universal version claims.

## Establish authoritative evidence

- Prefer version-scoped official upgrade guides, release notes, compatibility tables, source changes, ecosystem package metadata, and official advisories. Check that the cited range actually includes the target. Record where documents conflict, are inaccessible, or lack version specificity.
- Resolve target compatibility across: primary runtime versions; OS/architecture; compiler/build system; host framework/plugins; peer dependencies; optional features; platform images; public API consumers; external integrations.
- Inspect dependencies being removed, newly introduced, changed in transitive resolution, and possibly replaced by forks. Distinguish declared constraints from what the lock/resolver actually selects.
- Examine lifecycle/postinstall scripts, supply-chain authenticity and provenance where supported, licensing policy, documented CVEs/security fixes, and effects of bypass flags. Do not disable audit or strict verification simply to obtain a green install.

## Decision points

| Condition | Decision or response |
| --- | --- |
| Target incompatible with supported environment or contracts | Stop or request an explicit platform/architecture decision; do not silently expand scope. |
| Two packages require jointly incompatible peer constraints | Search official supported compatibility set; avoid `--force`/peer bypass as a default. |
| Upgrade requires generated code changes | Identify authoritative generator/version, regenerate, and test source-to-output consistency. |
| Existing tests fail before edits | Preserve baseline evidence; attribute only new failures to migration unless old failures block validation. |
| Transitive version unexpectedly changes | Explain resolver reason and impact; constrain only with repository-sanctioned mechanisms. |
| Release notes absent, conflicting, or unclear | Mark an evidence gap, inspect source/diff and test behavior; escalate unresolved consequential choices. |
| Runtime or toolchain version impacts CI/deploy | Align supported matrix and images only where justified; validate representative supported targets. |
| CVE or malicious package risk | Verify identity and advisories from primary sources; stop execution of suspect code until assessed. |
| API or wire format affects outside consumers | Define compatibility window, dual-read/write or staged rollout if required; obtain owner approval before external rollout. |
| Database or persisted format changes | Verify backup, recovery test feasibility, forward/back compatibility, and ownership of schema migration; no automatic live execution. |
| Rollback requires irreversible state conversion | Treat it as forward-fix or restore-from-validated-backup, not `git revert`; stop for explicit authorization. |
| Existing dirty worktree overlaps migration | Preserve it and request scope resolution; do not overwrite or reset. |

## Staged changes

Favor a compatibility bridge when old and new runtime, serialized data, or consumers must coexist. Define entry criteria, telemetry or other observable health evidence, failure thresholds, rollback window, and ownership. A plan for a production rollout is **not** permission to execute it. Do not claim security issues fixed merely because a package version changed; confirm the resolved tree and applicable vulnerability status.
