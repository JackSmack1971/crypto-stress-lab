"""PostToolUse (Bash, async) handler: append a sanitized outcome record to .codex-runtime/results/<session_id>.jsonl.

Records only ids, a coarse command class and the exit code. It never stores command lines, output or environment.
Operational assistance, not proof that a test's semantics are correct.
"""
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hooklib  # noqa: E402


def exit_code(resp):
    if isinstance(resp, dict):
        for key in ("exit_code", "exitCode"):
            v = resp.get(key)
            if isinstance(v, int) and not isinstance(v, bool):
                return v
        meta = resp.get("metadata")
        if isinstance(meta, dict):
            return exit_code(meta)
    return None


def main():
    event = hooklib.read_event()
    if event is None or event.get("tool_name") != "Bash":
        return
    root = hooklib.find_root(event.get("cwd") or os.getcwd())
    if not root:
        return
    ti = event.get("tool_input")
    cmd = ti.get("command") if isinstance(ti, dict) else None
    record = {
        "schema_version": 1,
        "session_id": str(event.get("session_id") or ""),
        "turn_id": str(event.get("turn_id") or ""),
        "tool_use_id": str(event.get("tool_use_id") or ""),
        "tool_name": "Bash",
        "command_class": hooklib.command_class(cmd),
        "exit_code": exit_code(event.get("tool_response")),
        "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    out_dir = os.path.join(root, ".codex-runtime", "results")
    if os.path.islink(os.path.join(root, ".codex-runtime")) or os.path.islink(out_dir):
        return
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, hooklib.safe_name(record["session_id"]) + ".jsonl")
    if os.path.islink(path) or (os.path.exists(path) and os.path.getsize(path) > 2_000_000):
        return
    with open(path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(record, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        sys.stderr.write("execution_evidence: " + type(exc).__name__ + "; no record written\n")
    sys.exit(0)
