#!/usr/bin/env python3
"""Read-only, best-effort candidate inventory for documentation synchronization.

Never claims semantic completeness. Uses git-tracked files and a caller-provided
baseline; no network, writes, or shell interpretation.
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

DOC_EXT = {'.md', '.mdx', '.rst', '.adoc', '.txt'}
DOC_NAMES = {'readme', 'changelog', 'contributing', 'migration', 'upgrade'}


def git(repo, *args):
    result = subprocess.run(['git', '-C', str(repo), *args], capture_output=True, check=True)
    return result.stdout


def tracked(repo):
    return [s.decode('utf-8', 'surrogateescape') for s in git(repo, 'ls-files', '-z').split(b'\0') if s]


def inventory(repo, base):
    # -z protects whitespace and unusual filenames. Triple-dot compares against merge base.
    raw = git(repo, 'diff', '--name-only', '-z', f'{base}...HEAD')
    changed = {s.decode('utf-8', 'surrogateescape') for s in raw.split(b'\0') if s}
    raw2 = git(repo, 'diff', '--name-only', '-z', 'HEAD')
    changed.update(s.decode('utf-8', 'surrogateescape') for s in raw2.split(b'\0') if s)
    raw3 = git(repo, 'diff', '--cached', '--name-only', '-z')
    changed.update(s.decode('utf-8', 'surrogateescape') for s in raw3.split(b'\0') if s)
    paths = tracked(repo)
    docs = sorted(p for p in paths if Path(p).suffix.lower() in DOC_EXT or Path(p).stem.lower() in DOC_NAMES)
    names = {Path(p).stem.lower() for p in changed if Path(p).stem and len(Path(p).stem) >= 4}
    # Candidate matching is deliberately conservative; words are escaped.
    matches = []
    for p in docs:
        file = repo / p
        if not file.is_file() or file.is_symlink() or file.stat().st_size > 1_000_000:
            continue
        try:
            content = file.read_text('utf-8')
        except UnicodeError:
            continue
        hits = sorted(n for n in names if re.search(r'(?<!\w)' + re.escape(n) + r'(?!\w)', content, re.I))
        if hits or p in changed:
            matches.append({'path': p, 'matched_changed_stems': hits, 'changed_file': p in changed})
    return {'baseline': base, 'changed_paths': sorted(changed), 'documentation_candidates': matches,
            'tracked_documentation_count': len(docs),
            'warning': 'Heuristic candidates only. Review semantic dependencies, untracked files, generated sources, and negative searches manually.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--base', required=True, help='Existing git baseline ref')
    args = parser.parse_args()
    try:
        print(json.dumps(inventory(args.repo.resolve(), args.base), indent=2))
    except (subprocess.CalledProcessError, OSError) as exc:
        parser.exit(2, f'inventory unavailable: {exc}\n')


if __name__ == '__main__':
    main()
