# Portable handoff record

Use the repository's existing ledger if it is authoritative. This minimal JSON format is for a saved handoff when no existing compatible ledger is available. It is **evidence bookkeeping**, not security enforcement. The optional validator checks internal consistency only and cannot verify command execution, actual Git state, reviewer independence, or authorization.

Required fields and types:

```json
{
  "task_id": "task-001",
  "state": "PARTIAL",
  "risk": "L2",
  "baseline": "git-sha-or-not_git",
  "revision": "git-sha-plus-diff-fingerprint-or-unknown",
  "scope": ["src/example.py"],
  "owners": [{"role": "implementer", "paths": ["src/example.py"]}],
  "acceptance": ["Relevant tests pass"],
  "checks": [{"id": "focused", "command": "pytest tests/test_example.py", "revision": "git-sha-plus-diff-fingerprint-or-unknown", "status": "NOT_RUN", "evidence": ""}],
  "findings": [],
  "approvals": [],
  "review": {"required": true, "status": "NOT_RUN", "revision": "git-sha-plus-diff-fingerprint-or-unknown", "evidence": ""},
  "effects": [],
  "next": "Run focused test and independent review"
}
```

- `task_id`, `baseline`, `revision` identify a **single task and snapshot**. Use `unknown` where evidence is absent, not a made-up SHA. SHA plus task-specific diff fingerprint is preferable for dirty checkouts.
- `scope`, `owners`, `acceptance`, `checks`, `findings`, `approvals`, `effects` are arrays; `next` gives the required action or terminal reason.
- Check statuses: `PASS`, `FAIL`, `NOT_RUN`, `BLOCKED`, `INCONCLUSIVE`; a PASS requires nonempty evidence, a concrete command and matching revision.
- Review statuses: `PASS`, `FAIL`, `NOT_RUN`, `BLOCKED`, `INCONCLUSIVE`, `INDEPENDENCE_UNAVAILABLE`; PASS requires evidence and matching revision.
- Findings: objects with `severity` (`CRITICAL`, `MAJOR`, `MINOR`), `status` (`OPEN`, `RESOLVED`, `ACCEPTED`), and `evidence`. `ACCEPTED` material findings require explicit authorized disposition outside this checker; treat them as blockers for COMPLETE unless project policy resolves them.
- Approval entries: objects with `action`, `authority`, `evidence`; record only when actually obtained. This schema cannot validate real permissions.
- `effects` describes actual edits, commits, remote writes and unknown outcomes. Never store secrets.
- `COMPLETE` requires acceptance criteria, at least one PASS check on the same known revision, no failed/inconclusive/blocked required checks, applicable PASS review, no open material finding and `next` empty. This is a *minimum generic completeness rule*, not a substitute for the repository's domain-specific checks.
