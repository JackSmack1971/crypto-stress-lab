# Failure and evidence handling

| Condition | Required response |
| --- | --- |
| Cannot identify repository root or read code | Report blocking access gap; avoid invented paths |
| Git unavailable / not a Git worktree | Use available read-only file evidence; mark working-tree baseline unverified |
| Instructions conflict or apply ambiguously | Record the conflict and stop before any consequential action; discovery may continue only where clearly permitted |
| Search returns multiple plausible owners | Compare import/call/registration evidence; preserve alternatives until a path is corroborated |
| No match in targeted search | Try one independent term/entry mechanism; report search scope and absence as inconclusive |
| Documentation disagrees with source/tests | Present both observations; treat executable behavior as provisional authority until reconciled |
| Generated file lacks traceable source | Mark edit authority unresolved; do not propose editing the generated output as canonical |
| Test or verification command missing | Report test files and missing invocation; do not invent a command |
| Baseline test failures visible | Distinguish pre-existing failures from changed behavior; read-only recon does not fix either |
| Tool unavailable or output truncated | Use a bounded alternate read; state what was not inspected |
| Network, secrets, writes, costly jobs, external effects needed for more evidence | Stop at the permission boundary and specify what authorization and observation are needed |
| Boundary stays ambiguous after bounded traversal | Return provisional map with ranked candidate paths and the smallest disambiguating inspection |
