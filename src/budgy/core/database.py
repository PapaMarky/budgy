import datetime

import logging
import sqlite3
from typing import List, Dict

class BudgyDatabase(object):
    TXN_TABLE_NAME = 'transactions'
    CATEGORY_TABLE_NAME = 'categories'
    CATEGORY_RULES_TABLE_NAME = 'cat_rules'
    DEFAULT_CATEGORY = 'No Category'
    EMPTY_SUBCATEGORY = ''

    NON_EXPENSE_TYPE = 0
    ONE_TIME_EXPENSE_TYPE = 1
    RECURRING_EXPENSE_TYPE = 2

    connection = None

    def __init__(self, path):
        self.db_path = path
        self._open_database()

    def table_exists(self, table_name):
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name=?;"
        result = self.execute(sql, (table_name,))
        rows = result.fetchall()
        return len(rows) > 0

    def index_exists(self, index_name):
        sql = "SELECT name FROM sqlite_master WHERE type='index' AND name=?;"
        result = self.execute(sql, (index_name,))
        rows = result.fetchall()
        return len(rows) > 0

    def _create_txn_table_if_missing(self):
        table_name = self.TXN_TABLE_NAME
        if not self.table_exists(table_name):
            print(f'Creating table: {table_name}')
            sql = f'CREATE TABLE IF NOT EXISTS {table_name} (' \
                  f'fitid INT, ' \
                  f'account TEXT, ' \
                  f'type TEXT, ' \
                  f'posted TEXT, ' \
                  f'amount FLOAT, ' \
                  f'name TEXT, ' \
                  f'memo TEXT, ' \
                  f'category INT DEFAULT 1, ' \
                  f'checknum TEXT' \
                  f');'
            print(sql)
            result = self.execute(sql)
            logging.debug(f'Create Table Result: {result}')
            sql = f'CREATE UNIQUE INDEX acct_fitid_posted ON {table_name} (fitid, account, posted);'
            result = self.execute(sql)
            logging.debug(f'Create Unique Index: {result}')

    def _create_rules_table_if_missing(self):
        table_name = self.CATEGORY_RULES_TABLE_NAME
        if not self.table_exists(table_name):
            print(f'Creating table: {table_name}')
            sql = f'CREATE TABLE IF NOT EXISTS {table_name} (' \
                   f'id INTEGER PRIMARY KEY AUTOINCREMENT, ' \
                   f'pattern TEXT, ' \
                   f'category TEXT, ' \
                   f'subcategory TEXT ' \
                   f');'
            print(sql)
            result = self.execute(sql)
            logging.debug(f'Create Table Result: {result}')
            print(f'Create Table Result: {result}')

    def _create_category_table_if_missing(self):
        table_name = self.CATEGORY_TABLE_NAME
        if not self.table_exists(table_name):
            print(f'Creating table: {self.CATEGORY_TABLE_NAME}')
            sql = f'CREATE TABLE IF NOT EXISTS {table_name} (' \
                  f'id INTEGER PRIMARY KEY AUTOINCREMENT, ' \
                  f'name TEXT, ' \
                  f'subcategory TEXT, ' \
                  f'expense_type INTEGER DEFAULT 0' \
                  f');'
            result = self.execute(sql)
            logging.debug(f'Create Table Result: {result}')
            print(f'Create Table Result: {result}')
            sql = f'CREATE UNIQUE INDEX category_full ON {table_name} (name, subcategory);'
            result = self.execute(sql)
            logging.debug(f'Create Unique Index: {result}')
            # load default values
            ### expense_type:
            # 0: not an expense
            # 1: one-time expense (like a car purchase)
            # 2: recurring expense (expenses that will continue in retirement)
            default_categories = [
                (self.DEFAULT_CATEGORY, self.EMPTY_SUBCATEGORY, 0),
                ('Expense', self.EMPTY_SUBCATEGORY, 2),
                ('Expense', 'Check', 2),
                ('Auto', self.EMPTY_SUBCATEGORY, 2),
                ('Auto', 'Gas', 2),
                ('Auto', 'Purchase', 1),
                ('Auto', 'Repairs', 2),
                ('Auto', 'Service', 2),
                ('Auto', 'DMV', 2),
                ('Cash Withdrawal', self.EMPTY_SUBCATEGORY, 2),
                ('Clothing', self.EMPTY_SUBCATEGORY, 2),
                ('Dry Cleaning', self.EMPTY_SUBCATEGORY, 2),
                ('Education', self.EMPTY_SUBCATEGORY, 2),
                ('Education', 'Books', 2),
                ('Education', 'College', 1),
                ('Education', 'Professional', 1),
                ('Education', 'Tuition', 1),
                ('Education', 'Post Secondary', 1),
                ('Entertainment', self.EMPTY_SUBCATEGORY, 2),
                ('Entertainment', 'Drinks', 2),
                ('Entertainment', 'Coffee', 2),
                ('Entertainment', 'Dining', 2),
                ('Entertainment', 'Movies', 2),
                ('Entertainment', 'Video Streaming', 2),
                ('Groceries / Food', self.EMPTY_SUBCATEGORY, 2),
                ('Household', self.EMPTY_SUBCATEGORY, 2),
                ('Household', 'Cleaning', 2),
                ('Household', 'Furniture', 2),
                ('Household', 'Gardener', 2),
                ('Household', 'Pool Maintenance', 2),
                ('Household', 'Remodel', 1),
                ('Household', 'Rent', 2),
                ('Household', 'Repairs', 2),
                ('Insurance', self.EMPTY_SUBCATEGORY, 2),
                ('Insurance', 'Auto', 2),
                ('Insurance', 'Home', 2),
                ('Insurance', 'Life', 2),
                ('Insurance', 'Medical', 2),
                ('Postage / Shipping', self.EMPTY_SUBCATEGORY, 2),
                ('Recreation', self.EMPTY_SUBCATEGORY, 2),
                ('Recreation', 'Golf', 2),
                ('Recreation', 'Camping', 2),
                ('Recreation', 'Hobbies', 2),
                ('Rideshare', self.EMPTY_SUBCATEGORY, 2),
                ('Taxes', self.EMPTY_SUBCATEGORY, 1),
                ('Taxes', 'Federal', 1),
                ('Taxes', 'State', 1),
                ('Travel', self.EMPTY_SUBCATEGORY, 2),
                ('Travel', 'Hotel', 2),
                ('Travel', 'Tours', 2),
                ('Travel', 'Transportation (air, sea, rail)', 2),
                ('Utilities', self.EMPTY_SUBCATEGORY, 2),
                ('Utilities', 'Cable', 2),
                ('Utilities', 'Gas / Electric', 2),
                ('Utilities', 'Internet', 2),
                ('Utilities', 'Phone', 2),
                ('Utilities', 'Water', 2),
                ('Income', self.EMPTY_SUBCATEGORY, 0),
                ('Income', 'Dividends', 0),
                ('Income', 'Interest', 0),
                ('Income', 'Salary / Wages', 0),
                ('Income', 'Unemployment', 0),
                ('Savings', self.EMPTY_SUBCATEGORY, 0),
                ('Savings', 'College fund', 0),
                ('Savings', 'Investment', 0),
                ('Savings', 'Retirement', 0),
                ('Shopping', self.EMPTY_SUBCATEGORY, 2),
                ('Shopping', 'Online', 2),
                ('Shopping', 'Amazon', 2),
                ('Transfer', self.EMPTY_SUBCATEGORY, 0),
                ('Medical', self.EMPTY_SUBCATEGORY, 2),
                ('Medical', 'Medicine', 2),
                ('Morgage', self.EMPTY_SUBCATEGORY, 2),
                ('Entertainment', 'Hobbies', 2),
                ('Entertainment', 'Music', 2),
                ('Entertainment', 'Concert', 2),
                ('Tax Preparation', self.EMPTY_SUBCATEGORY, 2),
                ('Work Expense', self.EMPTY_SUBCATEGORY, 2),
                ('Work Expense', 'License', 2),
                ('Auto', 'Rental', 1)
            ]

            print(f'Loading default categories')
            result = result.executemany(
                f'INSERT OR REPLACE INTO {self.CATEGORY_TABLE_NAME} (name, subcategory, expense_type) VALUES (?, ?, ?)',
                default_categories
            )
            print(f'COMMIT default categories')
            self.connection.commit()
            print(f'RESULT: {result}')

    def execute(self, sql, params=None):
        cursor = self.connection.cursor()
        logging.debug(f'EXECUTE: {sql}')
        if params:
            return cursor.execute(sql, params)
        else:
            return cursor.execute(sql)

    def _open_database(self):
        logging.debug(f'Opening {self.db_path}')
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
        self._create_txn_table_if_missing()
        self._create_category_table_if_missing()
        self._create_rules_table_if_missing()
        self.migrate_unique_constraint()

    def get_record_by_fitid(self, fitid, account, posted=None):
        if posted:
            sql = f'SELECT * from {self.TXN_TABLE_NAME} WHERE fitid = ? AND account = ? AND posted = ?;'
            result = self.execute(sql, (fitid, account, posted))
        else:
            sql = f'SELECT * from {self.TXN_TABLE_NAME} WHERE fitid = ? AND account = ?;'
            result = self.execute(sql, (fitid, account))
        rows = result.fetchall()
        output = []
        for row in rows:
            output.append(row)
            logging.debug(f'Posted: {row[3]} ({type(row[3])})')
        return output

    def get_record_by_unique_key(self, fitid, account, posted):
        sql = f'SELECT * from {self.TXN_TABLE_NAME} WHERE fitid = ? AND account = ? AND posted = ?;'
        result = self.execute(sql, (fitid, account, posted))
        rows = result.fetchall()
        if len(rows) > 1:
            raise Exception(f'Multiple records found for unique key: fitid={fitid}, account={account}, posted={posted}')
        return rows[0] if len(rows) == 1 else None

    def record_from_row(self, row):
        checknum = "" if row[7] is None else row[7]
        return {
            'fitid': row[0],
            'account': row[1],
            'type': row[2],
            'posted': row[3], # datetime.datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S%z') ,
            'amount': row[4],
            'name': row[5],
            'memo': row[6],
            'checknum': checknum
        }

    def insert_record(self, record):
        checknum = "" if record['checknum'] is None else record['checknum']
        sql = f'INSERT INTO {self.TXN_TABLE_NAME} (fitid, account, type, posted, amount, name, memo, checknum) VALUES (?, ?, ?, ?, ?, ?, ?, ?);'
        result = self.execute(sql, (
            record["fitid"],
            record["account"],
            record["type"],
            record["posted"],
            record["amount"],
            record["name"],
            record["memo"],
            checknum
        ))
        self.connection.commit()

    def merge_record(self, record):
        existing_record = self.get_record_by_unique_key(record['fitid'], record['account'], record['posted'])
        if existing_record is not None:
            old_record = self.record_from_row(existing_record)
            print(f'Record exists: {record["fitid"]}|{record["account"]}|{record["posted"]}')
            print(f'Old Record: {old_record}')
            logging.info(f'------------------')
            logging.info(f'|{"key":10}|{"NEW":30}|{"OLD":30}|')
            for k in record:
                # Skip fields that were removed from the schema (like 'exclude')
                if k not in old_record:
                    continue
                v1 = record[k] if record[k] is not None else '<NONE>'
                v2 = old_record[k] if old_record[k] is not None else '<NONE>'
                match_text = 'MATCH'
                if v1 != v2:
                    match_text = 'NO MATCH'
                print(f'|{k:10}|{v1:30}|{v2:30}|{match_text}|')
        else:
            print(f'New record, inserting: {record["fitid"]}|{record["account"]}|{record["posted"]}')
            logging.debug(f'New Record, inserting')
            self.insert_record(record)


    def get_date_range(self):
        sql = f'SELECT MIN(posted) AS start, MAX(posted) AS end FROM transactions'
        result = self.execute(sql)
        if result is not None:
            print(f'date range result: "{result}"')
            for row in result:
                print(f'date range row: "{row}"')
                if row[0] is None or row[1] is None:
                    return (None, None)
                start = datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S%z')
                end  = datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S%z')
                return (start, end)
        return (None, None)

    def count_records(self):
        sql = f'SELECT COUNT(*) FROM {self.TXN_TABLE_NAME}'
        result = self.execute(sql)
        count = 0
        if result is not None:
            logging.debug(result)
            for row in result:
                return(row[0])
        return 0

    def get_report(self):
        sql_old = ('SELECT STRFTIME("%Y", posted) AS year, STRFTIME("%m", posted) AS month, SUM(amount) AS expences '
                   'FROM transactions '
                   'WHERE amount < 0 AND NOT exclude '
                   'GROUP BY year, month ORDER BY year, month DESC;')
        sql = ('SELECT STRFTIME("%Y", posted) AS year, STRFTIME("%m", posted) AS month, SUM(ABS(amount)) AS expences '
               'FROM transactions AS txn '
               'WHERE amount < 0 '
               'GROUP BY year, month ORDER BY year, month DESC;')
        print(sql)
        result = self.execute(sql)
        data = {}
        if result is not None:
            for row in result:
                year = row[0]
                expense_month = int(row[1]) - 1
                expense = row[2]
                if year not in data:
                    data[year] = {
                        'months': [None, None, None, None, None, None, None, None, None, None, None, None],
                        'average': None
                    }
                data[year]['months'][expense_month] = expense

            sql = ('SELECT STRFTIME("%Y", posted) AS year, STRFTIME("%m", posted) AS month, SUM(ABS(amount)) AS expences '
                   'FROM transactions AS txn, categories AS cat '
                   'WHERE amount < 0 AND txn.category = cat.id AND NOT cat.expense_type '
                   'GROUP BY year, month ORDER BY year, month DESC;')

            result = self.execute(sql)
            if result is not None:
                for row in result:
                    year = row[0]
                    expense_month = int(row[1]) - 1
                    amount = row[2]
                    data[year]['months'][expense_month] -= amount

            for year in data:
                sum = 0
                n = 0
                data[year]['minimum'] = None
                data[year]['maximum'] = None
                max_expense = None
                for monthly_expense in data[year]['months']:
                    # NOTE: expenses are negative so the max expense is less-than the others
                    if monthly_expense is not None:
                        if data[year]['minimum'] is None:
                            data[year]['minimum'] = monthly_expense
                        else:
                            if monthly_expense < data[year]['minimum']:
                                data[year]['minimum'] = monthly_expense

                        if data[year]['maximum'] is None:
                            data[year]['maximum'] = monthly_expense
                        else:
                            if monthly_expense > data[year]['maximum']:
                                data[year]['maximum'] = monthly_expense

                        sum += float(monthly_expense)
                        n += 1
                data[year]['average'] = sum / n

        return data


    def all_records(self, year=None, month=None) -> List[Dict]:
        where_clause = ''
        params = []
        if year is not None or month is not None:
            where_clause = ' WHERE '
            and_clause = ''
            if year is not None:
                where_clause += 'STRFTIME("%Y", posted) = ?'
                params.append(year)
                and_clause = ' AND '
            if month is not None:
                where_clause += and_clause + 'STRFTIME("%m", posted) = ?'
                params.append(month)
        sql = (f'SELECT fitid, account, type, posted, amount, name, memo, checknum, category '
               f'FROM {self.TXN_TABLE_NAME} '
               f'{where_clause}'
               f'ORDER BY posted')
        print(sql)
        result = self.execute(sql, tuple(params) if params else None)
        records = []
        if result is not None:
            for record in result:
                records.append({
                    'fitid': record[0],
                    'account': record[1],
                    'type': record[2],
                    'posted': record[3],
                    'amount': record[4],
                    'name': record[5],
                    'memo': record[6],
                    'checknum': record[7],
                    'category': record[8] if record[8] != '' else self.DEFAULT_CATEGORY
                })
        return records

    def delete_all_records(self):
        sql = f'DELETE FROM {self.TXN_TABLE_NAME}'
        result = self.execute(sql)

    def merge_records(self, newrecords):
        result = {
            'merged': 0
        }
        print(f'Merging {len(newrecords)}')
        for record in newrecords:
            self.merge_record(record)


    def get_catetory_dict(self):
        sql = f'SELECT name, subcategory, expense_type, id FROM {self.CATEGORY_TABLE_NAME} ORDER BY name'
        result = self.execute(sql)
        category_dict = {}
        for row in result:
            if not row[0] in category_dict:
                category_dict[row[0]] = {}
            category_dict[row[0]][row[1]] = {'expense_type': row[2], 'id': row[3]}
        return category_dict

    def get_category_list(self):
        sql = f'SELECT DISTINCT name FROM {self.CATEGORY_TABLE_NAME} ORDER BY name'
        result = self.execute(sql)
        category_list = []
        for record in result:
            if record[0] == self.DEFAULT_CATEGORY:
                category_list.insert(0, {'name': record[0]})
            else:
                category_list.append({
                    'name': record[0]
                })
        return category_list

    def get_category_for_fitid(self, fitid):
        if fitid is None:
            return [self.DEFAULT_CATEGORY, '', 0]
        sql = f'SELECT c.name, c.subcategory, c.expense_type FROM {self.TXN_TABLE_NAME} AS t, {self.CATEGORY_TABLE_NAME} AS c WHERE t.fitid = ? AND t.category = c.id'
        result = self.execute(sql, (fitid,))
        if not result:
            return [self.DEFAULT_CATEGORY, '', 0]
        rows = result.fetchall()
        if len(rows) == 0:
            return [self.DEFAULT_CATEGORY, '', 0]
        return list(rows[0])

    def get_category_id(self, category, subcategory):
        sql = f'SELECT id FROM {self.CATEGORY_TABLE_NAME} WHERE name = ? AND subcategory = ?'
        result = self.execute(sql, (category, subcategory))
        if not result:
            raise Exception(f'Category not in database: "{category}" / "{subcategory}"')
        for row in result:
            return row[0]

    def set_txn_category(self, fitid, account, posted, category, subcategory):
        category_id = self.get_category_id(category, subcategory)
        sql = f'UPDATE {self.TXN_TABLE_NAME} SET category = ? WHERE fitid = ? AND account = ? AND posted = ?'
        result = self.execute(sql, (category_id, fitid, account, posted))
        rows_affected = result.rowcount
        if rows_affected == 0:
            raise Exception(f'No transaction found for fitid={fitid}, account={account}, posted={posted}')
        elif rows_affected > 1:
            raise Exception(f'Multiple transactions updated for fitid={fitid}, account={account}, posted={posted}')
        self.connection.commit()

    def bulk_categorize(self, txn_pattern, category, subcategory=EMPTY_SUBCATEGORY, include_categorized=False):
        category_id = self.get_category_id(category, subcategory)
        if not include_categorized:
            default_category_id = self.get_category_id(self.DEFAULT_CATEGORY, self.EMPTY_SUBCATEGORY)
            sql = f'UPDATE {self.TXN_TABLE_NAME} SET category = ? WHERE name LIKE ? AND category = ?'
            result = self.execute(sql, (category_id, txn_pattern, default_category_id))
        else:
            sql = f'UPDATE {self.TXN_TABLE_NAME} SET category = ? WHERE name LIKE ?'
            result = self.execute(sql, (category_id, txn_pattern))
        if not result:
            raise Exception(f'Bulk Categorize Failed for {txn_pattern} to "{category}" "{subcategory}"')
        self.connection.commit()

    def migrate_unique_constraint(self):
        """Migrate existing databases to use new unique constraint"""
        old_index_name = 'acct_fitid'
        new_index_name = 'acct_fitid_posted'

        # Check if old index exists and new index doesn't
        if self.index_exists(old_index_name) and not self.index_exists(new_index_name):
            print(f"Migrating database: updating unique constraint to include posted date")

            # Check for existing duplicate records that would violate new constraint
            sql = f'''
                SELECT fitid, account, COUNT(*) as count
                FROM {self.TXN_TABLE_NAME}
                GROUP BY fitid, account
                HAVING count > 1
            '''
            result = self.execute(sql)
            duplicates = result.fetchall()

            if len(duplicates) > 0:
                print(f"Warning: Found {len(duplicates)} fitid/account combinations with multiple records")
                for dup in duplicates:
                    print(f"  fitid={dup[0]}, account={dup[1]}, count={dup[2]}")
                print("These will be allowed under the new constraint (different posted dates)")

            # Drop old index
            print(f"Dropping old index: {old_index_name}")
            self.execute(f'DROP INDEX IF EXISTS {old_index_name}')

            # Create new index
            print(f"Creating new index: {new_index_name}")
            sql = f'CREATE UNIQUE INDEX {new_index_name} ON {self.TXN_TABLE_NAME} (fitid, account, posted);'
            self.execute(sql)

            self.connection.commit()
            print("Migration completed successfully")
        elif self.index_exists(new_index_name):
            print("Database already migrated - new unique constraint exists")
        else:
            print("No migration needed - database appears to be new")