#!/usr/bin/env python3
"""Standalone, read-only lint of this skill package; not runtime conformance."""
import argparse
import re
from pathlib import Path


def validate(root):
    issues = []
    file = root / 'SKILL.md'
    if not file.is_file():
        return ['missing SKILL.md']
    content = file.read_text(encoding='utf-8')
    match = re.match(r'\A---\n(.*?)\n---\n', content, re.S)
    if not match:
        return ['missing or malformed frontmatter']
    fields = {}
    for line in match.group(1).splitlines():
        if ':' not in line:
            issues.append('unsupported frontmatter line')
            continue
        key, value = line.split(':', 1)
        fields[key.strip()] = value.strip().strip('"\'')
    if set(fields) != {'name', 'description'}:
        issues.append('expected name and description fields only')
    name = fields.get('name', '')
    description = fields.get('description', '')
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) or len(name) > 64 or name != root.name:
        issues.append('invalid or mismatched skill name')
    if not description or len(description) > 1024 or '<' in description or '>' in description:
        issues.append('invalid description')
    for ref in re.findall(r'`((?:references|scripts)/[^`\s]+)`', content):
        if not (root / ref).is_file():
            issues.append(f'missing reference {ref}')
    for name in ('references/coordination-contract.md', 'references/handoff-schema.md', 'scripts/check_handoff.py'):
        if not (root / name).is_file():
            issues.append(f'missing required package member {name}')
    return issues


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('skill_dir', nargs='?', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    problems = validate(args.skill_dir.resolve())
    if problems:
        print('\n'.join(f'FAIL: {p}' for p in problems))
        return 1
    print('PASS: package metadata and references; no Codex execution tested')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
