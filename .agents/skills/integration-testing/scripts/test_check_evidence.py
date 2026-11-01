import copy
import unittest
from check_evidence import validate

GOOD = {'boundaries': [{
    'id': 'client-db', 'contract': 'atomic write', 'environment': 'local-ephemeral',
    'status': 'verified', 'cleanup': 'verified', 'command': 'pytest -q tests/integration',
    'exit_code': 0, 'assertion': 'row matched', 'observation': 'independent query',
    'real_components': ['adapter', 'database'], 'simulated_components': []
}]}

class EvidenceTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(validate(GOOD), [])
    def test_empty(self):
        self.assertTrue(validate({'boundaries': []}))
    def test_false_pass(self):
        record = copy.deepcopy(GOOD)
        record['boundaries'][0]['observation'] = ''
        self.assertTrue(validate(record))
    def test_failed_needs_reason(self):
        record = copy.deepcopy(GOOD)
        record['boundaries'][0]['status'] = 'failed'
        self.assertTrue(validate(record))
    def test_duplicate(self):
        record = copy.deepcopy(GOOD)
        record['boundaries'].append(copy.deepcopy(record['boundaries'][0]))
        self.assertTrue(validate(record))
    def test_type_strict(self):
        record = copy.deepcopy(GOOD)
        record['boundaries'][0]['exit_code'] = False
        self.assertTrue(validate(record))
    def test_no_actual_component(self):
        record = copy.deepcopy(GOOD)
        record['boundaries'][0]['real_components'] = []
        self.assertTrue(validate(record))
    def test_invalid_cleanup(self):
        record = copy.deepcopy(GOOD)
        record['boundaries'][0]['cleanup'] = 'unverified'
        self.assertTrue(validate(record))
    def test_bad_component_type(self):
        record = copy.deepcopy(GOOD)
        record['boundaries'][0]['real_components'] = [None]
        self.assertTrue(validate(record))

if __name__ == '__main__':
    unittest.main()
