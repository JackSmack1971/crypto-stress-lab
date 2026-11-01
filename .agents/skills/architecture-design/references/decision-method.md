# Decision comparison method

Use when alternatives cross multiple boundaries or the choice depends on contested nonfunctional qualities. This is a structured reasoning aid, not an automatic scoring formula.

1. Define decision drivers and tag each **hard constraint**, **preference**, or **unknown**. For each driver name the authoritative source or owner.
2. Construct a common-option matrix with columns: option, hard-constraint fit, component/interface impact, migration/rollback, operational risk, evidence confidence, and distinguishing tradeoff. Add security, latency, availability, cost, or complexity columns only if decision-relevant.
3. Use **pass / fail / unknown** for hard constraints. Unknown is not pass. Use ordinal tradeoff labels only with explicitly stated observations and assumptions; never manufacture numeric rankings or throughput estimates.
4. Include smallest change and a materially distinct alternative if feasible. Record why each rejected option loses; identify if one is a valid fallback under different conditions.
5. For data and compatibility decisions, trace: writer -> storage/wire format -> reader; old/new clients; version/rollback; partial deployment; failure recovery. Explicitly identify irreversible transformations and dual-write/replay requirements if applicable.
6. For boundary or security decisions, trace principals, trust boundaries, authorization enforcement point, secret/data flow, and failure behavior. Proposed controls are not proof of enforcement.
7. Specify the smallest observation or prototype that could falsify the preferred option, if uncertainty materially affects the choice. Design work cannot claim experimental evidence that has not been collected.
8. Reconcile rejected alternatives and critical unknowns before declaring readiness. If options cannot be discriminated with current evidence, return a conditional decision with an evidence-gathering plan rather than false certainty.
