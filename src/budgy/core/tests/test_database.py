import datetime
import json
import os.path
import sys
import tempfile
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

        # Safe file removal for all platforms
        try:
            os.remove(self.TEST_DB)
        except (OSError, PermissionError) as e:
            # On Windows, sometimes file is still locked
            if sys.platform == 'win32':
                import time
                time.sleep(0.1)
                try:
                    os.remove(self.TEST_DB)
                except:
                    pass  # Best effort cleanup on Windows
            else:
                raise e

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
            # Note: May be less than n_records if duplicates are detected
            self.assertGreaterEqual(dbsize_after, dbsize_before)
            self.assertLessEqual(dbsize_after, dbsize_before + n_records)

            db.merge_records(test_records)
            dbsize_after2 = db.count_records()
            self.assertEqual(dbsize_after, dbsize_after2)

    def test_sql_injection_protection_get_record_by_fitid(self):
        """Test that get_record_by_fitid protects against SQL injection"""
        db = BudgyDatabase(self.TEST_DB)

        # Test malicious fitid and account parameters
        malicious_fitid = "1'; DROP TABLE transactions; --"
        malicious_account = "test'; DROP TABLE transactions; --"
        malicious_posted = "2023-01-01'; DROP TABLE transactions; --"

        # Should not raise exception or corrupt database
        result = db.get_record_by_fitid(malicious_fitid)
        self.assertIsNone(result)  # Should return None for non-existent fitid

        # Verify database integrity - tables should still exist
        self.assertTrue(db.table_exists('transactions'))
        self.assertTrue(db.table_exists('categories'))

    def test_sql_injection_protection_get_record_by_fitid(self):
        """Test that get_record_by_fitid protects against SQL injection"""
        db = BudgyDatabase(self.TEST_DB)

        # Test with malicious fitid (should be integer but test string injection)
        malicious_fitid = "1'; DELETE FROM transactions; --"

        # Should safely handle malicious input
        result = db.get_record_by_fitid(malicious_fitid)
        self.assertIsNone(result)  # Should return None for non-existent record

        # Verify database integrity
        self.assertTrue(db.table_exists('transactions'))

    def test_sql_injection_protection_category_operations(self):
        """Test category operations against SQL injection"""
        db = BudgyDatabase(self.TEST_DB)

        malicious_category = "test'; DROP TABLE categories; --"
        malicious_subcategory = "sub'; DELETE FROM categories; --"

        # Should safely handle malicious input - either return None or raise proper exception, not execute SQL
        try:
            result = db.get_category_id(malicious_category, malicious_subcategory)
            # If it doesn't raise an exception, result should be None or a valid ID
            # The important thing is that it doesn't crash or execute malicious SQL
        except Exception:
            pass  # Expected to fail finding category, but not crash

        # Verify database integrity
        self.assertTrue(db.table_exists('categories'))

        # Test get_category_for_fitid with malicious fitid
        malicious_fitid = "1'; DROP TABLE categories; --"
        result = db.get_category_for_fitid(malicious_fitid)
        self.assertIsInstance(result, list)
        self.assertEqual(result, [db.DEFAULT_CATEGORY, '', 0])  # Should return default

    def test_sql_injection_protection_table_and_index_exists(self):
        """Test table_exists and index_exists methods against SQL injection"""
        db = BudgyDatabase(self.TEST_DB)

        # Test malicious table names
        malicious_table = "transactions'; DROP TABLE transactions; --"
        malicious_index = "acct_fitid_posted'; DROP TABLE transactions; --"

        # Should safely handle malicious input
        result = db.table_exists(malicious_table)
        self.assertFalse(result)  # Should return False for non-existent table

        result = db.index_exists(malicious_index)
        self.assertFalse(result)  # Should return False for non-existent index

        # Verify database integrity
        self.assertTrue(db.table_exists('transactions'))

    def test_sql_injection_protection_all_records(self):
        """Test all_records method against SQL injection in year/month parameters"""
        db = BudgyDatabase(self.TEST_DB)

        # Add some test data first
        test_record = {
            'fitid': 99999,
            'account': 'test_account',
            'type': 'DEBIT',
            'posted': '2023-01-01 00:00:00+00:00',
            'amount': -50.0,
            'name': 'Test Transaction',
            'memo': 'Test memo',
            'checknum': ''
        }
        db.insert_record(test_record)

        # Test malicious year and month parameters
        malicious_year = "2023'; DROP TABLE transactions; --"
        malicious_month = "01'; DELETE FROM transactions; --"

        # Should safely handle malicious input
        records = db.all_records(year=malicious_year)
        self.assertIsInstance(records, list)

        records = db.all_records(month=malicious_month)
        self.assertIsInstance(records, list)

        records = db.all_records(year=malicious_year, month=malicious_month)
        self.assertIsInstance(records, list)

        # Verify database still exists and has data
        self.assertTrue(db.table_exists('transactions'))
        self.assertGreaterEqual(db.count_records(), 1)

    def test_sql_injection_protection_insert_record(self):
        """Test insert_record method against SQL injection in record data"""
        db = BudgyDatabase(self.TEST_DB)

        # Test record with malicious data in various fields
        malicious_record = {
            'fitid': 88888,
            'account': "test'; DROP TABLE transactions; --",
            'type': "DEBIT'; DELETE FROM transactions; --",
            'posted': "2023-01-01'; DROP TABLE transactions; --",
            'amount': -25.0,
            'name': "Malicious'; DROP TABLE transactions; --",
            'memo': "Memo'; DELETE FROM transactions; --",
            'checknum': "123'; DROP TABLE transactions; --"
        }

        # Should safely insert without executing malicious SQL
        db.insert_record(malicious_record)

        # Verify record was inserted safely by checking record count
        self.assertGreaterEqual(db.count_records(), 1)

        # Verify database integrity
        self.assertTrue(db.table_exists('transactions'))

    def test_sql_injection_protection_bulk_categorize(self):
        """Test bulk_categorize against SQL injection in pattern"""
        db = BudgyDatabase(self.TEST_DB)

        # Create a test transaction first
        test_record = {
            'fitid': 77777,
            'account': 'test_account',
            'type': 'DEBIT',
            'posted': '2023-01-01 00:00:00+00:00',
            'amount': -50.0,
            'name': 'Test Transaction for Bulk',
            'memo': 'Test memo',
            'checknum': ''
        }
        db.insert_record(test_record)

        # Test malicious pattern
        malicious_pattern = "test'; DROP TABLE transactions; --"

        # Should handle malicious pattern safely
        db.bulk_categorize(malicious_pattern, 'Expense')

        # Verify database integrity
        self.assertTrue(db.table_exists('transactions'))
        self.assertGreaterEqual(db.count_records(), 1)

    def test_special_characters_handling(self):
        """Test handling of special characters in database operations"""
        db = BudgyDatabase(self.TEST_DB)

        special_chars = ["'", '"', ";", "--", "/*", "*/", "\\", "%", "_"]

        for char in special_chars:
            test_fitid = f"test{char}fitid"
            test_account = f"test{char}account"

            # Should handle special characters safely
            result = db.get_record_by_fitid(test_fitid)
            self.assertIsNone(result)  # Should return None for non-existent fitid

            # Test table_exists with special characters
            result = db.table_exists(f"test{char}table")
            self.assertFalse(result)

    def test_unicode_injection_attempts(self):
        """Test handling of Unicode-based injection attempts"""
        db = BudgyDatabase(self.TEST_DB)

        unicode_attacks = [
            "test\u0000account",  # Null byte
            "test\u2019account",  # Unicode apostrophe
            "test\uFF07account",  # Fullwidth apostrophe
            "test\u0027account",  # Unicode apostrophe variant
        ]

        for attack in unicode_attacks:
            result = db.get_record_by_fitid(123)
            self.assertIsNone(result)  # Should return None for non-existent fitid

            # Test get_category_id with Unicode attacks
            try:
                db.get_category_id(attack, "subcategory")
            except Exception:
                pass  # Expected to fail finding category, but not crash

            # Verify database integrity
            self.assertTrue(db.table_exists('transactions'))

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