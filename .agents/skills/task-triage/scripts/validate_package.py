#!/usr/bin/env python3
"""Read-only packaging/fixture validation, not a Codex behavioral test."""
import json
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
skill = (root / 'SKILL.md').read_text(encoding='utf-8')
assert skill.startswith('---\n')
header, body = skill.split('---\n', 2)[1:]
assert re.search(r'^name: task-triage$', header, re.M)
assert re.search(r'^description: .+', header, re.M)
assert len(re.search(r'^description: (.+)$', header, re.M).group(1)) <= 1024
assert not re.search(r'^\w[\w-]*:', header.replace('name:', '', 1).replace('description:', '', 1), re.M)
assert len(body.strip()) > 300
assert (root / 'references/levels-and-boundaries.md').is_file()
corpus=json.loads((root/'evals/routing-corpus.json').read_text(encoding='utf-8'))
counts={k:sum(x['class']==k for x in corpus['routing']) for k in ('positive','negative','neighbor')}
assert counts == {'positive':20,'negative':20,'neighbor':10}, counts
assert len({x['prompt'] for x in corpus['routing']})==50
assert all(isinstance(x['expected_activate'],bool) for x in corpus['routing'])
print('PASS: frontmatter, references, 20/20/10 routing cases, uniqueness; no behavior evaluated')
