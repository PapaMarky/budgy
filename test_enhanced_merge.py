#!/usr/bin/env python3
"""
Test the enhanced merge logic with real QFX files to detect duplicates with different fitids.
"""
import os
import sys
import tempfile
import glob
from pathlib import Path
# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from budgy.core.database import BudgyDatabase
from budgy.core import load_ofx_file
class DuplicateTracker:
    """Track potential duplicates found during merge"""
    def __init__(self):
        self.duplicates = []
        self.insertions = 0
        self.skipped = 0
    def add_duplicate(self, new_record, existing_record, confidence, reason):
        self.duplicates.append({
            'new': new_record,
            'existing': existing_record,
            'confidence': confidence,
            'reason': reason,
            'action': 'skipped' if 'SKIPPING' in reason else 'inserted'
        })
        if 'SKIPPING' in reason:
            self.skipped += 1
        else:
            self.insertions += 1
def monkey_patch_merge_for_tracking(db, tracker):
    """Monkey patch the merge function to track duplicates"""
    original_merge = db.merge_record
    def tracking_merge(record):
        # Check for duplicate content (ignoring fitid and checknum)
        duplicate_record = db.find_duplicate_by_content(record)
        if duplicate_record is not None:
            old_record = db.record_from_row(duplicate_record)
            # Since all major fields match (account, posted, amount, name, memo, type),
            # this is definitely a duplicate - only fitid/checknum differ
            confidence = 1.0  # 100% confidence since all major fields match
            reason = f'SKIPPING: All content fields match, treating as duplicate'
            tracker.add_duplicate(record, old_record, confidence, reason)
            return
        # Insert new record - call the original insert_record method
        original_merge(record)
    db.merge_record = tracking_merge
