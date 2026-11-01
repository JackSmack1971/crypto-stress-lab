# Review evidence and divergence protocol

## Reviewer packet

Include task ID; repository; base/head and any working-tree digest; intended files and exclusions; acceptance criteria and non-goals; applicable repository constraints; focused verification outputs; authorization limits. Prefer line-specific findings supported by triggering inputs or contracts over speculative broad commentary. Review untracked candidate files explicitly where relevant.

## Finding record

Use stable ID, candidate identity, path/line, severity, defect class, contract violated, input/trigger, expected vs observed behavior, reproduction or inspectable evidence, provenance (`introduced`, `pre-existing`, `unknown`), disposition, and rationale. Confirmed = evidence supports an actual defect; rejected = counter-evidence demonstrates no defect; unresolved = cannot yet adjudicate. Accepted risk requires authorized owner decision; it is not equivalent to fixed.

## Failure and decision branches

| Condition | Required response |
|---|---|
| Reviewer unavailable or not independent | Report missing independence; use preliminary self-inspection only; no independent gate claim |
| Candidate changes during review | Record new identity; invalidate any clean verdict for old identity; retain task ID and pass budget |
| Existing repository ledger or cap | Follow authoritative repository policy; do not create competing task/budget records |
| Missing base, diff, relevant file or acceptance criterion | Inspect local evidence; if irrecoverable stop with incomplete scope |
| Tests fail before edit | Establish baseline where safe; distinguish baseline failure from introduced behavior |
| Flaky or inconclusive tests | Repeat focused check when justified, capture seed/environment; do not label pass without evidence |
| Source/generated mismatch | Locate authoritative generator; change source and regenerate only if permitted; otherwise stop |
| Disputed security or privacy finding | Keep open pending reproduction or authorized owner resolution; do not expose secrets in evidence |
| Proposed fix conflicts with architecture/compatibility | Explain competing choices and stop for owner decision |
| Fix would touch unrelated user changes | Avoid overwrite; request integration decision when inseparable |
| Review passes exhausted or ledger missing/corrupt | Stop with open results; never relabel/reset to gain another pass |
| External side effect (PR, merge, deploy, release, push) | Require separate explicit authorization and appropriate gates; skill never grants it |

## Re-review discipline

Deduplicate by defect identity and evidence; re-examine changes since last review plus affected interfaces. A previously rejected finding can reopen only with new evidence. Preserve the original finding ID and reasoning. Scan related call sites only when their defect class plausibly applies; avoid turning the repair into an unsolicited repository-wide refactor.

## Completion evidence

Sufficient: exact final candidate identity, all blocking material findings resolved or explicitly identified as open, independent review record, applicable tests/checks with results, inspected final diff, and a remaining-risk/approval report. A clean model review does not establish merge eligibility; branch protection and human approvals are separate enforceable controls.
