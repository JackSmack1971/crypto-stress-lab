import unittest

from app.store import get_user, page


class StoreTest(unittest.TestCase):
    def test_get_user_rejects_empty_name(self):
        with self.assertRaises(ValueError):
            get_user("")

    def test_page_second_page(self):
        self.assertEqual(page([1, 2, 3, 4, 5], 2), [3, 4])

    def test_page_zero_rejected(self):
        with self.assertRaises(ValueError):
            page([1, 2], 0)


if __name__ == "__main__":
    unittest.main()
