"""SubagentStart / SubagentStop handler (dispatches on hook_event_name).

Start: inject the standing delegation rules. Stop: send a subagent back once when its last message has no status.
Both events want JSON on stdout when exiting 0.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hooklib  # noqa: E402

RULES = ("Delegation rules: stay inside the assigned scope; cite files and symbols; label hypotheses as hypotheses; do not "
         "commit, push, deploy or change secrets; end with exactly one status line: COMPLETE, PARTIAL, BLOCKED, CONFLICTED "
         "or UNVERIFIED, with the evidence for it.")
_ALT = "|".join(hooklib.STATUSES)
# A status line: a line that starts with the word (optionally after "Status:" or markdown marks), or "Status: WORD" anywhere.
STATUS = re.compile(r"(?m)^[\s*#>_-]*(?:(?i:status)\W{0,3})?(?:" + _ALT + r")\b|\b(?i:status)\W{1,3}(?:" + _ALT + r")\b")


def main():
    event = hooklib.read_event()
    if event is None:
        hooklib.emit({})
        return
    name = event.get("hook_event_name")
    if name == "SubagentStart":
        hooklib.emit({"hookSpecificOutput": {"hookEventName": "SubagentStart", "additionalContext": RULES}})
    elif name == "SubagentStop":
        msg = event.get("last_assistant_message")
        if event.get("stop_hook_active") is True or not isinstance(msg, str) or STATUS.search(msg):
            hooklib.emit({})
        else:
            hooklib.emit({"decision": "block",
                          "reason": "End with COMPLETE, PARTIAL, BLOCKED, CONFLICTED, or UNVERIFIED and cite evidence."})
    else:
        hooklib.emit({})


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        sys.stderr.write("subagent_contract: " + type(exc).__name__ + "\n")
        print("{}")
    sys.exit(0)
