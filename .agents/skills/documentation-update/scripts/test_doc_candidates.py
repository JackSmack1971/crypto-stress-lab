import tempfile
import unittest
import subprocess
from pathlib import Path
from doc_candidates import inventory


def run(repo, *args):
    subprocess.run(['git', '-C', str(repo), *args], check=True, capture_output=True)


class InventoryTests(unittest.TestCase):
    def test_tracked_docs_and_unstaged_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            run(root, 'init', '-q')
            run(root, 'config', 'user.email', 'test@example.invalid')
            run(root, 'config', 'user.name', 'test')
            (root / 'widget.py').write_text('OLD = 1\n')
            (root / 'README.md').write_text('widget usage\n')
            run(root, 'add', '.')
            run(root, 'commit', '-qm', 'start')
            (root / 'widget.py').write_text('NEW = 2\n')
            result = inventory(root, 'HEAD')
            self.assertIn('widget.py', result['changed_paths'])
            self.assertEqual(result['documentation_candidates'][0]['path'], 'README.md')
            self.assertEqual(result['documentation_candidates'][0]['matched_changed_stems'], ['widget'])

    def test_staged_doc_change_and_spaces(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            run(root, 'init', '-q')
            run(root, 'config', 'user.email', 'test@example.invalid')
            run(root, 'config', 'user.name', 'test')
            (root / 'my module.py').write_text('value=1\n')
            (root / 'usage notes.md').write_text('my module\n')
            run(root, 'add', '.')
            run(root, 'commit', '-qm', 'start')
            (root / 'usage notes.md').write_text('new usage\n')
            run(root, 'add', 'usage notes.md')
            data = inventory(root, 'HEAD')
            self.assertIn('usage notes.md', data['changed_paths'])
            self.assertTrue(any(d['changed_file'] for d in data['documentation_candidates']))

    def test_unchanged_docs_are_not_claimed_exhaustive(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            run(root, 'init', '-q')
            run(root, 'config', 'user.email', 'test@example.invalid')
            run(root, 'config', 'user.name', 'test')
            (root / 'module.py').write_text('value=1\n')
            (root / 'README.md').write_text('overview\n')
            run(root, 'add', '.')
            run(root, 'commit', '-qm', 'start')
            (root / 'module.py').write_text('value=2\n')
            data = inventory(root, 'HEAD')
            self.assertEqual(data['documentation_candidates'], [])
            self.assertIn('Heuristic', data['warning'])


if __name__ == '__main__':
    unittest.main()
