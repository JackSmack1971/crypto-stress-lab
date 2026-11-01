"""Summarize independently adjudicated review findings; never infer approval or merge readiness.

Input is a JSON array of {case_id, expected_bug, disposition, introduced_by_change}.
`expected_bug` is independently curated ground truth: true, false, or null (unknown).
`disposition` is fixed, confirmed, false_positive, intentional, deferred, or open.
This is analysis only; a reviewer or author cannot establish ground truth by self-labeling.
"""
import argparse
import json
from pathlib import Path

DISPOSITIONS = {'fixed', 'confirmed', 'false_positive', 'intentional', 'deferred', 'open'}


def summarize(records):
    if not isinstance(records, list):
        raise ValueError('expected a JSON array')
    seen = set()
    counts = {k: 0 for k in sorted(DISPOSITIONS)}
    known = hits = false_alarms = 0
    preexisting = 0
    for row in records:
        if not isinstance(row, dict) or set(row) != {'case_id', 'expected_bug', 'disposition', 'introduced_by_change'}:
            raise ValueError('record keys must be case_id, expected_bug, disposition, introduced_by_change')
        case = row['case_id']
        if not isinstance(case, str) or not case.strip() or case in seen:
            raise ValueError('case_id must be unique and nonempty')
        seen.add(case)
        truth, state, introduced = row['expected_bug'], row['disposition'], row['introduced_by_change']
        if truth is not None and type(truth) is not bool:
            raise ValueError('expected_bug must be true, false, or null')
        if introduced is not None and type(introduced) is not bool:
            raise ValueError('introduced_by_change must be true, false, or null')
        if state not in DISPOSITIONS:
            raise ValueError('invalid disposition')
        counts[state] += 1
        preexisting += introduced is False
        if truth is not None:
            known += 1
            reported_real = state in {'fixed', 'confirmed'}
            hits += bool(truth and reported_real)
            false_alarms += bool(not truth and reported_real)
    return {'records': len(records), 'dispositions': counts, 'preexisting': preexisting,
            'independently_labeled': known, 'confirmed_true_positive': hits,
            'confirmed_false_positive': false_alarms,
            'recall': None, 'note': 'Recall cannot be computed without known missed bugs / a complete labeled evaluation set. No gate or authorization is implied.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('records', type=Path)
    a = p.parse_args()
    try:
        print(json.dumps(summarize(json.loads(a.records.read_text(encoding='utf-8'))), indent=2))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        p.exit(2, f'invalid review feedback: {exc}\n')


if __name__ == '__main__':
    main()
