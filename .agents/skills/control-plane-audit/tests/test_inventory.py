import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'inventory.py'


class InventoryTests(unittest.TestCase):
    def test_detects_bounded_files_without_following_symlinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'repo'
            root.mkdir()
            (root / 'AGENTS.md').write_text('instructions')
            skill = root / '.agents' / 'skills' / 'audit'
            skill.mkdir(parents=True)
            (skill / 'SKILL.md').write_text('skill')
            (root / 'other.txt').write_text('other')
            result = subprocess.run([sys.executable, str(SCRIPT), '--root', str(root)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual({r['path'] for r in data['records']}, {'AGENTS.md', '.agents/skills/audit/SKILL.md'})
            self.assertFalse(data['truncated'])
            self.assertEqual(data['scanned'], 3)

    def test_rejects_writing_within_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = subprocess.run([sys.executable, str(SCRIPT), '--root', str(root), '--output', str(root / 'audit.json')], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((root / 'audit.json').exists())

    def test_limit_reports_truncation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'AGENTS.md').write_text('x')
            (root / 'SKILL.md').write_text('x')
            result = subprocess.run([sys.executable, str(SCRIPT), '--root', str(root), '--limit', '1'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
            data = json.loads(result.stdout)
            self.assertTrue(data['truncated'])
            self.assertEqual(data['scanned'], 1)


if __name__ == '__main__':
    unittest.main()
