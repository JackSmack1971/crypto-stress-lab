# Failure decisions (load on divergence)

| Observation | Required response | Completion boundary |
|---|---|---|
| Expected target file or local contract missing | Search relevant authoritative paths; identify actual source of truth; avoid guessed paths | Stop if scope or intended behavior cannot be established |
| User changes overlap proposed edit | Inspect index and working-tree differences; preserve existing lines; seek a compatible minimal edit | Stop before overwriting or staging others' work |
| Tests already failing | Obtain a baseline if possible; compare same check and environment after edit | Claim pre-existing only with comparable observed evidence; otherwise attribution unknown |
| Test tool or runtime missing | Use existing repo-supported alternate evidence where possible, without changing dependencies just to make the check run | Report exact unavailable command, cause, and unverified behavior |
| Generated artifact differs from source | Identify generator, authoritative inputs, and regeneration procedure | Do not hand-reconcile or claim synchronized without regeneration and diff inspection |
| Specification conflicts with architecture or compatibility | Examine governing instructions and consumer contracts, propose smallest viable options | Stop when selecting an option would decide a consequential product or architecture policy |
| Check succeeds but does not test acceptance | Add or run a narrower assertion, manual reproduction, or other independent observation | Report verification gap if suitable evidence cannot be obtained |
| Unexpected new failures | Isolate changed surface and run targeted diagnostics; avoid modifying unrelated tests | Treat unresolved potential regressions as blockers to a verified-success claim |
| External, destructive, secret-sensitive, or high-blast-radius action becomes necessary | Prefer reversible read-only work, ask for explicit scoped authorization, validate target | Do not perform action based on skill activation alone |
| Subagent or companion skill unavailable | Use direct implementation/verification with explicit ownership; do not pretend delegation or review occurred | Mark independent review not performed if applicable |
| Validation stalls or repeats without new evidence | Stop escalation and explain uncertainty with reproducible commands and observations | Do not continue indefinitely or declare unsupported success |

For high-risk changes (security boundaries, data loss, cross-cutting APIs, financial movement, authentication, production operations), increase independent review and verification in proportion to blast radius. A risk label from another workflow is informative only when its definition is actually available; do not assume an `L2/L3` scale exists.
