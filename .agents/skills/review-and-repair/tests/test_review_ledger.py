import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'review_ledger.py'

class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.tmp.name) / 'ledger.json')
    def tearDown(self):
        self.tmp.cleanup()
    def run_cli(self, *args, success=True):
        run = subprocess.run([sys.executable, str(SCRIPT), *args, '--file', self.path], capture_output=True, text=True)
        self.assertEqual(run.returncode == 0, success, run.stderr)
        return run
    def test_cap_and_no_reset(self):
        self.run_cli('init', '--task', 'issue-1', '--candidate', 'a')
        self.run_cli('init', '--task', 'issue-1', '--candidate', 'a', success=False)
        for i in range(3):
            self.run_cli('pass', '--task', 'issue-1', '--candidate', str(i), '--reviewer', 'independent')
        self.run_cli('pass', '--candidate', 'new', '--reviewer', 'independent', success=False)
        data = json.loads(Path(self.path).read_text())
        self.assertEqual(len(data['passes']), 3)
        self.assertEqual(data['candidate'], '2')
    def test_identity_and_corruption(self):
        self.run_cli('init', '--task', 'issue-1', '--candidate', 'a')
        self.run_cli('pass', '--task', 'other', '--candidate', 'b', '--reviewer', 'r', success=False)
        self.run_cli('pass', '--candidate', 'b', success=False)
        self.assertEqual(json.loads(Path(self.path).read_text())['passes'], [])
        Path(self.path).write_text('{bad')
        self.run_cli('status', success=False)
    def test_status(self):
        self.run_cli('init', '--task', 't', '--candidate', 'a')
        run = self.run_cli('status')
        self.assertEqual(json.loads(run.stdout)['remaining'], 3)

if __name__ == '__main__':
    unittest.main()
