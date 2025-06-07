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
        sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';"
        result = self.execute(sql)
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
            # TODO The unique transaction key needs to include "posted"
            sql = f'CREATE UNIQUE INDEX acct_fitid ON {table_name} (fitid, account);'
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

    def execute(self, sql):
        cursor = self.connection.cursor()
        logging.debug(f'EXECUTE: {sql}')
        return cursor.execute(sql)

    def _open_database(self):
        logging.debug(f'Opening {self.db_path}')
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
        self._create_txn_table_if_missing()
        self._create_category_table_if_missing()
        self._create_rules_table_if_missing()

    def get_record_by_fitid(self, fitid, account):
        sql = f'SELECT * from {self.TXN_TABLE_NAME} WHERE fitid = {fitid} AND account = "{account}";'
        result = self.execute(sql)
        rows = result.fetchall()
        output = []
        for row in rows:
            output.append(row)
            logging.debug(f'Posted: {row[2]} ({type(row[2])})')
        return output

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
        sql = f'INSERT INTO {self.TXN_TABLE_NAME} (fitid, account, type, posted, amount, name, memo, checknum) ' \
              f'VALUEs ({record["fitid"]}, "{record["account"]}", "{record["type"]}", "{record["posted"]}", ' \
              f'{record["amount"]}, "{record["name"]}", "{record["memo"]}", "{checknum}" );'
        result = self.execute(sql)
        self.connection.commit()

    def merge_record(self, record):
        result = self.get_record_by_fitid(record['fitid'], record['account'])
        if result is not None:
            n = len(result)
            # if n > 1:
            #     raise Exception('Multiple records with same fitid')
            print(f'{record["fitid"]}|{record["account"]} matched {n} records')
            if n == 0:
                logging.debug(f'New Record, inserting')
                self.insert_record(record)
                return
            old_record = self.record_from_row(result[0])
            print(f'Old Record: {old_record}')
            logging.info(f'------------------')
            logging.info(f'|{"key":10}|{"NEW":30}|{"OLD":30}|')
            for k in record:
                v1 = record[k] if record[k] is not None else '<NONE>'
                v2 = old_record[k] if old_record[k] is not None else '<NONE>'
                match_text = 'MATCH'
                if v1 != v2:
                    match_text = 'NO MATCH'
                # logging.info(f'|{k:10}|{v1:30}|{v2:30}|{match_text}|')
                print(f'|{k:10}|{v1:30}|{v2:30}|{match_text}|')
        else:
            print(f'Matched no records')


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
        if year is not None or month is not None:
            where_clause = ' WHERE '
            and_clause = ''
            if year is not None:
                where_clause += f'STRFTIME("%Y", posted) = "{year}"'
                and_clause = ' AND '
            if month is not None:
                where_clause += and_clause + f'STRFTIME("%m", posted) = "{month}" '
        sql = (f'SELECT fitid, account, type, posted, amount, name, memo, checknum, category '
               f'FROM {self.TXN_TABLE_NAME} '
               f'{where_clause}'
               f'ORDER BY posted')
        print(sql)
        result = self.execute(sql)
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
        sql = f'SELECT c.name, c.subcategory, c.expense_type FROM {self.TXN_TABLE_NAME} AS t, {self.CATEGORY_TABLE_NAME} AS c WHERE t.fitid = {fitid} AND t.category = c.id'
        result = self.execute(sql)
        if not result:
            return [self.DEFAULT_CATEGORY, '', 0]
        for row in result:
            return row

    def get_category_id(self, category, subcategory):
        sql = f'SELECT id FROM {self.CATEGORY_TABLE_NAME} WHERE name = "{category}" AND subcategory = "{subcategory}"'
        result = self.execute(sql)
        if not result:
            raise Exception(f'Category not in database: "{category}" / "{subcategory}"')
        for row in result:
            return row[0]

    def set_txn_category(self, fitid, category, subcategory):
        category_id = self.get_category_id(category, subcategory)
        sql = f'UPDATE {self.TXN_TABLE_NAME} SET category = {category_id} WHERE fitid = {fitid}'
        self.execute(sql)
        self.connection.commit()

    def bulk_categorize(self, txn_pattern, category, subcategory=EMPTY_SUBCATEGORY, include_categorized=False):
        category_id = self.get_category_id(category, subcategory)
        sql = f'UPDATE {self.TXN_TABLE_NAME} SET category = {category_id} WHERE name LIKE {txn_pattern}'
        if not include_categorized:
            sql += f' AND category = {self.DEFAULT_CATEGORY}'
        result = self.execute(sql)
        if not result:
            raise Exception(f'Bulk Categorize Failed for {txn_pattern} to "{category}" "{subcategory}"')
        self.connection.commit()