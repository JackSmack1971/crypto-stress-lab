# Root-cause evidence report

Use concise prose or a compact table. Omit categories that do not apply, but never omit unknowns that affect confidence.

1. **Scope and symptom** — user-requested diagnosis/repair/verification; observed versus expected result; relevant input and environment, redacting secrets.
2. **Reproduction and baseline** — exact commands/inputs, attempts, exit statuses, discriminating excerpts, baseline comparison and provenance. Explicitly say `not reproduced` or `baseline unknown` when applicable.
3. **Causal analysis** — first divergence, mechanism, competing explanations, falsifying observations. Classify root cause as **confirmed**, **probable**, or **unresolved**, and state why.
4. **Action** — minimal correction or proposed change and affected files; record whether work was diagnosis-only.
5. **Verification** — focused test commands and outcomes; red-before/green-after evidence if obtained, independent checks, broader validation only if warranted. Distinguish pre-existing from introduced failures.
6. **Remaining uncertainty** — unverified behavior, environmental differences, tools/permissions unavailable, conflicting evidence, and the next discriminating test or owner decision.

Never equate a command being attempted with success, and never present a plausible explanation as confirmed without causal evidence.
