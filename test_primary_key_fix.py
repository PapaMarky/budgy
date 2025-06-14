#!/usr/bin/env python3
"""
Test suite for the auto-generated fitid system.
Tests the migration to auto-generated unique fitids and content-based duplicate detection.
"""
from src.budgy.core.database import BudgyDatabase
import tempfile
import os
import sys
import time
import sqlite3
def safe_remove_db(db_path):
    """Safely remove database file, handling Windows file locking issues"""
    if not os.path.exists(db_path):
        return
    try:
        os.unlink(db_path)
    except (OSError, PermissionError):
        if sys.platform == 'win32':
            # Windows sometimes keeps file handles open
            time.sleep(0.2)
            try:
                os.unlink(db_path)
            except:
                print(f"Warning: Could not remove {db_path} - file may be locked")
        else:
            raise
def print_result(success, message):
    """Print result with Windows-compatible characters"""
    if sys.platform == 'win32':
        # Use ASCII characters on Windows to avoid encoding issues
        status = "[PASS]" if success else "[FAIL]"
    else:
        # Use emojis on other platforms
        status = "✅" if success else "❌"
    print(f'{status} {message}')
def test_new_database():
    """Test 1: Create new database (should have auto-generated fitids)"""
    print('=== Test 1: New Database ===')
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        test_db = f.name
    try:
        db = BudgyDatabase(test_db)
        print('New database created successfully')
        # Check that content lookup index exists
        if db.index_exists('content_lookup'):
            print_result(True, 'Content lookup index exists')
        else:
            print_result(False, 'Content lookup index missing')
        # Check schema for auto-generated fitids
        result = db.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='transactions'")
        schema = result.fetchone()
        if schema and 'AUTOINCREMENT' in schema[0]:
            print_result(True, 'Auto-generated fitids enabled')
        else:
            print_result(False, 'Auto-generated fitids not enabled')
    finally:
        safe_remove_db(test_db)
    print('Test 1 completed\n')
def test_migration():
    """Test 2: Simulate old database and test migration to auto-generated fitids"""
    print('=== Test 2: Migration Test ===')
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        test_db = f.name
    try:
        # Create old-style database manually
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        # Create old schema with TEXT fitids (final old format before auto-generated)
        cursor.execute('''
            CREATE TABLE transactions (
                fitid TEXT,
                account TEXT,
                type TEXT,
                posted TEXT,
                amount FLOAT,
                name TEXT,
                memo TEXT,
                category INT DEFAULT 1,
                checknum TEXT
            )
        ''')
        # Insert test data
        cursor.execute('''
            INSERT INTO transactions
            (fitid, account, type, posted, amount, name, memo, checknum)
            VALUES ('bank_fitid_1', 'CHK001', 'DEBIT', '2024-01-01 10:00:00+00:00', -50.00, 'Test Transaction 1', 'memo1', '')
        ''')
        cursor.execute('''
            INSERT INTO transactions
            (fitid, account, type, posted, amount, name, memo, checknum)
            VALUES ('bank_fitid_2', 'CHK001', 'DEBIT', '2024-01-02 10:00:00+00:00', -75.00, 'Test Transaction 2', 'memo2', '')
        ''')
        conn.commit()
        conn.close()
        print('Old database created with TEXT fitids')
        # Now open with BudgyDatabase to trigger migration
        db = BudgyDatabase(test_db)
        print('Migration completed')
        # Check schema for auto-generated fitids
        result = db.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='transactions'")
        schema = result.fetchone()
        if schema and 'AUTOINCREMENT' in schema[0]:
            print_result(True, 'Migrated to auto-generated fitids')
        else:
            print_result(False, 'Failed to migrate to auto-generated fitids')
        # Test that records still exist
        records = db.all_records()
        print(f'Records in database: {len(records)}')
        if len(records) == 2:
            print_result(True, 'All records preserved during migration')
            # Check that new fitids are integers
            fitids = [record['fitid'] for record in records]
            if all(isinstance(fitid, int) for fitid in fitids):
                print_result(True, 'New fitids are auto-generated integers')
            else:
                print_result(False, 'fitids are not integers')
        else:
            print_result(False, f'Expected 2 records, got {len(records)}')
    finally:
        safe_remove_db(test_db)
    print('Test 2 completed\n')
