#!/usr/bin/env python3
"""Compare matched performance observations; stdlib only, read-only."""
import argparse
import csv
import json
import math
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path


def read_samples(path):
    result = {}
    with Path(path).open(newline='', encoding='utf-8-sig') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ['case', 'run', 'value']:
            raise ValueError(f'{path}: expected header case,run,value')
        for line, row in enumerate(reader, start=2):
            if not row['case'] or not row['run']:
                raise ValueError(f'{path}:{line}: empty case/run')
            key = (row['case'], row['run'])
            try:
                value = float(row['value'])
            except (TypeError, ValueError) as exc:
                raise ValueError(f'{path}:{line}: invalid value') from exc
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f'{path}:{line}: value must be finite and positive')
            if key in result:
                raise ValueError(f'{path}:{line}: duplicate pair {key}')
            result[key] = value
    if not result:
        raise ValueError(f'{path}: no observations')
    return result


def compare(base, candidate, direction, min_gain, draws, confidence):
    if base.keys() != candidate.keys():
        missing = sorted(base.keys() - candidate.keys())[:5]
        extra = sorted(candidate.keys() - base.keys())[:5]
        raise ValueError(f'pair identifiers differ; baseline-only={missing}, candidate-only={extra}')
    by_case = defaultdict(list)
    for case, run in sorted(base):
        b, c = base[(case, run)], candidate[(case, run)]
        # Positive means improvement for either metric direction.
        gain = (b - c) / b if direction == 'lower' else (c - b) / b
        by_case[case].append((b, c, gain))
    rng = random.Random(20261031)
    results = []
    for case, samples in sorted(by_case.items()):
        if len(samples) < 5:
            raise ValueError(f'{case}: at least 5 independent paired runs required')
        gains = [s[2] for s in samples]
        estimates = sorted(statistics.median(rng.choices(gains, k=len(gains))) for _ in range(draws))
        lo = estimates[min(draws - 1, int(draws * (1 - confidence) / 2))]
        hi = estimates[min(draws - 1, int(draws * (1 + confidence) / 2))]
        results.append(dict(case=case, pairs=len(samples), baseline_median=statistics.median(s[0] for s in samples),
                            candidate_median=statistics.median(s[1] for s in samples),
                            median_paired_relative_gain=statistics.median(gains), confidence_interval=[lo, hi],
                            meets_threshold=lo > min_gain))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('baseline')
    parser.add_argument('candidate')
    parser.add_argument('--direction', required=True, choices=['lower', 'higher'])
    parser.add_argument('--min-gain', required=True, type=float, help='Predefined minimum relative gain; 0.05 means 5%')
    parser.add_argument('--draws', type=int, default=10000)
    parser.add_argument('--confidence', type=float, default=0.95)
    args = parser.parse_args()
    if not (0 <= args.min_gain < 1 and math.isfinite(args.min_gain)) or args.draws < 1000 or not 0.5 < args.confidence < 1:
        parser.error('min-gain must be [0,1), draws >=1000, confidence in (0.5,1)')
    try:
        cases = compare(read_samples(args.baseline), read_samples(args.candidate), args.direction,
                        args.min_gain, args.draws, args.confidence)
    except (ValueError, OSError) as exc:
        print(f'INVALID: {exc}', file=sys.stderr)
        return 2
    passed = all(c['meets_threshold'] for c in cases)
    print(json.dumps(dict(status='SUPPORTED' if passed else 'NOT_SUPPORTED', method='paired bootstrap median relative gain',
                          confidence=args.confidence, min_gain=args.min_gain, direction=args.direction, cases=cases), indent=2))
    return 0 if passed else 1


if __name__ == '__main__':
    sys.exit(main())
