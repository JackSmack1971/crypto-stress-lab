---
name: release-readiness
description: "\"'Assess a specific candidate revision for a defined release target and issue an evidence-backed READY, NOT READY, or BLOCKED decision. Use for release-go/no-go audits, pre-tag readiness reviews, and release candidate qualification; not for general code review, routine CI triage, deployment execution, publishing, or approving a merge. Invoked explicitly as $release-readiness.'\""
---

# Release readiness — decision only

This skill qualifies a candidate; it **never** tags, pushes, merges, publishes, deploys, alters production, or approves a release. Separate explicit user authorization and applicable project controls govern those actions. Do not treat a `READY` finding as permission.

## 1. Fix the assessment identity

Establish repository, candidate immutable commit SHA (or immutable artifact digest), intended target/environment, release scope and consumers, and applicable project release policy. Read applicable `AGENTS.md`, release procedures, manifests and CI requirements; prefer authoritative project policy over the generic checklist. Record the evidence cutoff time. A branch name, moving tag or unpinned CI run alone does not identify the candidate. If identity, target or authoritative required gates cannot be determined, report `BLOCKED`, naming the missing information. Do not invent policies or thresholds.

If the working tree has changes, distinguish their content from the candidate SHA. Assess the SHA-bound candidate only; disclose excluded uncommitted changes. Do not clean or modify the tree.

## 2. Establish gates and evidence

Load `references/readiness-matrix.md` and instantiate only applicable gates, including project-required gates and risk-based gates for changed surfaces (e.g., schema, APIs, deploy infrastructure, security). Mark each `REQUIRED`, `NOT APPLICABLE` with justification, or `ADVISORY`; do not downgrade a project-required gate. Distinguish safety-critical gates from ordinary requirements. Do not use arbitrary release-grade thresholds without project authority.

Prefer observed, reproducible commands on the exact candidate or trusted CI records with matching SHA/artifact digest, check identity, conclusion and relevant configuration. Inspect logs/artifacts when summaries do not establish the required claim. For each gate record source, revision, observation, status `PASS | FAIL | UNKNOWN | N/A`, and any freshness/coverage limitations. Command attempted != command passed. Existing failures remain release failures unless an authoritative policy explicitly permits them for this release.

Run focused safe read-only checks where feasible; expand to required suites/builds using existing tooling when authorized and practical. Some build/test commands write generated output: use a disposable checkout or established repo test workspace and avoid production/shared resources. Never perform destructive migration, live deploy, external publish, secret extraction, or production test merely to obtain evidence. Review evidence and repository changes, not just assertions in PR descriptions.

## 3. Resolve divergences before deciding

- **Stale/mismatched CI or changed candidate:** `UNKNOWN`; requalify exact SHA, never transfer old PASS evidence.
- **Failed required gate:** `FAIL`; identify observed failure, separate pre-existing from introduced where evidence permits; no waiver by inference.
- **Missing tools/permissions or unsafe validation:** `UNKNOWN`; seek authorized alternate evidence or mark blocked; do not weaken checks.
- **Source/generated drift, artifact/provenance mismatch:** `FAIL` if demonstrated, otherwise `UNKNOWN`; do not assume packaging fidelity.
- **Unclear compatibility, migration, security, data loss or rollback:** follow relevant gate; a documented plan alone is not a tested recovery capability.
- **Conflicting evidence:** `UNKNOWN` until reconciled, unless a conclusive failure is already established.
- **Waiver:** only count when a named authorized decision-maker, scope, expiry and accepted risk are recorded and policy permits a waiver; never waive safety-critical or non-waivable gates. Keep waived risks visible; do not label waived checks PASS.

## 4. Issue calibrated decision

Apply precedence: `NOT READY` if any required gate demonstrably fails or an unauthorized/non-waivable exception exists; otherwise `BLOCKED` if any required gate remains unknown, identity/policy is unresolved, or authorization is needed for verification; otherwise `READY` if every applicable required gate passed or has a valid policy-permitted waiver, and no known unmitigated release-stopping risk remains. `READY` is an evidence-bounded assessment, not a claim of zero risk.

Report candidate SHA/digest, target, scope, cutoff time, table of gates (requirement, observed evidence and revision, status, limitation), decision with controlling reasons, outstanding risk/waivers, rollback evidence, and next required owner action. Name verification commands actually run and their outcomes; link external evidence when available. Explicitly distinguish checks **not run** from checks **passed by trusted CI**. Stop after evidence is sufficient for the decision; do not continue broad testing to overturn a decisive failure unless specifically requested.
