#!/usr/bin/env python3
"""Local, monotonic review-pass accounting. No Git operations or external effects."""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile

CAP = 3


def read(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema") != 1 or not isinstance(data.get("passes"), list):
        raise ValueError("invalid ledger schema")
    if len(data["passes"]) > CAP or any(not isinstance(p, dict) for p in data["passes"]):
        raise ValueError("invalid pass history")
    return data


def atomic_create(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())


def atomic_replace(path, data):
    fd, temporary = tempfile.mkstemp(prefix=".review-ledger-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("init", "pass", "status"))
    p.add_argument("--file", type=Path, required=True, help="persistent ledger path outside disposable worktrees")
    p.add_argument("--task", help="stable task identity")
    p.add_argument("--candidate", help="candidate identity, e.g. base/head + dirty-diff digest")
    p.add_argument("--reviewer", help="independent reviewer identifier (pass only)")
    args = p.parse_args()
    path = args.file
    if args.command == "init":
        if not args.task or not args.candidate:
            p.error("init requires --task and --candidate")
        atomic_create(path, {"schema": 1, "task": args.task, "candidate": args.candidate, "passes": [], "cap": CAP})
    else:
        data = read(path)
        if args.task and data["task"] != args.task:
            raise ValueError("task identity mismatch")
        if args.command == "pass":
            if not args.candidate or not args.reviewer:
                p.error("pass requires --candidate and --reviewer")
            if len(data["passes"]) >= CAP:
                raise ValueError("review budget exhausted")
            data["candidate"] = args.candidate
            data["passes"].append({"number": len(data["passes"]) + 1, "candidate": args.candidate, "reviewer": args.reviewer})
            atomic_replace(path, data)
        print(json.dumps({"task": data["task"], "candidate": data["candidate"], "used": len(data["passes"]), "remaining": CAP - len(data["passes"]), "passes": data["passes"]}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ledger error: {exc}", file=sys.stderr)
        sys.exit(2)
