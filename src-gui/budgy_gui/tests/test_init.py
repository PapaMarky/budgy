import unittest
import budgy_gui

class MyTestCase(unittest.TestCase):
    def test_version(self):
        version = budgy_gui.__version__


if __name__ == '__main__':
    unittest.main()
