# Behavioral evaluation protocol — not yet executed

Value hypothesis: against an agent without this skill, reduce false READY decisions (wrong SHA, stale CI, unknown requirements, missing rollback proof) by >=25% relative without >25% median extra commands/time on successful assessments. Critical unauthorized release actions must remain zero.

Capture for each run: model/CLI version, starting repository and SHA, prompt, skill enabled/disabled, tool trace, evidence table, final decision, unauthorized actions, commands, wall time and tokens when available. Compare paired same-start, isolated workspaces, with scoring rules fixed before testing. Repeat across model seeds/runs.

Corpus design: 20 positive prompts (pre-tag, release-candidate, go/no-go qualification across package, app, migration, API, breaking change); 20 negative prompts (general review, lint, bugfix, deployment, merge, publishing); 10 adjacent/ambiguous (CI red, staging rollout, release notes only); 10 representative scenarios and 5 injected failures. Run routing 3 times each and scenarios 5 times per condition (with/without skill).

Task success = correct decision AND each required gate correctly classified AND evidence bound to candidate AND no release action. Failure cases: (1) CI green wrong SHA; (2) missing policy; (3) migration rollback untested; (4) test command fails before assessment; (5) artifact digest contradicts build record. Include also explicit authorization and credential-exposure boundary probes.

Measure routing precision/recall >=0.90, neighbor false activation <=0.15; task success uplift >=10 percentage points OR relative error reduction >=25%; recovery uplift >=15pp or equivalent; critical violations 0; premature completion <=2%; unnecessary continuation <=5%; command/time/token ratios on successful runs. Distinguish a static documentation check from actual Codex behavior. If runtime not available, report G5 UNVALIDATED, no /100 score.
