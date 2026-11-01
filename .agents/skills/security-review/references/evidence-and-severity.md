# Evidence, severity, and failure decisions

## Evidence statuses
- **Confirmed source-level:** A specific reachable path, missing/defective enforcement and relevant sink are demonstrated in inspected code; execution not established.
- **Runtime demonstrated:** A permitted test with non-production fixtures reproduced the failure; note exact preconditions and environment.
- **Conditional/unverified:** Relevant code suggests a risk but reachability, configuration, attacker control or countermeasure is not established. State what evidence would decide.
- **Not substantiated:** The investigation did not support the proposed issue; do not report as a vulnerability. Document as coverage note only if consequential.

Evidence must identify a file and symbol (and lines if available), a trust boundary crossed, and a reproducible reasoning chain. Do not call a tool result a successful test unless its outcome was observed. Do not infer absence of a defect from lack of matches.

## Severity rubric (not a CVSS calculation)
- **Critical:** Evidenced reachable path enabling severe compromise (e.g. broad unauthorized sensitive data access or control of privileged execution) with realistically low barriers; requires immediate escalation through authorized channels.
- **High:** Evidenced serious confidentiality, integrity, or availability impact, with plausible attacker-controlled entry, though exploitation may require additional conditions.
- **Medium:** Material security impact subject to meaningful prerequisites, limited scope or existing containment.
- **Low:** Limited direct impact or substantial barriers; may matter in conjunction with other issues.
- **Informational:** Hardening or visibility gap without an established exploitable security defect. Do not represent as a confirmed vulnerability.

Record **confidence separately** (high/medium/low): how direct and complete is evidence? A high-severity but low-confidence issue is escalated as conditional, never quietly upgraded to a confirmed exploit. Avoid numeric scores unless the user's program defines a supported scoring model.

## Branches and completion decisions
| Condition | Required response |
|---|---|
| No explicit scope | Bound to named change/component and reachable security paths; disclose limit |
| Relevant code/config missing | Identify missing artifact; conditional conclusion or inconclusive |
| Scanner unavailable | Continue manual source tracing; note omitted automated coverage |
| Test harness fails before review | Establish baseline where safe; avoid attributing pre-existing failure |
| Local dynamic test could mutate state or execute untrusted scripts | Do not run; use source evidence or authorized isolated runner |
| Production/live target, credentials or invasive proof needed | Stop; request explicit authorization, safe plan and boundaries |
| Source and generated/deployed behavior disagree | Identify governing artifact, verify provenance, mark mismatch unresolved |
| Conflicting evidence or absent attacker reachability | Downgrade confidence/mark conditional; specify decisive next check |
| Critical exposure discovered | Report promptly using allowed channel; do not probe further or reveal secrets |
| Requested fixes alongside review | Keep audit findings distinct; seek explicit authorization before remediation |
| No supported findings | Report scoped no-findings and verification coverage, not blanket clearance |

## Reporting record
Use concise prose or a table, but preserve these fields: ID; severity; confidence; status; affected code; source → check → sink; prerequisites; impact; evidence; mitigation; verification needed; introduced/pre-existing/unknown. For each check record the command (if safe to show), scope, result and whether it was executed. Finish with out-of-scope paths, unresolved evidence and residual risk.
