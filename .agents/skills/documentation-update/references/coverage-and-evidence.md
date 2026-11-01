# Coverage and evidence branches

Load for nontrivial diffs, ambiguous authority, generated documentation, or several documentation consumers.

## Change-to-surface prompts

| Changed contract | Check likely documentation surfaces |
|---|---|
| Public function, route, response or schema | API references, SDK snippets, request/response examples, error documentation, compatibility notes |
| CLI argument, command or output | `--help` / CLI references, quickstarts, shell completions, copyable commands, usage examples |
| Config key, environment variable, default | environment templates, deployment/runbooks, configuration tables, upgrade guidance |
| Behavior, edge case or failure mode | README promises, tutorials, troubleshooting, docstrings, assertions quoted in docs |
| Renamed or removed interface | backlinks, old terminology, replacement instructions, migration/upgrade notes |
| Generated documentation | generator source, templates, generation command, checked-in outputs as applicable |

Search lexical variants and behavior descriptions, not only exact identifiers. Check both added and removed lines. Coverage is bounded by repository visibility and discovery strategy; absence from search is not a guarantee.

## Evidence classes

- **Executed:** safe reproducible command/test ran; record command, outcome, environment constraint and exact claim established.
- **Source-checked:** link to implementation/configuration or authoritative schema with enough location detail to reproduce; do not claim the example ran.
- **Unverified:** execution unavailable or source insufficient; explicitly qualify the affected statement and report the missing evidence.
- **Conflicted:** sources disagree materially; avoid asserting one as fact until the responsible authority resolves the discrepancy.

A test source expresses expectations; passing test execution adds observed evidence. A passing link checker confirms reachability, not the linked content's correctness. Never treat a script's candidate list as an exhaustive semantic proof.

## Failure and autonomy matrix

| Divergence | Response |
|---|---|
| Unknown diff baseline or detached archive | use user-specified implementation scope; label discovery incomplete |
| No relevant docs discovered | report search terms and inspected locations; avoid claiming complete absence |
| Existing edits overlap proposed documentation change | reconcile and preserve; stop and request decision if intent cannot be established |
| Source, tests and generated output disagree | record conflict, withhold disputed claim; do not change implementation under this skill |
| Generator or validation tool unavailable | inspect authoritative source, perform safe static checks, mark regeneration/validation blocked |
| Existing checks fail | isolate affected vs. baseline failures; report unresolved failures without weakening tests |
| Example requires network, credentials, production or destructive state | static-check or isolated approved test; do not run unauthorised operations |
| Documentation publication or deployment required | separate local edits from release; obtain explicit authorization before external side effects |

## Compact coverage ledger example

| Contract | Surface | Disposition | Evidence |
|---|---|---|---|
| `--format` default changed | CLI guide | update | parser default at `src/cli.py`, source-checked |
| JSON API response | README | checked-unchanged | README has no response example |
| shell snippet | quickstart | blocked | service credentials unavailable; static check only |

Do not fabricate paths or commands from this example.
