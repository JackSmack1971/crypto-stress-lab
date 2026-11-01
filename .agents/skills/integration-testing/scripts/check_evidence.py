#!/usr/bin/env python3
"""Check integration evidence record consistency; never execute its commands."""
import argparse
import json
import sys
from pathlib import Path

STATUSES = {'verified', 'failed', 'blocked', 'not tested'}
CLEANUP = {'verified', 'unverified', 'not-applicable'}

def validate(doc):
    errors = []
    if not isinstance(doc, dict) or not isinstance(doc.get('boundaries'), list) or not doc['boundaries']:
        return ['root.boundaries must be a nonempty array']
    seen = set()
    for i, b in enumerate(doc['boundaries']):
        prefix = f'boundaries[{i}]'
        if not isinstance(b, dict):
            errors.append(f'{prefix} must be an object')
            continue
        for field in ('id', 'contract', 'environment', 'status', 'cleanup'):
            if not isinstance(b.get(field), str) or not b[field].strip():
                errors.append(f'{prefix}.{field} must be nonempty string')
        name = b.get('id')
        if isinstance(name, str):
            if name in seen:
                errors.append(f'{prefix}.id duplicated')
            seen.add(name)
        for field in ('real_components', 'simulated_components'):
            if not isinstance(b.get(field), list) or any(not isinstance(x, str) or not x.strip() for x in b.get(field, []) if isinstance(b.get(field), list)):
                errors.append(f'{prefix}.{field} must be array of nonempty strings')
        status = b.get('status')
        if status not in STATUSES:
            errors.append(f'{prefix}.status invalid')
        if b.get('cleanup') not in CLEANUP:
            errors.append(f'{prefix}.cleanup invalid')
        if status == 'verified':
            for field in ('command', 'assertion', 'observation'):
                if not isinstance(b.get(field), str) or not b[field].strip():
                    errors.append(f'{prefix}.{field} required for verified')
            if type(b.get('exit_code')) is not int or b['exit_code'] != 0:
                errors.append(f'{prefix}.exit_code must equal 0 for verified')
            if b.get('cleanup') not in ('verified', 'not-applicable'):
                errors.append(f'{prefix}.cleanup unverified')
            if not b.get('real_components'):
                errors.append(f'{prefix}.real_components empty; cannot claim integration verified')
        elif status in ('failed', 'blocked', 'not tested'):
            if not isinstance(b.get('reason'), str) or not b['reason'].strip():
                errors.append(f'{prefix}.reason required for nonverified status')
            if 'exit_code' in b and type(b['exit_code']) is not int:
                errors.append(f'{prefix}.exit_code must be integer')
    return errors

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('record', type=Path)
    args = p.parse_args()
    try:
        doc = json.loads(args.record.read_text(encoding='utf-8'))
    except (OSError, UnicodeError, ValueError) as e:
        print(f'INVALID: unable to read JSON evidence ({type(e).__name__})', file=sys.stderr)
        return 2
    errors = validate(doc)
    for error in errors:
        print(f'INVALID: {error}', file=sys.stderr)
    if errors:
        return 1
    print(f'VALID RECORD: {len(doc["boundaries"])} boundaries (record consistency only; not test verification)')
    return 0

if __name__ == '__main__':
    sys.exit(main())
