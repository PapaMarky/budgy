import unittest
from unittest.mock import patch
import logging
import os
import sys
from budgy import importer

logger = logging.getLogger()

class MyTestCase(unittest.TestCase):
    DATADIR = os.path.join(os.path.dirname(__file__), 'testdata')
    DB_PATH = os.path.abspath('./test_importer.db')

    def test_create_app(self):
        self.assertFalse(os.path.exists(self.DB_PATH))
        testargs = ['prog', '--db', self.DB_PATH, os.path.join(self.DATADIR, 'credit.qfx')]
        with patch.object(sys, 'argv', testargs):
            app = importer.ImporterApp()
            self.assertTrue(os.path.exists(self.DB_PATH))
            with patch.object(logger, 'info') as mock_info:
                app.run()
                self.assertTrue(os.path.exists(self.DB_PATH))
            # different code paths are followed when the database already exists
            with patch.object(logger, 'info') as mock_info:
                app.run()
                self.assertTrue(os.path.exists(self.DB_PATH))
                os.remove(self.DB_PATH)

    def test_main(self):
        testargs = ['prog', '--db', self.DB_PATH, os.path.join(self.DATADIR, 'credit.qfx')]
        with patch.object(sys, 'argv', testargs):
            importer.main()
            self.assertTrue(os.path.exists(self.DB_PATH))
            os.remove(self.DB_PATH)


if __name__ == '__main__':
    unittest.main()
