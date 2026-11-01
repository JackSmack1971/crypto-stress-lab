---
name: control-plane-audit
description: "Invoke as $control-plane-audit to Audit the configuration and operational evidence of a Codex project control plane: instruction precedence, custom agents, skill routing, validators, tool permissions, delegation and enforcement claims. Use when explicitly invoked to assess control-plane correctness or regressions; not for implementing features, automatically fixing defects, or general code review."
---

# Control-plane audit

This skill exists to **produce a reproducible, evidence-calibrated audit of a Codex control plane** when explicitly invoked. The skill grants no new authority. Keep the audit read-only; do not edit the target repository, execute model-backed Codex sessions, generate commits, or open network connections without separate authorization. A user's request to audit is not authorization for paid/model-backed runtime experiments.

## 1. Fix scope and baseline

1. Identify the target repository/root and current Git branch, status, tracked changes, and applicable `AGENTS.md`/`AGENTS.override.md`. Record any inaccessible or untrusted evidence. Do not assume CODEX PRIME layout; infer actual inventory from the repository.
2. List audit claims made by the project's documentation: discovery, instruction hierarchy, agent routing/spawning, skill activation, tool/sandbox boundaries, validators, reviews, telemetry, CI, and completion gates. Audit only claims that exist or are implied by deployed configuration; label absent features **not implemented**, not failed runtime checks.
3. Establish comparison version/commit only when supplied or independently available. Otherwise use **no regression baseline**; avoid calling a defect a regression without comparative evidence.
4. Perform read-only inventory with `python scripts/inventory.py --root <repo> --output <temporary-json-path>` when Python is available; this script does not verify semantics. Review the output and validate manually rather than treating it as authority. If unavailable, inventory equivalent paths with repository tools. Read [audit matrix](references/audit-matrix.md) for coverage and [evidence rules](references/evidence-and-reporting.md) for verdicts.

## 2. Static verification

- Inspect actual configuration, `AGENTS` instruction scope and conflicts, skill frontmatter, `agents/openai.yaml`, custom agent definitions, script references, validators, gates and triggers. Do not infer priority/enforcement solely from filenames or comments. Trace each claim to its consuming mechanism, invocation site, observable output and failure behavior.
- Follow existing repository validator commands and the conditional examples in [audit procedure](references/audit-procedure.md). Inspect each command's implementation and expected effects **before executing**; run only confirmed read-only, locally safe checks. A `--self-test` flag is not evidence of safety. Never run arbitrary discovered scripts automatically.
- Assign each control an enforcement class: **Codex-enforced**, **repository-enforced**, **advisory**, **unverified**, or **absent**. For an enforcement claim, require configuration plus the actual loader/consumer or verifiable execution evidence; otherwise use **unverified**. A validator that exists but is not wired into an enforced gate is not an enforcement boundary.
- Check competing skill descriptions and agent selectors for indistinguishable routing, aliases and duplicate identities; inventory broken references, orphaned definitions, stale docs, hard-coded paths, unresolved dependencies and hidden side effects.

## 3. Runtime and adversarial evidence

Static pass is not runtime pass. For each material claim identify the smallest observable probe, expected behavior, result artifact and disconfirming outcome using [runtime probes](references/runtime-probes.md). In particular, distinguish `codex` availability, configuration listing, actual skill activation, delegation, permission denial, CI blocking, and successful enforcement.

Do **not** run `codex exec`, token-consuming calls, subagent spawning, or live external tests without user approval for exact scope/cost and isolation. When approved, use isolated disposable targets, record tool versions and effective sandbox settings, and keep destructive/high-impact probes simulated. A probe that is unavailable, unsafe or unauthorized is **NOT TESTED**, never PASS. Do not silently weaken a probe to make it pass.

## 4. Reconcile and terminate

For each finding record: unique ID, requirement/claim, source and path, command/probe, observed evidence, expected behavior, enforcement class, static/runtime classification, severity, certainty, impact, proposed minimal repair, and verification needed. Distinguish pre-existing issues from introduced regressions only with a comparison baseline. Prioritize **P0** unsafe authority or false security controls; **P1** wrong routing/enforcement, broken mandatory gates or materially misleading completion; **P2** coverage/robustness gaps; **P3** polish. Never label speculative exposure as proven exploit.

Audit complete means all **applicable** domains from the matrix were assessed or explicitly marked unverified/not applicable with reasons; every claim has a traceable evidence class; every major uncertainty has a test/decision to resolve it; and no runtime assertion exceeds observation. Stop after delivering findings—do not fix the target unless separately requested. Present an executive verdict, coverage table, prioritized findings, static-vs-runtime results, evidence gaps, recommended repairs and exact checks performed. If evidence is insufficient, say **INCONCLUSIVE**, not PASS.
