# Regression evidence matrix

Maintain one row per distinct contract/case; reuse existing tests when adequate.

| Contract / risk | Case (positive, rejection, boundary, transition) | Expected observation | Test identity | Baseline evidence | Actual command/result | Disposition |
| --- | --- | --- | --- | --- | --- | --- |

Rules:
- Enumerate relevant acceptance criteria and unchanged contracts endangered by the diff. Every required contract must map to test evidence or an explicit gap.
- Mark tests `not_run` until their actual results are observed. Do not infer success from unrelated green commands.
- A negative case must demonstrate a meaningful forbidden input or state, not a duplicate happy path. Mark `not_applicable` and explain when none exists.
- Record test identity (stable test name/file) and executed command; annotate gaps where a required case is absent or inaccessible.
- Distinguish unit, integration, system and cross-version claims; do not treat one level as evidence of another without grounds.
