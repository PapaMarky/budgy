import unittest
from pathlib import Path
from budgy.gui.configdata import BudgyConfig
import pytest

class MyTestCase(unittest.TestCase):
    def test_create(self):
        config = BudgyConfig()
        self.assertIsNotNone(config)

        default_path = Path('~/.config/budgy/budgyconfig.json').expanduser()
        self.assertEqual(config._filepath, default_path)
        d = config.config_dict
        self.assertIsNotNone(d)
        self.assertTrue('database' in d)
        dbconfig = d['database']
        self.assertIsNotNone(dbconfig)
        self.assertTrue('path' in dbconfig)

        with pytest.raises(FileNotFoundError):
            config = BudgyConfig(filepath='/bad/file/path')


if __name__ == '__main__':
    unittest.main()
