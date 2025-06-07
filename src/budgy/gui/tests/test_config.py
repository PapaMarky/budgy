import unittest
import sys
import tempfile
from pathlib import Path
from budgy.gui.configdata import BudgyConfig
import pytest

class MyTestCase(unittest.TestCase):
    def test_create(self):
        # Use a temporary directory to avoid Windows path issues
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / 'budgy'
            config = BudgyConfig(configdir=config_dir)
            self.assertIsNotNone(config)

            expected_path = config_dir / 'budgyconfig.json'
            self.assertEqual(config._filepath, expected_path.expanduser())
            d = config.config_dict
            self.assertIsNotNone(d)
            self.assertTrue('database' in d)
            dbconfig = d['database']
            self.assertIsNotNone(dbconfig)
            self.assertTrue('path' in dbconfig)

        # Test invalid path - use platform appropriate bad path
        bad_path = '/bad/file/path' if sys.platform != 'win32' else 'Z:\\bad\\file\\path'
        with pytest.raises(FileNotFoundError):
            config = BudgyConfig(filepath=bad_path)


if __name__ == '__main__':
    unittest.main()
