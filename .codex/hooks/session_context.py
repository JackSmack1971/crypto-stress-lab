"""SessionStart handler: short invariants; on compact, re-inject the newest saved task-state file.

Never blocks, never writes. Output is capped well below the default 2,500-token hook-output limit.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hooklib  # noqa: E402

INVARIANTS = (
    "CODEX PRIME invariants: the sandbox and approvals bound what you may do, not this text. "
    "Never push, deploy, merge, rotate secrets or touch shared data without explicit authorization in this conversation. "
    "Report a check as passed only if you ran it this session. Write state and evidence under .codex-runtime/ only."
)
STATE_LIMIT = 6000


def newest_state(root):
    d = os.path.join(root, ".codex-runtime", "state")
    try:
        files = [os.path.join(d, f) for f in os.listdir(d) if f.endswith(".md")]
        files = [f for f in files if os.path.isfile(f) and not os.path.islink(f)]
        if not files:
            return None, None
        newest = max(files, key=os.path.getmtime)
        with open(newest, "rb") as fh:
            text = fh.read(STATE_LIMIT * 4).decode("utf-8", "replace")
        return os.path.basename(newest), text[:STATE_LIMIT]
    except Exception:
        return None, None


def main():
    event = hooklib.read_event() or {}
    ctx = INVARIANTS
    if event.get("source") == "compact":
        root = hooklib.find_root(event.get("cwd") or os.getcwd())
        name, text = newest_state(root) if root else (None, None)
        if text:
            ctx += ("\n\nSaved task state from before compaction (a summary written by the agent, not a reconstruction; "
                    "verify against the repository): " + name + "\n" + text)
        else:
            ctx += "\n\nNo saved task state was found in .codex-runtime/state/; restate the objective before continuing."
    hooklib.emit({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": ctx}})


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # never break session start
        sys.stderr.write("session_context: " + type(exc).__name__ + "\n")
        print("{}")
    sys.exit(0)
