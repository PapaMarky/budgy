import unittest
from unittest.mock import patch
import logging
import os
import sys
import tempfile
import time
from budgy.core import importer

logger = logging.getLogger()

class ImporterTestCase(unittest.TestCase):
    DATADIR = os.path.join(os.path.dirname(__file__), 'testdata')
    DB_PATH = os.path.abspath('./test_importer.db')
    
    def _safe_remove_db(self, db_path):
        """Safely remove database file, handling Windows file locking issues"""
        if not os.path.exists(db_path):
            return
        try:
            os.remove(db_path)
        except (OSError, PermissionError):
            if sys.platform == 'win32':
                # Windows sometimes keeps file handles open
                time.sleep(0.1)
                try:
                    os.remove(db_path)
                except:
                    pass  # Best effort cleanup
            else:
                raise

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
                self._safe_remove_db(self.DB_PATH)

    def test_main(self):
        testargs = ['prog', '--db', self.DB_PATH, os.path.join(self.DATADIR, 'credit.qfx')]
        with patch.object(sys, 'argv', testargs):
            importer.main()
            self.assertTrue(os.path.exists(self.DB_PATH))
            os.remove(self.DB_PATH)


if __name__ == '__main__':
    unittest.main()
