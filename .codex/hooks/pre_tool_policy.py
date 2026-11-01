"""PreToolUse handler: explicit denial for a narrow list of unsafe operations.

Fails open on malformed input or internal error (the hooks page documents that PreToolUse callback errors, timeouts and
malformed responses do not block the tool; the same for a crashing command hook is an inference). The sandbox and approvals
remain the real boundary. Commands too long or too nested to evaluate are denied instead.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hooklib  # noqa: E402


def decide(event):
    tool = event.get("tool_name")
    ti = event.get("tool_input")
    cmd = ti.get("command") if isinstance(ti, dict) else None
    if tool == "Bash":
        return hooklib.evaluate_bash(cmd)
    if tool == "apply_patch":
        return hooklib.evaluate_patch(cmd)
    return None


def main():
    event = hooklib.read_event()
    if event is None:
        sys.stderr.write("pre_tool_policy: malformed input; not evaluated (fails open)\n")
        return
    reason = decide(event)
    if reason:
        hooklib.emit(hooklib.deny_pretool("Blocked by project policy: " + reason))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        sys.stderr.write("pre_tool_policy: internal error " + type(exc).__name__ + "; not evaluated (fails open)\n")
    sys.exit(0)
