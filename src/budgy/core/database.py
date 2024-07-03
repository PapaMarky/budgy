import datetime

import logging
import sqlite3
from typing import List, Dict

class BudgyDatabase(object):
    TXN_TABLE_NAME = 'transactions'
    CATEGORY_TABLE_NAME = 'categoriesX'
    DEFAULT_CATEGORY = 'No Category'
    EMPTY_SUBCATEGORY = ''
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
            sql = f'CREATE TABLE IF NOT EXISTS {table_name} (' \
                  f'fitid INT, ' \
                  f'account TEXT, ' \
                  f'type TEXT, ' \
                  f'posted TEXT, ' \
                  f'amount FLOAT, ' \
                  f'name TEXT, ' \
                  f'memo TEXT, ' \
                  f'category INT DEFAULT 1, ' \
                  f'checknum TEXT, ' \
                  f'exclude BOOL DEFAULT 0' \
                  f');'
            result = self.execute(sql)
            logging.debug(f'Create Table Result: {result}')
            sql = f'CREATE UNIQUE INDEX acct_fitid ON {table_name} (fitid, account);'
            result = self.execute(sql)
            logging.debug(f'Create Unique Index: {result}')

    def _create_category_table_if_missing(self):
        table_name = self.CATEGORY_TABLE_NAME
        if not self.table_exists(table_name):
            print(f'Creating table: {self.CATEGORY_TABLE_NAME}')
            sql = f'CREATE TABLE IF NOT EXISTS {table_name} (' \
                  f'id INTEGER PRIMARY KEY AUTOINCREMENT, ' \
                  f'name TEXT, ' \
                  f'subcategory TEXT, ' \
                  f'is_expense BOOL DEFAULT 0' \
                  f');'
            result = self.execute(sql)
            logging.debug(f'Create Table Result: {result}')
            print(f'Create Table Result: {result}')
            sql = f'CREATE UNIQUE INDEX category_full ON {table_name} (name, subcategory);'
            result = self.execute(sql)
            logging.debug(f'Create Unique Index: {result}')
            # load default values
            default_categories = [
                (self.DEFAULT_CATEGORY, self.EMPTY_SUBCATEGORY, False),
                # Expense categories
                ('Expense', self.EMPTY_SUBCATEGORY, True),
                ('Auto', self.EMPTY_SUBCATEGORY, True),
                ('Auto', 'Gas', True),
                ('Auto', 'Purchase', True),
                ('Auto', 'Repairs', True),
                ('Auto', 'Service', True),
                ('Cash Withdrawal', self.EMPTY_SUBCATEGORY, True),
                ('Clothing', self.EMPTY_SUBCATEGORY, True),
                ('Dry Cleaning', self.EMPTY_SUBCATEGORY, True),
                ('Education', self.EMPTY_SUBCATEGORY, True),
                ('Education', 'Books', True),
                ('Education', 'College', True),
                ('Education', 'Professional', True),
                ('Education', 'Tuition', True),
                ('Entertainment', self.EMPTY_SUBCATEGORY, True),
                ('Entertainment', 'Drinks', True),
                ('Entertainment', 'Coffee', True),
                ('Entertainment', 'Dining', True),
                ('Entertainment', 'Movies', True),
                ('Entertainment', 'Video Streaming', True),
                ('Groceries / Food', self.EMPTY_SUBCATEGORY, True),
                ('Household', self.EMPTY_SUBCATEGORY, True),
                ('Household', 'Cleaning', True),
                ('Household', 'Furniture', True),
                ('Household', 'Gardener', True),
                ('Household', 'Pool Maintenance', True),
                ('Household', 'Remodel', True),
                ('Household', 'Rent', True),
                ('Household', 'Repairs', True),
                ('Insurance', self.EMPTY_SUBCATEGORY, True),
                ('Insurance', 'Auto', True),
                ('Insurance', 'Home', True),
                ('Insurance', 'Life', True),
                ('Insurance', 'Medical', True),
                ('Postage / Shipping', self.EMPTY_SUBCATEGORY, True),
                ('Recreation', self.EMPTY_SUBCATEGORY, True),
                ('Recreation', 'Golf', True),
                ('Recreation', 'Camping', True),
                ('Rideshare', self.EMPTY_SUBCATEGORY, True),
                ('Taxes', self.EMPTY_SUBCATEGORY, True),
                ('Taxes', 'Federal', True),
                ('Taxes', 'State', True),
                ('Travel', self.EMPTY_SUBCATEGORY, True),
                ('Travel', 'Hotel', True),
                ('Travel', 'Tours', True),
                ('Travel', 'Transportation (air, sea, rail)', True),
                ('Utilities', self.EMPTY_SUBCATEGORY, True),
                ('Utilities', 'Cable', True),
                ('Utilities', 'Gas / Electric', True),
                ('Utilities', 'Internet', True),
                ('Utilities', 'Phone', True),
                ('Utilities', 'Water', True),
                # Non-Expense Categories
                ('Income', self.EMPTY_SUBCATEGORY, False),
                ('Income', 'Dividends', False),
                ('Income', 'Interest', False),
                ('Income', 'Salary / Wages', False),
                ('Income', 'Unemployment', False),
                ('Savings', self.EMPTY_SUBCATEGORY, False),
                ('Savings', 'College fund', False),
                ('Savings', 'Investment', False),
                ('Savings', 'Retirement', False),
                ('Transfer', self.EMPTY_SUBCATEGORY, False)
            ]

            print(f'Loading default categories')
            result = result.executemany(
                f'INSERT OR REPLACE INTO {self.CATEGORY_TABLE_NAME} (name, subcategory, is_expense) VALUES (?, ?, ?)',
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
            'checknum': checknum,
            'exclude': row[8] != 0
        }

    def insert_record(self, record):
        checknum = "" if record['checknum'] is None else record['checknum']
        sql = f'INSERT INTO {self.TXN_TABLE_NAME} (fitid, account, type, posted, amount, name, memo, checknum, exclude) ' \
              f'VALUEs ({record["fitid"]}, "{record["account"]}", "{record["type"]}", "{record["posted"]}", ' \
              f'{record["amount"]}, "{record["name"]}", "{record["memo"]}", "{checknum}", "{record["exclude"]}" );'
        result = self.execute(sql)
        self.connection.commit()

    def merge_record(self, record):
        result = self.get_record_by_fitid(record['fitid'], record['account'])
        if result is not None:
            n = len(result)
            # if n > 1:
            #     raise Exception('Multiple records with same fitid')
            if n == 0:
                logging.debug(f'New Record, inserting')
                self.insert_record(record)
                return
            old_record = self.record_from_row(result[0])
            logging.info(f'------------------')
            logging.info(f'|{"key":10}|{"NEW":30}|{"OLD":30}|')
            for k in record:
                v1 = record[k] if record[k] is not None else '<NONE>'
                v2 = old_record[k] if old_record[k] is not None else '<NONE>'
                match_text = 'MATCH'
                if v1 != v2:
                    match_text = 'NO MATCH'
                logging.info(f'|{k:10}|{v1:30}|{v2:30}|{match_text}|')


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
        sql = ('SELECT STRFTIME("%Y", posted) AS year, STRFTIME("%m", posted) AS month, SUM(amount) AS expences FROM transactions '
               'WHERE amount < 0 AND NOT exclude GROUP BY year, month ORDER BY year, month DESC;')
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
                            if monthly_expense > data[year]['minimum']:
                                data[year]['minimum'] = monthly_expense

                        if data[year]['maximum'] is None:
                            data[year]['maximum'] = monthly_expense
                        else:
                            if monthly_expense < data[year]['maximum']:
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
        sql = (f'SELECT fitid, account, type, posted, amount, name, memo, checknum, exclude, category '
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
                    'exclude': record[8] != 0,
                    'category': record[9] if record[9] != '' else 1
                })
        return records

    def delete_all_records(self):
        sql = f'DELETE FROM {self.TXN_TABLE_NAME}'
        result = self.execute(sql)

    def merge_records(self, newrecords):
        result = {
            'merged': 0
        }
        for record in newrecords:
            self.merge_record(record)

    def exclude_fitid(self, fitid:str, exclude:bool):
        exclude_value = 'True' if exclude else 'False'
        sql = f'UPDATE {self.TXN_TABLE_NAME} SET exclude = {exclude_value} WHERE fitid = "{fitid}"'
        self.execute(sql)
        self.connection.commit()

    def get_catetory_dict(self):
        sql = f'SELECT name, subcategory, is_expense, id FROM {self.CATEGORY_TABLE_NAME} ORDER BY name'
        result = self.execute(sql)
        category_dict = {}
        for row in result:
            if not row[0] in category_dict:
                category_dict[row[0]] = {}
            category_dict[row[0]][row[1]] = {'is_expense': row[2] != 0, 'id': row[3]}
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
        sql = f'SELECT c.name, c.subcategory, c.is_expense FROM {self.TXN_TABLE_NAME} AS t, {self.CATEGORY_TABLE_NAME} AS c WHERE t.fitid = {fitid} AND t.category = c.id'
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
