import unittest
import vocadbtosqlite.util


class UtilTest(unittest.TestCase):
    def test_json_read(self):
        expected = {'test': True}
        actual = vocadbtosqlite.util.parse_json('resources/sample.json')
        self.assertEqual(actual, expected)  # add assertion here


if __name__ == '__main__':
    unittest.main()