def test_qfx_files(qfx_directory):
    """Test merge logic with real QFX files"""
    qfx_path = Path(qfx_directory)
    if not qfx_path.exists():
        print(f"Directory not found: {qfx_directory}")
        return False
    # Find all QFX files
    qfx_files = list(qfx_path.glob("*.qfx")) + list(qfx_path.glob("*.ofx"))
    if not qfx_files:
        print(f"No QFX/OFX files found in: {qfx_directory}")
        return False
    print(f"Found {len(qfx_files)} QFX/OFX files in {qfx_directory}")
    for f in qfx_files:
        print(f"  - {f.name}")
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        test_db_path = tmp_file.name
    try:
        db = BudgyDatabase(test_db_path)
        tracker = DuplicateTracker()
        # Verify the schema uses auto-generated fitids
        result = db.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='transactions'")
        schema = result.fetchone()
        if schema and 'AUTOINCREMENT' in schema[0]:
            print(f"✓ Auto-generated fitids enabled")
        else:
            print("⚠️  Warning: Auto-generated fitids not detected!")
        # Check for content lookup index
        result = db.execute("SELECT sql FROM sqlite_master WHERE type='index' AND name='content_lookup'")
        index = result.fetchone()
        if index:
            print(f"✓ Content lookup index exists")
        else:
            print("⚠️  Content lookup index not found")
        # Monkey patch the merge function to track duplicates
        monkey_patch_merge_for_tracking(db, tracker)
        print(f"\n{'='*80}")
        print("PROCESSING QFX FILES")
        print(f"{'='*80}")
        total_records = 0
        # Process each QFX file
        for qfx_file in sorted(qfx_files):
            print(f"\n--- Processing: {qfx_file.name} ---")
            try:
                records = load_ofx_file(qfx_file)
                print(f"Loaded {len(records)} records from {qfx_file.name}")
                for record in records:
                    db.merge_record(record)
                    total_records += 1
            except Exception as e:
                print(f"Error processing {qfx_file.name}: {e}")
        print(f"\n{'='*80}")
        print("DUPLICATE ANALYSIS RESULTS")
        print(f"{'='*80}")
        print(f"Total records processed: {total_records}")
        print(f"Potential duplicates found: {len(tracker.duplicates)}")
        print(f"  - Skipped (high confidence): {tracker.skipped}")
        print(f"  - Inserted (low confidence): {tracker.insertions}")
        # Show detailed comparison of duplicates
        if tracker.duplicates:
            print(f"\n{'='*80}")
            print("DETAILED DUPLICATE COMPARISON")
            print(f"{'='*80}")
            for i, dup in enumerate(tracker.duplicates, 1):
                new_rec = dup['new']
                old_rec = dup['existing']
                print(f"\n--- Potential Duplicate #{i} ---")
                print(f"Action: {dup['action'].upper()}")
                print(f"Confidence: {dup['confidence']:.1%}")
                print(f"Reason: {dup['reason']}")
                print(f"\nRecord 1 (existing):")
                print(f"  FITID:    {old_rec['fitid']} (auto-generated)")
                print(f"  Account:  {old_rec['account']}")
                print(f"  Posted:   {old_rec['posted']}")
                print(f"  Amount:   {old_rec['amount']}")
                print(f"  Name:     {old_rec['name']}")
                print(f"  Memo:     {old_rec['memo']}")
                print(f"  Type:     {old_rec['type']}")
                print(f"  CheckNum: {old_rec.get('checknum', 'None')}")
                print(f"\nRecord 2 (new, would be inserted):")
                print(f"  Account:  {new_rec['account']}")
                print(f"  Posted:   {new_rec['posted']}")
                print(f"  Amount:   {new_rec['amount']}")
                print(f"  Name:     {new_rec['name']}")
                print(f"  Memo:     {new_rec['memo']}")
                print(f"  Type:     {new_rec['type']}")
                print(f"  CheckNum: {new_rec.get('checknum', 'None')}")
                # Highlight differences (only checknum should differ since content matching excludes checknum)
                differences = []
                # More detailed checknum comparison
                old_checknum = old_rec.get('checknum') or ''
                new_checknum = new_rec.get('checknum') or ''
                if old_checknum != new_checknum:
                    differences.append(f"CheckNum ('{old_checknum}' vs '{new_checknum}')")
                # These should not differ due to our matching logic, but check for completeness
                if old_rec['memo'] != new_rec['memo']:
                    differences.append("Memo (unexpected!)")
                if old_rec['type'] != new_rec['type']:
                    differences.append("Type (unexpected!)")
                if old_rec['account'] != new_rec['account']:
                    differences.append("Account (unexpected!)")
                if old_rec['amount'] != new_rec['amount']:
                    differences.append("Amount (unexpected!)")
                if differences:
                    print(f"\nDifferences: {', '.join(differences)}")
                else:
                    print(f"\nAll fields match except FITID")
        # Analyze patterns in the duplicates
        if tracker.duplicates:
            print(f"\n{'='*80}")
            print("DUPLICATE PATTERNS ANALYSIS")
            print(f"{'='*80}")
            field_diff_counts = {
                'CheckNum': 0,
                'Memo': 0,
                'Type': 0,
                'Account': 0,
                'Amount': 0
            }
            for dup in tracker.duplicates:
                new_rec = dup['new']
                old_rec = dup['existing']
                if old_rec['memo'] != new_rec['memo']:
                    field_diff_counts['Memo'] += 1
                if old_rec['type'] != new_rec['type']:
                    field_diff_counts['Type'] += 1
                if (old_rec.get('checknum') or '') != (new_rec.get('checknum') or ''):
                    field_diff_counts['CheckNum'] += 1
                if old_rec['account'] != new_rec['account']:
                    field_diff_counts['Account'] += 1
                if old_rec['amount'] != new_rec['amount']:
                    field_diff_counts['Amount'] += 1
            print("Fields that differ in potential duplicates:")
            for field, count in field_diff_counts.items():
                if count > 0:
                    percentage = (count / len(tracker.duplicates)) * 100
                    print(f"  {field:10}: {count:3} out of {len(tracker.duplicates)} ({percentage:5.1f}%)")
        # Final database stats
        result = db.execute("SELECT COUNT(*) FROM transactions")
        final_count = result.fetchone()[0]
        # Check fitid uniqueness
        result = db.execute("SELECT COUNT(DISTINCT fitid) FROM transactions")
        unique_fitids = result.fetchone()[0]
        print(f"\n{'='*80}")
        print("FINAL DATABASE STATISTICS")
        print(f"{'='*80}")
        print(f"Records in final database: {final_count}")
        print(f"Unique fitids: {unique_fitids}")
        print(f"Records processed: {total_records}")
        print(f"Duplicates prevented: {tracker.skipped}")
        print(f"Potential duplicates inserted: {tracker.insertions}")
        if final_count != unique_fitids:
            print(f"⚠️  WARNING: {final_count - unique_fitids} records have non-unique fitids!")
            print("   This may cause issues with code that expects fitid to be unique.")
        else:
            print("✓ All fitids are unique")
        if tracker.duplicates:
            prevented_ratio = (tracker.skipped / len(tracker.duplicates)) * 100
            print(f"Duplicate prevention rate: {prevented_ratio:.1f}%")
        return True
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if os.path.exists(test_db_path):
            os.unlink(test_db_path)
            print(f"\nCleaned up test database: {test_db_path}")
def main():
    if len(sys.argv) != 2:
        print("Usage: python3 test_enhanced_merge.py <directory_with_qfx_files>")
        print("Example: python3 test_enhanced_merge.py ~/Documents/Retirement/statements/budget/")
        sys.exit(1)
    qfx_directory = sys.argv[1]
    print(f"Testing enhanced merge logic with QFX files from: {qfx_directory}")
    success = test_qfx_files(qfx_directory)
    sys.exit(0 if success else 1)
if __name__ == '__main__':
    main()