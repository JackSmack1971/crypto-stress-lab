# Anthropic review principles — CODEX PRIME transfer assessment

**Source:** Addy Osmani, Morgan Westlee Lunt, Qing Wang, *How the Claude Code team does code review*, October 15, 2026, https://claude.dev/blog/solving-code-review-at-anthropic/. **Interpretation date:** October 31, 2026. These are published observations about Anthropic's internal workflow, not validation of this package or a native Codex implementation.

## Highest-value directly transferable ideas

| Principle from the article | CODEX PRIME application | Enforcement / evidence limit |
|---|---|---|
| Verification before human attention | Keep executed tests, focused checks, diff and fresh-context reviewer as distinct recorded evidence | Never claim unexecuted checks passed; native reviewer is advisory |
| Risk-adaptive review | Existing review-policy path floors and evidence matrices govern local readiness | GitHub CODEOWNERS, branch protection, human approvals and merge queue require independent hosting setup |
| Review convergence | Use existing review ledger's 3-pass cap; re-review repairs, deduplicate, escalate persistent findings | State is local and user-modifiable, not a security guarantee |
| Findings are high-signal and verifiable | Require triggering state and reproduction, classify introduced vs pre-existing, avoid style noise | Other model agreement alone does not prove defects |
| Learn from incidents and false positives | Capture adjudicated feedback and create independently labeled incident/revert eval fixtures | New feedback script reports counts, *not recall* without known misses or full ground truth |
| Reversibility and observability | Ask for rollback strategy and blast radius in PR template | No native deployments, feature flags, telemetry, or rollback operations added |
| Human judgment reserved for consequences | Maintain protected config/CI/agent paths and escalate unresolved security and authority decisions | Machine review never counts as a human approval |

## What was implemented in this pass

- `review-and-repair/SKILL.md`, `references/review-loop.md`: converge on existing ledger round count; evidence-first triage, no repeats, incremental re-review, class-level fixes.
- `.codex/agents/reviewer.toml`: explicit origin classification and high-signal findings instructions.
- `.github/pull_request_template.md`: risk, failure-path testing, rollback, blast radius and unresolved findings.
- `tools/control_plane/review_feedback.py`: independently curated feedback aggregation, no invented accuracy/recall; `test_review_feedback.py` checks the pure logic; CI command added.

## Deferred: operational and research gates

1. **Actual continuous AI review:** does not arise from a policy document. Enable and qualify Codex PR review or a pinned GitHub workflow, verify permissions, costs, credentials and actual PR comments on a test PR. No remote changes were made.
2. **Protected approvals / merge queue:** set real CODEOWNERS and GitHub branch rules based on actual owners, required checks, current head SHA and human authorization; do not invent team identities or merge authority.
3. **Incident eval quality:** construct labeled PRs with known regressions, fix-forward and clean negative controls; measure true-positive detection, false positives, reviewer time, rounds-to-pass, reverts and incidents. Current static scenarios are not this dataset.
4. **Release rollback:** choose product-specific deployment/flags, stage rollout and collect real downstream health signals before automating rollback.
5. **Review policy tuning:** benchmark low/medium/high classifications and review model behavior on real diffs before altering required humans or auto-merge policy.

**Boundary:** Anthropic's reported throughput/revert figures and review consensus processes are observations about its own systems. Do not assume equivalent effectiveness for Codex; independently reproduced evidence matters more than majority-model votes. No runtime enforcement or hosting-side protection was proven in this pass.