def test_duplicate_detection():
    """Test 3: Test content-based duplicate detection"""
    print('=== Test 3: Duplicate Detection Test ===')
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        test_db = f.name
    try:
        db = BudgyDatabase(test_db)
        print('Database created')
        # Test records with identical content (should be detected as duplicates)
        record1 = {
            'account': 'CHK001',
            'type': 'DEBIT',
            'posted': '2024-01-01 10:00:00+00:00',
            'amount': -50.00,
            'name': 'Coffee Shop',
            'memo': 'Morning coffee'
        }
        record2 = {
            'account': 'CHK001',
            'type': 'DEBIT',
            'posted': '2024-01-01 10:00:00+00:00',
            'amount': -50.00,
            'name': 'Coffee Shop',
            'memo': 'Morning coffee',
            'checknum': '1234'  # Different checknum (should still be detected as duplicate)
        }
        # Different record (should not be duplicate)
        record3 = {
            'account': 'CHK001',
            'type': 'DEBIT',
            'posted': '2024-01-02 10:00:00+00:00',  # Different date
            'amount': -75.00,  # Different amount
            'name': 'Gas Station',
            'memo': 'Fill up tank'
        }
        print('Importing first record...')
        db.merge_record(record1)
        print('Importing duplicate record (should be skipped)...')
        db.merge_record(record2)
        print('Importing different record...')
        db.merge_record(record3)
        # Check results
        records = db.all_records()
        print(f'Total records in database: {len(records)}')
        if len(records) == 2:
            print_result(True, 'Duplicate detection working - only 2 unique records stored!')
            for i, record in enumerate(records, 1):
                print(f'  Record {i}: fitid={record["fitid"]}, posted={record["posted"][:10]}, name={record["name"]}')
        else:
            print_result(False, f'Expected 2 records, got {len(records)}')
        # Test that we can retrieve records by auto-generated fitid
        print('\nTesting record retrieval by auto-generated fitid...')
        if len(records) >= 1:
            first_fitid = records[0]['fitid']
            retrieved_record = db.get_record_by_fitid(first_fitid)
            if retrieved_record:
                print_result(True, f'Successfully retrieved record by fitid {first_fitid}')
            else:
                print_result(False, f'Could not retrieve record by fitid {first_fitid}')
    finally:
        safe_remove_db(test_db)
    print('Test 3 completed\n')
def test_category_assignment():
    """Test 4: Test category assignment with auto-generated fitids"""
    print('=== Test 4: Category Assignment Test ===')
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        test_db = f.name
    try:
        db = BudgyDatabase(test_db)
        print('Database created')
        # Add test records
        record1 = {
            'account': 'CHK001',
            'type': 'DEBIT',
            'posted': '2024-01-01 10:00:00+00:00',
            'amount': -50.00,
            'name': 'Coffee Shop',
            'memo': 'Morning coffee'
        }
        record2 = {
            'account': 'CHK001',
            'type': 'DEBIT',
            'posted': '2024-01-02 10:00:00+00:00',
            'amount': -75.00,
            'name': 'Gas Station',
            'memo': 'Fill up tank'
        }
        db.merge_record(record1)
        db.merge_record(record2)
        print('Added 2 records')
        records = db.all_records()
        coffee_fitid = None
        gas_fitid = None
        for record in records:
            if 'Coffee' in record['name']:
                coffee_fitid = record['fitid']
            elif 'Gas' in record['name']:
                gas_fitid = record['fitid']
        # Test category assignment using auto-generated fitids
        print('\nTesting category assignment...')
        db.set_txn_category(coffee_fitid, 'Entertainment', 'Coffee')
        print(f'Assigned Entertainment/Coffee to fitid {coffee_fitid}')
        db.set_txn_category(gas_fitid, 'Auto', 'Gas')
        print(f'Assigned Auto/Gas to fitid {gas_fitid}')
        # Verify categories were assigned correctly
        print('\nVerifying category assignments...')
        # Check both records explicitly by retrieving all records
        updated_records = db.all_records()
        coffee_record = None
        gas_record = None
        for record in updated_records:
            if record['fitid'] == coffee_fitid:
                coffee_record = record
            elif record['fitid'] == gas_fitid:
                gas_record = record
        print(f'Coffee record category: {coffee_record["category"]}')
        print(f'Gas record category: {gas_record["category"]}')
        # Check if categories are different (should be different IDs)
        if coffee_record['category'] != gas_record['category']:
            print_result(True, 'Different categories assigned to each record')
            print_result(True, 'Precise category assignment working!')
        else:
            print_result(False, 'Same category assigned to both records')
        # Test that wrong fitid doesn't update anything
        print('\nTesting safety checks...')
        try:
            db.set_txn_category(99999, 'Entertainment', 'Coffee')
            print_result(False, 'Should have failed with non-existent fitid')
        except Exception as e:
            print_result(True, f'Correctly rejected invalid fitid: {str(e)}')
    finally:
        safe_remove_db(test_db)
    print('Test 4 completed\n')
def run_all_tests():
    """Run all tests"""
    print("Running Auto-Generated FITID Test Suite")
    print("=" * 50)
    test_new_database()
    test_migration()
    test_duplicate_detection()
    test_category_assignment()
    print("All tests completed!")
if __name__ == "__main__":
    run_all_tests()
