# Hook handlers

## Code Review Rules
### Hook contracts
- Flag output fields that are unsupported for the event: `permissionDecision: "ask"`, `updatedInput` without allow, or `continue`,
  `stopReason`, `suppressOutput` on `PreToolUse`; `allow`, `updatedInput`, `updatedPermissions` or `interrupt` from `PermissionRequest`.
  Safe path: the deny shape or empty output in `.codex/knowledge/hooks.md`.
- Flag a `Stop` or `SubagentStop` handler that can continue when `stop_hook_active` is true: it must never continue twice.
- Flag a handler that denies, exits 2 or blocks on its own malformed input or internal error without a tested contract, because the
  event may fail open anyway and the sandbox, not the hook, is the boundary.
- Flag handlers that store command lines, tool output or environment, write outside `.codex-runtime/`, or use network access,
  `eval`, `exec` or `shell=True`.
- Flag a changed handler or registration without a fixture test in `tools/control_plane/test_hook_policies.py`; any edit needs
  operator re-review in `/hooks`, so say so.
