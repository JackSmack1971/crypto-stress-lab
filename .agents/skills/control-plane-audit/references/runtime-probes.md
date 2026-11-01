# Optional runtime-probe protocol (authorization required)

1. Record explicit user authorization, maximum scope/cost, runtime version, workspace safety and target fixture. If absent, produce a probe plan only.
2. Run in an isolated disposable workspace using confirmed supported commands. Inspect `codex --help` and local configuration before selecting flags. Treat output from `/status`, `/skills` or agent listings as evidence only of what it actually lists.
3. Skill discovery: one explicitly invoked known skill, one missing skill; record real transcript and changed files. Implicit routing: at least 20 positives, 20 negatives, 10 neighboring prompts, three trials each, including competing skills where applicable. Repeat under identical selection conditions; log false positives/negatives.
4. Agent delegation: invoke a minimal authorized delegation task and observe actual spawn, agent selection, boundaries, return and verified output; also inject a failed handoff or missing agent. Text claiming the spawn happened is not actual observation.
5. Enforcement: in a disposable fixture make one reversible violation that the claimed validator should block; observe validator exit and the actual blocking gate (CI/pre-commit/wrapper). Do not test destructive permissions against real repositories, secrets or production systems.
6. Run at least ten representative scenarios and five relevant failure scenarios with/without the skill from matched starting states, repeated when practical. Fix outcome rubric before sampling. Capture task success, recovery, policy violations, premature completion and at least two cost dimensions.
7. Redact transcripts; archive machine-readable outcomes, version and prompts. A safety or permission denial that prevents a probe is a legitimate NOT TESTED reason, not an invitation to relax limits.

Do not infer a result from the existence of this plan; all tests here are optional until explicitly authorized.
