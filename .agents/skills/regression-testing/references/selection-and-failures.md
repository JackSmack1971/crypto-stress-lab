# Test selection and failure triage

## Selection by consequence

| Changed surface | Minimum evidence to consider | Expand when |
| --- | --- | --- |
| Pure local behavior | Targeted unit tests for new and preserved contracts | Callers depend on undocumented assumptions or tests are weak |
| Shared/public API | Consumer-facing compatibility cases and affected callers | Contract spans multiple packages or schema/serialization boundaries |
| Persisted schema/data | Existing-data compatibility, migration/backward-read cases | State is irreversible or deployment/rollback compatibility is at issue |
| Async/concurrency | Ordering, cancellation, retry, race-sensitive invariants | Timing/interleaving could invalidate local-only evidence |
| Auth/security | Allowed and denied paths, privilege boundaries, unintended side effects | Consequences require additional independent review |
| External integration | Contract fixtures/fakes then authorized integration checks | Local test doubles cannot establish provider compatibility |

Select the narrowest sufficient suite. Use the repository's required checks even if broader; explain additional cost/risk before introducing new runners or external operations. Avoid fake certainty from mocks or coverage statistics.

## Failure classification standards

- **Introduced:** comparative or causal evidence ties the failure to this change.
- **Pre-existing:** the same relevant failure is observed in a comparable baseline or supported historical run, with meaningful configuration differences accounted for.
- **Flaky:** repeated controlled runs yield different outcomes with no intervening relevant change; preserve the failed attempt and investigate possible timing/ordering assumptions.
- **Environmental:** a concrete missing dependency, permission, infrastructure or configuration prevents meaningful execution. Do not call this a product pass.
- **Unresolved:** evidence cannot distinguish the above. Prefer this over an unsupported attribution.

A failure in a baseline may coexist with a new regression; baseline classification does not waive risk. For unsafe baseline checkout or unavailable build infrastructure, mark the comparison unperformed, report the missing evidence, and stop or use safe alternate verification.

## Stop/escalate

- **Verified:** relevant contracts independently checked with observed passing results, mandatory checks satisfied, relevant failures resolved or conclusively outside scope, and no critical gaps.
- **Not verified:** changed contract demonstrably fails or a mandatory acceptance criterion is unmet.
- **Inconclusive:** required evidence unavailable, unresolved relevant failures, or checks cannot safely run.
- Escalate before touching production/integration accounts, deleting state, changing CI gates, or broad destructive cleanup.
