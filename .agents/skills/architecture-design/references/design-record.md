# Architecture decision record — output contract

Use concise prose for an ordinary choice. Expand only where blast radius and unresolved uncertainty warrant it. Do not persist an ADR to the repository unless requested.

- **Status:** READY FOR OWNER REVIEW / CONDITIONAL / BLOCKED / NO ARCHITECTURE DECISION NEEDED. This is not an implementation validation status.
- **Decision question and scope:** intended outcome, design boundary, non-goals, and who owns approval.
- **Current state and evidence:** relevant paths/symbols/specs inspected; established invariants and impacted producers/consumers; conflicts and confidence.
- **Decision drivers:** hard constraints, tradeoff preferences, and assumptions separated explicitly.
- **Alternatives:** smallest viable change, materially distinct feasible options, and no-change if relevant; common comparison criteria, violated constraints, and rejection reasons.
- **Recommendation:** selected approach and why it beats alternatives under stated assumptions; what would change the choice.
- **Consequences:** boundary/interface/data/authorization effects, compatibility, staged migration, rollout/rollback, dependencies and operational risks (as applicable).
- **Verification contract:** acceptance conditions; focused unit/contract/integration/migration/performance/security checks relevant to risks; independent evidence required; distinguish already observed checks from future tests. Do not prescribe invented repository commands.
- **Open decisions:** named owner decision, missing evidence, impact, and safe stopping point.
- **Implementation boundary:** smallest coherent implementation slices and what remains explicitly unauthorized.

Readiness check: no hard-constraint violation; affected contracts enumerated within the scope; proposed validation would be capable of falsifying the design; unresolved high-consequence decisions surfaced rather than silently decided.
