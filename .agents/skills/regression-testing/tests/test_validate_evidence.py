import unittest
from scripts.validate_evidence import validate


def valid_record():
    return {"baseline_status": "not_established", "contracts": [{"id": "C1", "status": "passed", "command_ids": ["r1"]}], "commands": [{"id": "r1", "command": "pytest -q", "status": "passed", "exit_code": 0}], "conclusion": "verified"}


class EvidenceTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(validate(valid_record()), [])

    def test_missing_observation_rejected(self):
        record = valid_record()
        record["commands"][0]["status"] = "not_run"
        record["commands"][0]["exit_code"] = None
        self.assertTrue(validate(record))

    def test_false_verified_rejected(self):
        record = valid_record()
        record["contracts"][0]["status"] = "blocked"
        self.assertTrue(validate(record))

    def test_unknown_command_rejected(self):
        record = valid_record()
        record["contracts"][0]["command_ids"] = ["absent"]
        self.assertTrue(validate(record))

    def test_failed_exit_zero_rejected(self):
        record = valid_record()
        record["commands"][0].update(status="failed", exit_code=0)
        self.assertTrue(validate(record))

    def test_duplicate_ids_rejected(self):
        record = valid_record()
        record["contracts"].append(dict(record["contracts"][0]))
        self.assertTrue(validate(record))

    def test_bool_exit_not_integer(self):
        record = valid_record()
        record["commands"][0]["exit_code"] = False
        self.assertTrue(validate(record))


if __name__ == "__main__":
    unittest.main()
