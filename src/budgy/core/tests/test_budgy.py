import datetime
import os
import unittest
import pytest

import budgy
from budgy.core import load_ofx_file

class BudgyTestCase(unittest.TestCase):
    DATADIR = os.path.join(os.path.dirname(__file__), 'testdata')
    TEST_ID = 'test_id'
    OFX_CHECKING = 'checking.qfx'

    def test_version(self):
        version = budgy.version.__version__
        self.assertIsInstance(version, str)

    def test_import(self):
        records = load_ofx_file(self.OFX_CHECKING)
        self.assertIsNotNone(records)
        self.assertEqual(len(records), 31)

        with pytest.raises(FileNotFoundError):
            records = load_ofx_file('badfile')

    @classmethod
    def setUpClass(cls) -> None:
        if not os.path.isdir(cls.DATADIR):
            raise Exception(f'{os.path.basename(__file__)} DATADIR missing: {cls.DATADIR}')
        cls.OFX_CHECKING = os.path.join(cls.DATADIR, cls.OFX_CHECKING)
        if not os.path.isfile(cls.OFX_CHECKING):
            raise Exception(f'{os.path.basename(__file__)} OFX_CHECKING missing: {cls.OFX_CHECKING}')

        now = datetime.datetime.now()
        cls.TEST_ID = datetime.datetime.strftime(now, '%Y%m%d_%H%M%S')


if __name__ == '__main__':
    unittest.main()
