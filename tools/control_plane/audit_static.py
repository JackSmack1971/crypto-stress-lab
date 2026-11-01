"""Run bounded, deterministic CODEX PRIME structural checks without invoking Codex.

This does not validate runtime hooks, permissions, models, network isolation, or model behavior.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHECKS = (
    'validate_config.py',
    'validate_contracts.py',
    'validate_agents.py',
    'validate_skills.py',
    'validate_classification.py',
    'validate_review_rules.py',
)


def run(timeout):
    results = []
    for name in CHECKS:
        try:
            result = subprocess.run(
                [sys.executable, '-I', str(ROOT / 'tools/control_plane' / name)],
                cwd=ROOT, capture_output=True, text=True, timeout=timeout, check=False,
            )
            outcome = 'passed' if result.returncode == 0 else 'failed'
            results.append({'check': name, 'status': outcome, 'exit_code': result.returncode,
                            'output': (result.stdout + result.stderr)[-3000:]})
        except subprocess.TimeoutExpired:
            results.append({'check': name, 'status': 'blocked', 'reason': f'timeout after {timeout}s'})
        except OSError as exc:
            results.append({'check': name, 'status': 'blocked', 'reason': type(exc).__name__})
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--timeout', type=int, default=20, help='per-check timeout in seconds')
    args = parser.parse_args()
    if not 1 <= args.timeout <= 300:
        parser.error('--timeout must be between 1 and 300')
    results = run(args.timeout)
    report = {'scope': 'static-only; no Codex execution or enforcement tested', 'checks': results,
              'all_passed': all(item['status'] == 'passed' for item in results)}
    print(json.dumps(report, indent=2))
    return 0 if report['all_passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
