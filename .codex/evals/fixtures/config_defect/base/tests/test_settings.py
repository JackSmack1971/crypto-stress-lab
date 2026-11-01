import unittest

from app.settings import load


class SettingsTest(unittest.TestCase):
    def test_configured_timeout_is_used(self):
        self.assertEqual(load("config.json")["timeout_seconds"], 5)


if __name__ == "__main__":
    unittest.main()
