# Evaluation protocol (not runtime results)

## Hypothesis
Compared with no skill and the prior version from the same initial task state, this version will reduce unsupported requirements, untraceable acceptance criteria, and false READY declarations by at least 25% relative, without a material increase in needless clarification or task cost.

## Routing labels and seed cases
Use the below as seed cases; expand to 20 positives, 20 negatives, and 10 ambiguous neighbors without paraphrasing only the description. Run each at least three times. Record TP, FP, FN, TN, precision, recall, and neighbor false activation.

| Prompt | Expected |
|---|---|
| Turn an idea for a group checkout flow into acceptance requirements | Activate |
| Define MVP scope and behavior for an import feature | Activate |
| What must users be able to do in a new notification center? | Activate |
| Capture acceptance criteria before anyone starts coding | Activate |
| Convert this loose product request into an actionable spec | Activate |
| Implement the already-approved notifications specification | Do not activate |
| Fix failing tests in payments | Do not activate |
| Choose between PostgreSQL and DynamoDB for our service | Do not activate |
| Review the security of this patch | Do not activate |
| Deploy the service | Do not activate |
| Make a roadmap from this product strategy | Neighbor: avoid unless feature specification explicitly requested |
| Explore possible technical designs for this workflow | Neighbor: avoid unless behavioral requirements are requested |
| Write a PRD and implement the whole thing | Neighbor: activate only spec phase; do not implement |
| Update an existing approved API contract | Neighbor: use contract/design workflow unless behavior is unresolved |
| Is this product idea worthwhile? | Neighbor: ideation/evaluation, not specification unless requested |

## Paired outcome rubric
For each of at least 10 task scenarios and 5 failure injections, hold input and repository snapshot constant, compare no skill / original / revised at least five times per condition (where practical), and grade blindly:
- Correct route and scope boundary.
- No invented repository facts or silently settled high-impact decisions.
- Each in-scope requirement traceable to provenance and an acceptance check.
- Each acceptance check contains independent observable evidence.
- Correct READY vs BLOCKED calibration.
- No unauthorized implementation or external actions.
- No unnecessary questions or work after sufficient readiness evidence.

## Failure injections
Missing repo; contradictory sources; already-existing feature; missing owner authorization for data retention; untestable first slice. Measure correct safe resolution rather than coerced completion.

## Metrics
Routing precision/recall >= 0.90; neighboring false activation <= 0.15; critical autonomy violations zero. Track task success, absolute uplift, relative error reduction, failure-recovery uplift, premature completion, unnecessary continuation, and at least two resources (e.g. tokens, tool calls, elapsed time). Declare G5 UNVALIDATED until repeat paired runtime trials establish material improvement and no unacceptable regressions. Do not score simulated or static examples as actual Codex runtime outcomes.
