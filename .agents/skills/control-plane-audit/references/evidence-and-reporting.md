# Evidence and reporting contract

## Evidence classes

- **E0 claim only:** document, comment, intent; no operational validation.
- **E1 inventory:** path/configuration exists and parsed (static structural evidence).
- **E2 invocation:** actual component consumes/executes config or validator; outcome captured.
- **E3 independent negative test:** altered/injected invalid condition is correctly rejected or denied; compare expected and observed.
- **E4 repeated comparative test:** paired or repeated trials with grounded rates and bounded conditions.

Do not raise a statement beyond the supporting class. Passing self-tests is E2 for the test program, not E3 for its CI enforcement. Record raw command, exit status, files, observed text excerpt/artifact hash where relevant, environment/version, and timestamp when available; redact secrets and personal data.

## Severity and status

P0: materially unsafe external/permission action or falsely asserted hard protection with immediate consequence. P1: mandatory gate/route ineffective or decisive evidence incorrect. P2: meaningful robustness, completeness or maintenance gap. P3: cosmetic, optional or low-consequence. For each, confidence CONFIRMED / LIKELY / HYPOTHESIS; uncertainty is not severity.

Use PASS only for the specified scope with sufficient evidence. FAIL requires contradiction or unmet necessary condition. INCONCLUSIVE means evidence insufficient/contradictory. NOT TESTED means planned execution was not performed. NOT APPLICABLE requires why. MISSING means required component not found. Never convert a missing test into PASS/FAIL by assumption.

## Scorecard

Audit coverage = applicable domains with evidence-backed verdict or explicit evidence gap / all applicable domains. Report numerator and denominator, not a fabricated success percentage. Distinguish static coverage, runtime coverage, enforcement-trace coverage and traceable finding percentage. Count both sampled and total candidate files if a bounded inspection was necessary.

If using a historical baseline, show prior/current evidence on matching requirements. Do not claim an actual routing precision, recall, task uplift, or performance score from hypothetical prompts or static inspection. For skill quality follow the project rubric: Design Readiness /50 — UNVALIDATED until paired runtime tests establish G5.

## Report template

- **Scope:** root, revision, environment, exclusions, observed control-plane layout.
- **Executive outcome:** PASS / FAIL / INCONCLUSIVE scoped to static/runtime separately.
- **Coverage:** per-domain status, enforcement class and evidence reference; untested counts.
- **Findings:** ID | priority | certainty | claim | actual evidence | consequence | minimal repair | acceptance check.
- **Evidence ledger:** command, working directory, exit status, source paths, tool versions; avoid large log dumps.
- **Baseline/regressions:** known baseline and only evidenced deltas.
- **Next decisions:** missing authorization, inaccessible tools, incompatible versions, unverified claims.
- **Stop:** no implementation or external changes performed without separate authorization.
