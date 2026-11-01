#!/usr/bin/env python3
"""Validate consistency of a coordination handoff; no filesystem/network mutations."""
import argparse
import json
from pathlib import Path

STATES = {'NEW', 'SCOPED', 'IMPLEMENTING', 'VALIDATING', 'REVIEWING', 'COMPLETE', 'PARTIAL', 'BLOCKED', 'FAILED', 'CANCELLED'}
CHECKS = {'PASS', 'FAIL', 'NOT_RUN', 'BLOCKED', 'INCONCLUSIVE'}
REVIEWS = CHECKS | {'INDEPENDENCE_UNAVAILABLE'}


def check(record):
    errors = []
    if not isinstance(record, dict):
        return ['record must be a JSON object']
    for key in ('task_id', 'baseline', 'revision', 'next'):
        if not isinstance(record.get(key), str):
            errors.append(f'{key}: expected string')
    if not record.get('task_id'):
        errors.append('task_id: empty')
    if record.get('state') not in STATES:
        errors.append('state: unknown')
    if record.get('risk') not in {'L0', 'L1', 'L2', 'L3'}:
        errors.append('risk: unknown')
    for field in ('scope', 'owners', 'acceptance', 'checks', 'findings', 'approvals', 'effects'):
        if not isinstance(record.get(field), list):
            errors.append(f'{field}: expected array')
    if errors:
        return errors
    rev = record['revision']
    for i, owner in enumerate(record['owners']):
        if not isinstance(owner, dict) or not isinstance(owner.get('role'), str) or not isinstance(owner.get('paths'), list):
            errors.append(f'owners[{i}]: invalid owner')
    for i, c in enumerate(record['checks']):
        if not isinstance(c, dict) or c.get('status') not in CHECKS:
            errors.append(f'checks[{i}]: invalid check/status')
            continue
        if c['status'] == 'PASS' and (not c.get('command') or not c.get('evidence') or c.get('revision') != rev or rev in ('unknown', '')):
            errors.append(f'checks[{i}]: PASS requires command, evidence and known matching revision')
    r = record.get('review')
    if not isinstance(r, dict) or not isinstance(r.get('required'), bool) or r.get('status') not in REVIEWS:
        errors.append('review: invalid record')
        r = {'required': True, 'status': 'NOT_RUN'}
    if r['status'] == 'PASS' and (not r.get('evidence') or r.get('revision') != rev or rev in ('unknown', '')):
        errors.append('review: PASS requires evidence and known matching revision')
    if record['state'] == 'COMPLETE':
        if rev in ('unknown', '') or not record['acceptance']:
            errors.append('COMPLETE requires known revision and acceptance criteria')
        if not any(isinstance(c, dict) and c.get('status') == 'PASS' and c.get('revision') == rev for c in record['checks']):
            errors.append('COMPLETE requires a PASS check on current revision')
        if any(not isinstance(c, dict) or c.get('status') != 'PASS' for c in record['checks']):
            errors.append('COMPLETE has non-PASS check')
        if r['required'] and r['status'] != 'PASS':
            errors.append('COMPLETE requires successful required review')
        if any(isinstance(f, dict) and f.get('severity') in ('CRITICAL', 'MAJOR') and f.get('status') != 'RESOLVED' for f in record['findings']):
            errors.append('COMPLETE has unresolved material finding')
        if record.get('next'):
            errors.append('COMPLETE must not have pending next action')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('record', type=Path)
    args = parser.parse_args()
    try:
        obj = json.loads(args.record.read_text(encoding='utf-8'))
    except (OSError, UnicodeError, json.JSONDecodeError) as ex:
        parser.exit(2, f'INVALID INPUT: {ex}\n')
    errors = check(obj)
    if errors:
        for err in errors:
            print(f'FAIL: {err}')
        return 1
    print('PASS: handoff structure internally consistent; external evidence NOT verified')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
