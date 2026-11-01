"""PermissionRequest handler: deny-only. Never returns allow, so the normal approval flow decides everything else."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hooklib  # noqa: E402


def decide(event):
    tool = event.get("tool_name")
    ti = event.get("tool_input")
    cmd = ti.get("command") if isinstance(ti, dict) else None
    if tool == "apply_patch":
        return hooklib.evaluate_patch(cmd)
    if tool == "Bash":
        r = hooklib.evaluate_bash(cmd)
        if r:
            return r
        if isinstance(cmd, str) and hooklib.control_text(cmd):
            return "an escalation that targets hooks, rules or project config cannot be approved from inside a session"
    return None


def main():
    event = hooklib.read_event()
    if event is None:
        sys.stderr.write("permission_policy: malformed input; no decision (normal approval flow)\n")
        return
    reason = decide(event)
    if reason:
        hooklib.emit(hooklib.deny_permission("Blocked by repository policy: " + reason))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        sys.stderr.write("permission_policy: internal error " + type(exc).__name__ + "; no decision\n")
    sys.exit(0)
