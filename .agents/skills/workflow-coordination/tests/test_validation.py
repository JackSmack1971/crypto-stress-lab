import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_handoff import check
from validate_package import validate


class ValidationTests(unittest.TestCase):
    def record(self):
        return {
            'task_id': 't1', 'state': 'COMPLETE', 'risk': 'L2',
            'baseline': 'sha0', 'revision': 'sha1+diff', 'scope': ['src/a.py'],
            'owners': [{'role': 'writer', 'paths': ['src/a.py']}],
            'acceptance': ['Tests pass'],
            'checks': [{'id': 'test', 'command': 'pytest -q', 'revision': 'sha1+diff', 'status': 'PASS', 'evidence': 'exit=0, log#17'}],
            'findings': [], 'approvals': [], 'effects': ['local src/a.py edit'],
            'review': {'required': True, 'status': 'PASS', 'revision': 'sha1+diff', 'evidence': 'reviewer output#5'}, 'next': ''
        }

    def test_valid_complete(self):
        self.assertEqual(check(self.record()), [])

    def test_not_run_is_not_pass(self):
        r = self.record()
        r['checks'][0]['status'] = 'NOT_RUN'
        self.assertTrue(check(r))

    def test_stale_check(self):
        r = self.record()
        r['checks'][0]['revision'] = 'sha0'
        self.assertTrue(check(r))

    def test_missing_review(self):
        r = self.record()
        r['review']['status'] = 'INDEPENDENCE_UNAVAILABLE'
        self.assertTrue(check(r))

    def test_open_major_finding(self):
        r = self.record()
        r['findings'].append({'severity': 'MAJOR', 'status': 'OPEN', 'evidence': 'failure'})
        self.assertTrue(check(r))

    def test_partial_accepts_missing_checks(self):
        r = self.record()
        r['state'] = 'PARTIAL'
        r['checks'] = []
        r['review']['status'] = 'NOT_RUN'
        r['next'] = 'run tests'
        self.assertEqual(check(r), [])

    def test_non_dict_rejected(self):
        self.assertTrue(check([]))

    def test_package_valid(self):
        self.assertEqual(validate(ROOT), [])

    def test_package_missing_reference(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / ROOT.name
            p.mkdir()
            (p / 'SKILL.md').write_text((ROOT / 'SKILL.md').read_text(), encoding='utf-8')
            self.assertTrue(validate(p))

    def test_cli_failure_exit_code(self):
        r = self.record()
        r['checks'][0]['status'] = 'FAIL'
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'handoff.json'
            path.write_text(json.dumps(r), encoding='utf-8')
            run = subprocess.run([sys.executable, str(ROOT / 'scripts/check_handoff.py'), str(path)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 1)
            self.assertIn('FAIL:', run.stdout)


if __name__ == '__main__':
    unittest.main()
