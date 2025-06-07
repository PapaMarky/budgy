#!/usr/bin/env python3
"""
Test suite for the primary key collision fix.
Tests the migration from (fitid, account) to (fitid, account, posted) unique constraint.
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
    """Test 1: Create new database (should have new index)"""
    print('=== Test 1: New Database ===')
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        test_db = f.name

    try:
        db = BudgyDatabase(test_db)
        print('New database created successfully')
        
        # Check that new index exists
        if db.index_exists('acct_fitid_posted'):
            print_result(True, 'New unique index exists')
        else:
            print_result(False, 'New unique index missing')
            
        if not db.index_exists('acct_fitid'):
            print_result(True, 'Old index not present')
        else:
            print_result(False, 'Old index still exists')
            
    finally:
        safe_remove_db(test_db)

    print('Test 1 completed\n')

def test_migration():
    """Test 2: Simulate old database and test migration"""
    print('=== Test 2: Migration Test ===')
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        test_db = f.name

    try:
        # Create old-style database manually
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        
        # Create old schema
        cursor.execute('''
            CREATE TABLE transactions (
                fitid INT, 
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
        
        # Create old index
        cursor.execute('CREATE UNIQUE INDEX acct_fitid ON transactions (fitid, account);')
        
        # Insert test data (no duplicates yet - old constraint prevents them)
        cursor.execute('''
            INSERT INTO transactions 
            (fitid, account, type, posted, amount, name, memo, checknum) 
            VALUES (12345, 'CHK001', 'DEBIT', '2024-01-01 10:00:00+00:00', -50.00, 'Test Transaction 1', 'memo1', '')
        ''')
        cursor.execute('''
            INSERT INTO transactions 
            (fitid, account, type, posted, amount, name, memo, checknum) 
            VALUES (12346, 'CHK001', 'DEBIT', '2024-01-02 10:00:00+00:00', -75.00, 'Test Transaction 2', 'memo2', '')
        ''')
        
        conn.commit()
        conn.close()
        
        print('Old database created with old index')
        
        # Now open with BudgyDatabase to trigger migration
        db = BudgyDatabase(test_db)
        print('Migration completed')
        
        # Verify migration worked
        if db.index_exists('acct_fitid_posted'):
            print_result(True, 'New unique index exists after migration')
        else:
            print_result(False, 'New unique index missing after migration')
            
        if not db.index_exists('acct_fitid'):
            print_result(True, 'Old index removed after migration')
        else:
            print_result(False, 'Old index still exists after migration')
        
        # Test that records still exist
        records = db.all_records()
        print(f'Records in database: {len(records)}')
        if len(records) == 2:
            print_result(True, 'All records preserved during migration')
        else:
            print_result(False, f'Expected 2 records, got {len(records)}')
            
    finally:
        safe_remove_db(test_db)

    print('Test 2 completed\n')

def test_duplicate_fitid_import():
    """Test 3: Test the core fix - duplicate fitids on different dates"""
    print('=== Test 3: Duplicate FITID Import Test ===')
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        test_db = f.name

    try:
        db = BudgyDatabase(test_db)
        print('Database created')
        
        # Test records with same fitid/account but different posted dates
        record1 = {
            'fitid': 12345,
            'account': 'CHK001',
            'type': 'DEBIT',
            'posted': '2024-01-01 10:00:00+00:00',
            'amount': -50.00,
            'name': 'Coffee Shop',
            'memo': 'Morning coffee',
            'checknum': ''
        }
        
        record2 = {
            'fitid': 12345,  # Same fitid!
            'account': 'CHK001',  # Same account!
            'type': 'DEBIT',
            'posted': '2024-01-02 10:00:00+00:00',  # Different date
            'amount': -75.00,
            'name': 'Gas Station',
            'memo': 'Fill up tank',
            'checknum': ''
        }
        
        print('Importing first record...')
        db.merge_record(record1)
        
        print('Importing duplicate fitid with different date...')
        db.merge_record(record2)
        
        # Check results
        records = db.all_records()
        print(f'Total records in database: {len(records)}')
        
        if len(records) == 2:
            print_result(True, 'Both records imported successfully!')
            print_result(True, 'Primary key collision fix working!')
            for i, record in enumerate(records, 1):
                print(f'  Record {i}: fitid={record["fitid"]}, posted={record["posted"][:10]}, name={record["name"]}')
        else:
            print_result(False, f'Expected 2 records, got {len(records)}')
            
        # Test get_record_by_unique_key
        print('\nTesting precise record retrieval...')
        specific_record = db.get_record_by_unique_key(12345, 'CHK001', '2024-01-01 10:00:00+00:00')
        if specific_record:
            rec = db.record_from_row(specific_record)
            print_result(True, f'Found specific record: {rec["name"]} on {rec["posted"][:10]}')
        else:
            print_result(False, 'Could not find specific record')
            
    finally:
        safe_remove_db(test_db)

    print('Test 3 completed\n')

def test_category_assignment():
    """Test 4: Test category assignment with new unique constraint"""
    print('=== Test 4: Category Assignment Test ===')
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        test_db = f.name

    try:
        db = BudgyDatabase(test_db)
        print('Database created')
        
        # Add test records with same fitid but different dates
        record1 = {
            'fitid': 12345,
            'account': 'CHK001', 
            'type': 'DEBIT',
            'posted': '2024-01-01 10:00:00+00:00',
            'amount': -50.00,
            'name': 'Coffee Shop',
            'memo': 'Morning coffee',
            'checknum': ''
        }
        
        record2 = {
            'fitid': 12345,
            'account': 'CHK001',
            'type': 'DEBIT',
            'posted': '2024-01-02 10:00:00+00:00',
            'amount': -75.00,
            'name': 'Gas Station', 
            'memo': 'Fill up tank',
            'checknum': ''
        }
        
        db.merge_record(record1)
        db.merge_record(record2)
        print('Added 2 records with same fitid, different dates')
        
        # Test category assignment to specific record
        print('\nTesting category assignment...')
        db.set_txn_category(12345, 'CHK001', '2024-01-01 10:00:00+00:00', 'Entertainment', 'Coffee')
        print('Assigned Entertainment/Coffee to first record')
        
        db.set_txn_category(12345, 'CHK001', '2024-01-02 10:00:00+00:00', 'Auto', 'Gas')  
        print('Assigned Auto/Gas to second record')
        
        # Verify categories were assigned correctly
        print('\nVerifying category assignments...')
        
        # Check both records explicitly by retrieving all records
        records = db.all_records()
        coffee_record = None
        gas_record = None
        
        for record in records:
            if 'Coffee' in record['name']:
                coffee_record = record
            elif 'Gas' in record['name']:
                gas_record = record
        
        print(f'Coffee record category: {coffee_record["category"]}')
        print(f'Gas record category: {gas_record["category"]}')
        
        # Check if categories are different (should be different IDs)
        if coffee_record['category'] != gas_record['category']:
            print_result(True, 'Different categories assigned to each record')
            print_result(True, 'Precise category assignment working!')
        else:
            print_result(False, 'Same category assigned to both records')
            
        # Test that wrong parameters don't update anything
        print('\nTesting safety checks...')
        try:
            db.set_txn_category(99999, 'CHK001', '2024-01-01 10:00:00+00:00', 'Entertainment', 'Coffee')
            print_result(False, 'Should have failed with non-existent fitid')
        except Exception as e:
            print_result(True, f'Correctly rejected invalid fitid: {str(e)}')
            
    finally:
        safe_remove_db(test_db)

    print('Test 4 completed\n')

def run_all_tests():
    """Run all tests"""
    print("Running Primary Key Fix Test Suite")
    print("=" * 50)
    
    test_new_database()
    test_migration()
    test_duplicate_fitid_import()
    test_category_assignment()
    
    print("All tests completed!")

if __name__ == "__main__":
    run_all_tests()