# Status and failure decisions

Use a repository's explicit status contract where applicable; identify discrepancies rather than silently overriding it. Otherwise apply these portable definitions.

| Overall status | Observable condition |
| --- | --- |
| COMPLETE | Every material acceptance criterion and required review is verified; no unresolved material contradiction. |
| PARTIAL | Some requirements are supported, but outstanding checks or deliverables remain and progress can continue within the authorized task. |
| BLOCKED | Required evidence cannot be obtained without a dependency, decision, credential, unavailable capability, or authorization; state the precise blocker. |
| FAILED | Evidence establishes that a mandatory criterion fails or that the requested result is incorrect; separate new from baseline failures where possible. |
| CANCELLED | User or authoritative execution process cancelled the work; do not infer cancellation from a timeout. |

## Claim labels

- **VERIFIED**: direct, relevant, inspectable observation supports the claim under the claimed revision and environment.
- **FAILED**: direct observation contradicts the claimed outcome.
- **UNVERIFIED**: evidence missing, indirect, stale, incomplete, or unrun; absence of evidence is not evidence of failure.
- **CONFLICTED**: credible observations disagree or the criterion/authority conflicts; seek a discriminating check, otherwise leave unresolved.

## Failure branches

| Condition | Required handling |
| --- | --- |
| Tool or test runner missing | Identify the unavailable check; use equivalent evidence only when it actually proves the same claim. Otherwise UNVERIFIED and BLOCKED or PARTIAL. |
| Command exits 0 but assertions or target coverage are absent | Do not mark the behavior VERIFIED; inspect command output and test target. |
| Pre-existing test failure | Compare known baseline (if available) with current run; do not label newly introduced without evidence. Record attribution uncertainty. |
| Failed required check | Mark relevant claim FAILED; do not weaken or skip test to obtain green status. |
| Untracked, staged, ignored, or generated artifacts | Include relevant artifacts; distinguish known exclusions from omissions, and inspect source/generated consistency. |
| Diff contains unrelated pre-existing changes | Attribute by available provenance; preserve all work and flag attribution uncertainty. |
| Reviewer and executor disagree | Inspect their supporting artifacts; mark CONFLICTED until independently resolved. |
| No repository, no diff, or incomplete history | Use supplied artifact evidence and disclose coverage limitation; do not claim a clean diff. |
| Credentials, side effects, destructive operations, production checks | Do not initiate to complete this audit without specific authorization and appropriate controls; mark unverified. |
| Missing acceptance criteria or conflicting authority | Extract what is clear; identify the decision required, avoid manufactured criteria or completion. |
| Partial outage, timeout, or incomplete command output | Treat as inconclusive; retry only if safe, bounded, and decision-relevant. |
| Evidence from another agent, prior session, or cached log | Verify version, scope, authenticity, and observable artifacts before relying on it. |

A verification report itself never authorizes merge, commit, deployment, publication, cancellation, or independent review. Those actions follow the active instruction and permission hierarchy.
