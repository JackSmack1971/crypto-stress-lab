#!/usr/bin/env python3
"""Read-only, bounded inventory. No subprocesses, file content execution, or symlink traversal."""
import argparse
import json
import os
from pathlib import Path

WATCH = {"AGENTS.md", "AGENTS.override.md", "SKILL.md", "openai.yaml", "config.toml", "CLAUDE.md"}
SKIP = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__"}


def inventory(root: Path, limit: int = 10000):
    if not root.is_dir():
        raise ValueError("root must be an existing directory")
    records, skipped, scanned = [], [], 0
    for base, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SKIP and not (Path(base) / d).is_symlink())
        for name in sorted(files):
            scanned += 1
            if scanned > limit:
                return {"root": str(root), "records": records, "skipped": skipped,
                        "scanned": scanned - 1, "truncated": True}
            path = Path(base) / name
            if path.is_symlink():
                skipped.append(str(path.relative_to(root)))
                continue
            relative = path.relative_to(root).as_posix()
            if name in WATCH or ("control_plane" in path.parts and name.endswith(".py")):
                try:
                    size = path.stat().st_size
                except OSError:
                    skipped.append(relative)
                    continue
                records.append({"path": relative, "bytes": size, "kind": name})
    return {"root": str(root), "records": records, "skipped": skipped,
            "scanned": scanned, "truncated": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, help="Optional JSON output file outside the audited repository")
    parser.add_argument("--limit", type=int, default=10000)
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be positive")
    root = args.root.resolve()
    report = inventory(root, args.limit)
    payload = json.dumps(report, indent=2) + "\n"
    if args.output:
        output = args.output.resolve()
        if output == root or root in output.parents:
            parser.error("output must be outside the audited repository")
        output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
