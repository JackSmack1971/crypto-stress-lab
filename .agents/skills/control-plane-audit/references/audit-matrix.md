# Audit matrix (apply only to deployed or claimed subsystems)

For each domain record: present/claimed? applicable? files inspected, consumer/enforcement point, evidence, verdict PASS/FAIL/INCONCLUSIVE/NOT TESTED/NOT APPLICABLE, repair or next test. `PASS` requires observable evidence for the specific claim; static-only evidence may pass a *static* assertion, not a runtime assertion.

| Domain | Static checks | Required independent observation for runtime claims |
|---|---|---|
| Instruction chain | Root/ancestor/nested `AGENTS.md`, overrides, conflicting instructions, actual effective scope | Controlled task demonstrating instruction selection or sanctioned trace |
| Skill metadata/discovery | Exact SKILL.md frontmatter, name, description, paths, optional sidecar, duplicate names | Actual discovery and explicit activation |
| Implicit routing | Trigger/exclusion language, collision matrix across neighboring skills | Positive/negative/neighbor tests repeated; precision, recall and false activation |
| Custom agents | Actual supported configuration/schema, names, selectors, roles, permission scope | Successful spawn with intended assignment, output and isolation |
| Delegation | Packet inputs/outputs, responsible caller, handoff, return/timeout/failure | Observed handoff, verified result and safe failed delegation |
| Tool and sandbox limits | Config, tool permissions, filesystem/network boundary, role of guidance | Benign denied action with observed policy effect in isolated workspace |
| Validators | Source, preconditions, exit codes, fixtures, exact invocation and wiring | Invalid fixture blocked by enforced gate, valid fixture accepted |
| Review and approval | Threat/risk classes, approver, escalation, review ledger, CI invocation | Independent review evidence, proper non-bypass on reject |
| Observability/evidence | Identifiers, artifact paths, retention, reproducibility, missing results | End-to-end link between action, artifact, decision and review |
| Drift/updates | Doc-to-runtime consistency, version-sensitive switches, stale assumptions | Repeat probe on declared runtime version after change |
| Failure recovery | Missing files/tooling, conflicting config, pre-existing validator failures, partial outputs | Safe stop/alternative evidence under injected failure |
| External operations | Remote calls, publishing, credentials, production environment | Explicit authorization, isolation and independently verified effect |

## Decision rules

- Structural presence is not functional use. A file/flag/schema is only configuration evidence until its consumer is established.
- Explicit-only activation in `agents/openai.yaml` is a routing intent; verify the installed runtime honors it before asserting a policy boundary.
- Inspect actual source and permissions: `.codex` and `.agents` paths are not inherently protected against writes.
- Absence of a claimed mandatory validator is a failure; absence of an unclaimed optional feature is not.
- Record versions and avoid universal assertions about Codex internals on the strength of one CLI version.
