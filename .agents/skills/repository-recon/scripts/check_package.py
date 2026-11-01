#!/usr/bin/env python3
"""Dependency-free static checks; does not claim Codex runtime compatibility."""
from pathlib import Path
import json
import re
import sys

root = Path(__file__).resolve().parents[1]
text = (root / 'SKILL.md').read_text(encoding='utf-8')
parts = text.split('---', 2)
assert len(parts) == 3 and not parts[0].strip(), 'missing YAML-like frontmatter'
name = re.search(r'^name:\s*(.+)$', parts[1], re.M)
desc = re.search(r'^description:\s*"(.*)"$', parts[1], re.M)
assert name and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name.group(1))
assert len(name.group(1)) <= 64
assert desc and 1 <= len(desc.group(1)) <= 1024
assert all(x in desc.group(1).lower() for x in ('trace', 'when', 'not for'))
for ref in re.findall(r'\]\((references/[^)]+)\)', parts[2]):
    assert (root / ref).is_file(), f'broken reference: {ref}'
cases = json.loads((root / 'evals/routing_cases.json').read_text(encoding='utf-8'))
assert [len(cases[k]) for k in ('positive', 'negative', 'neighbors')] == [20, 20, 10]
assert len({p for p in cases['positive'] + cases['negative']}) == 40
assert all(x['prompt'] and x['expected'] for x in cases['neighbors'])
print('PASS: frontmatter shape, bounded name/description, reference paths, routing corpus')
print(f'SKILL.md: {len(text)} chars; description: {len(desc.group(1))} chars; routing cases: 50')
