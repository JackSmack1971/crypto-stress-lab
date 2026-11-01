# Verification and recovery branches

Load when executing, reviewing verification evidence, or encountering failures. Commands below are **examples only**: check the repository's manager, versions, flags, environment, and scripts before running.

## Independent evidence hierarchy

1. **Declared state:** manifest, constraints, overrides, workspace and optional/peer ranges.
2. **Resolved state:** lockfile/solver output shows selected concrete versions and integrity metadata where applicable.
3. **Reproduction:** supported clean or isolated install with locked/frozen resolution and no unexpected manifest mutation.
4. **Behavior:** affected import/load, type/build, unit and integration tests, dependent packages, CI/platform matrix as warranted.
5. **Scope:** final diff and generated files agree with changes, no unrelated modifications, rollback feasible for affected artifacts.

Examples (not universal, don't invoke indiscriminately):
- npm: `npm ci` for a lockfile-backed clean install; **warning:** removes existing `node_modules`. Use an isolated worktree/environment if destructive to current working state. `npm ls` can reveal resolution problems.
- Python/pip: inspect `pip check` for installed requirement incompatibilities, but do not mistake it for a reproducible lockfile verification. Use the repository's actual lock/constraints tool and isolated environment.
- Cargo: inspect `Cargo.lock` and run the repo's configured build/tests; do not casually rewrite lock entries by hand.
- Go: check module version and sums via existing module workflows and run the relevant test packages.

Do not install missing tools globally, change registries, weaken validation flags, or run installation scripts whose consequences have not been reviewed.

## Failure paths

| Observation | Required behavior |
| --- | --- |
| No official notes or target metadata | Record exact missing source; inspect authoritative alternatives; mark conclusions inconclusive where appropriate. |
| Baseline cannot reproduce due to network/tool outage | Stop claims of reproducibility; use local static evidence if useful, distinguish network failure from compatibility failure. |
| Lockfile conflicts with manifest | Use existing manager to resolve in safe environment; confirm the lock is correctly regenerated. |
| Tests fail in identical way before and after | Record a pre-existing failure; do not label post-change check PASS, and determine whether it blocks migration acceptance. |
| New test failure or type/API break | Minimize to impacted contract; patch or stop at checkpoint; do not hide by deleting tests. |
| Unexpected large resolver diff | Investigate transitive dependency cause and constrain scope or stop. |
| Unapproved command would touch external/production resources | Do not execute; present the bounded action, risk, and necessary approval. |
| Rollback cannot restore persisted state | Declare non-reversible; require approved restore/forward-fix procedure and recovery evidence. |
| Script/manager unavailable | Use other defensible evidence if available, clearly report which gate remains unverified. |
| Generated file differs from source | Re-run authoritative generator; if still divergent, block verification and investigate. |
| Changes overlap with unrelated user work | Do not reset; isolate attributable edits or stop for direction. |

A correct refusal, authorized escalation, or accurately labeled **UNVERIFIED** state is preferable to a fabricated green result.
