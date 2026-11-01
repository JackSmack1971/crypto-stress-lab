import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_feedback import summarize


class FeedbackTests(unittest.TestCase):
    def test_empty(self):
        r = summarize([])
        self.assertIsNone(r['recall'])
        self.assertEqual(r['records'], 0)

    def test_counts_and_preexisting(self):
        rows = [
            {'case_id': 'a', 'expected_bug': True, 'disposition': 'fixed', 'introduced_by_change': True},
            {'case_id': 'b', 'expected_bug': False, 'disposition': 'confirmed', 'introduced_by_change': False},
            {'case_id': 'c', 'expected_bug': None, 'disposition': 'open', 'introduced_by_change': None},
        ]
        r = summarize(rows)
        self.assertEqual((r['confirmed_true_positive'], r['confirmed_false_positive'], r['preexisting']), (1, 1, 1))
        self.assertEqual(r['independently_labeled'], 2)

    def test_reject_duplicate_and_bad_schema(self):
        row = {'case_id': 'a', 'expected_bug': True, 'disposition': 'fixed', 'introduced_by_change': True}
        for invalid in ([row, row], [{**row, 'expected_bug': 1}], [{**row, 'disposition': 'approved'}], [{}]):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    summarize(invalid)


if __name__ == '__main__':
    unittest.main()
