"""Stop handler: continue once when the final message claims passing tests but no test-class command ran this turn.

Continuation only; it does not judge correctness. The evidence log is written by an async PostToolUse hook, so a
very fast Stop could race it: the worst case is one extra continuation (stop_hook_active ends the loop).
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hooklib  # noqa: E402

CLAIM = re.compile(
    r"\b(tests?|checks?|self-tests?|test suite|validators?|validation)\b[^.\n]{0,40}\b(pass(ed|es|ing)?|green|succeed(ed)?|ok)\b"
    r"|\b(pass(ed|es)?|ran)\b[^.\n]{0,30}\b(tests?|checks?|self-tests?|test suite)\b"
    r"|\b\d+ (tests? )?passed\b", re.I)
# A message that reports a failure, a skipped run, or a conditional is not a false "tests passed" claim.
DENIAL = re.compile(
    r"\b(not run|did not run|didn't run|could not run|couldn't run|cannot run|not verified|no tests? (were )?run|"
    r"unable to run|failed to run|would pass|should pass|if (the )?tests? pass|not all|did not pass|didn't pass|"
    r"not passing|aren't passing|isn't passing|can't pass|cannot pass|fail(s|ed|ing)|[1-9]\d* fail(ures?)?)\b", re.I)


def test_ran(root, session_id, turn_id):
    path = os.path.join(root, ".codex-runtime", "results", hooklib.safe_name(session_id) + ".jsonl")
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if (isinstance(rec, dict) and rec.get("turn_id") == turn_id and rec.get("command_class") == "test"
                        and rec.get("exit_code") in (0, None)):  # a run known to have failed does not back a pass claim
                    return True
    except OSError:
        return False
    return False


def main():
    event = hooklib.read_event()
    if event is None or event.get("stop_hook_active") is True:
        hooklib.emit({})
        return
    msg = event.get("last_assistant_message")
    if not isinstance(msg, str) or not CLAIM.search(msg) or DENIAL.search(msg):
        hooklib.emit({})
        return
    root = hooklib.find_root(event.get("cwd") or os.getcwd())
    if root and test_ran(root, event.get("session_id"), str(event.get("turn_id") or "")):
        hooklib.emit({})
        return
    hooklib.emit({"decision": "block", "reason": "You reported tests as passing but no test command ran this turn. "
                  "Run them, or state that verification was not performed."})


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        sys.stderr.write("completion_gate: " + type(exc).__name__ + "\n")
        print("{}")
    sys.exit(0)
