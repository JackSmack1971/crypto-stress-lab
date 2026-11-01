# Migration evidence record

Use this structure in the final response or an existing repository-approved planning artifact; do not create a new file in the target repo unless asked or required by its process.

| Field | Evidence / decision |
| --- | --- |
| Mode and boundaries | assess / plan / implement / verify; authorized local changes, external changes excluded |
| Target | package identity; current and target exact versions; ecosystem; motivation |
| Baseline | commit, dirty-tree constraints, resolved versions, passing and failing tests |
| Authoritative sources | official URLs; relevant versions; specific breaking changes, dates/uncertainty |
| Dependents and compatibility | impacted code/config/CI/platform/public consumers; risk classification |
| Migration steps | dependency order; atomic coupled sets; files affected; checkpoint criteria |
| Evidence per step | command, environment, exit status, observed result, version verification |
| Rollback | reversible artifacts; commands or recovery procedure validated; state/consumer limits |
| Approval gates | destructive, shared, external, secret, publication or deployment actions held pending owner approval |
| Final state | VERIFIED / PARTIAL / BLOCKED / UNVERIFIED; remaining risk and missing evidence |

**Evidence rule:** Record observed results, not proposed commands as if executed. A rollback plan is not a demonstrated rollback test. Missing proof must not become a silent PASS.
