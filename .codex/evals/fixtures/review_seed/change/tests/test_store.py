import unittest

from app.store import get_user, page


class StoreTest(unittest.TestCase):
    def test_get_user_known(self):
        self.assertEqual(get_user("ada")["name"], "ada")

    def test_page_second_page(self):
        self.assertEqual(page([1, 2, 3, 4, 5], 1), [3, 4])


if __name__ == "__main__":
    unittest.main()
