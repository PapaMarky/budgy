import datetime
import json
import os.path
import unittest
from budgy.core.database import BudgyDatabase
class TestDatabase(unittest.TestCase):
    TEST_DB = './TESTBUDGY.db'
    DATADIR = os.path.join(os.path.dirname(__file__), 'testdata')
    TEST_ID = 'test_id'
    OFX_CHECKING = 'checking.qfx'
    def test_open(self):
        db = BudgyDatabase(self.TEST_DB)
        self.assertIsNotNone(db)

        self.assertTrue(os.path.exists(self.TEST_DB))
        self.assertTrue(os.path.isfile(self.TEST_DB))

        self.assertFalse(db.table_exists('nonexistent-table'))
        os.remove(self.TEST_DB)

    def test_import(self):
        db = BudgyDatabase(self.TEST_DB)
        self.assertIsNotNone(db)

        self.assertTrue(os.path.exists(self.TEST_DB))
        self.assertTrue(os.path.isfile(self.TEST_DB))

        with open(os.path.join(self.DATADIR, 'checking001.json')) as f:
            test_records = json.loads(f.read())
            n_records = len(test_records)
            dbsize_before = db.count_records()
            db.merge_records(test_records)
            dbsize_after = db.count_records()
            self.assertEqual(dbsize_before + n_records, dbsize_after)

            db.merge_records(test_records)
            dbsize_after2 = db.count_records()
            self.assertEqual(dbsize_after, dbsize_after2)

    @classmethod
    def setUpClass(cls) -> None:
        if not os.path.isdir(cls.DATADIR):
            raise Exception(f'{os.path.basename(__file__)} DATADIR missing: {cls.DATADIR}')
        cls.OFX_CHECKING = os.path.join(cls.DATADIR, cls.OFX_CHECKING)
        if not os.path.isfile(cls.OFX_CHECKING):
            raise Exception(f'{os.path.basename(__file__)} OFX_CHECKING missing: {cls.OFX_CHECKING}')

        now = datetime.datetime.now()
        cls.TEST_ID = datetime.datetime.strftime(now, '%Y%m%d_%H%M%S')
        cls.TEST_DB = f'./TESTBUDGY_{cls.TEST_ID}.db'

if __name__ == '__main__':
    unittest.main()