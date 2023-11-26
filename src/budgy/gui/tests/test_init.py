import unittest

import budgy

class InitTestCase(unittest.TestCase):
    def test_version(self):
        from budgy.gui.version import __version__
        version = __version__


if __name__ == '__main__':
    unittest.main()
