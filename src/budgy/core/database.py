import datetime
from pathlib import Path

import sqlite3
import logging

class BudgyDatabase(object):
    TABLE_NAME = 'transactions'

    def __init__(self, path):
        self.db_path = path
        self.connection = None
        self._open_database()

    def table_exists(self, table_name):
        sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';"
        result = self.execute(sql)
        rows = result.fetchall()
        return len(rows) > 0

    def _create_table_if_missing(self, table_name):
        if not self.table_exists(table_name):
            sql = f'CREATE TABLE IF NOT EXISTS {table_name} (' \
                  f'fitid INT, ' \
                  f'account TEXT, ' \
                  f'type TEXT, ' \
                  f'posted TEXT, ' \
                  f'amount FLOAT, ' \
                  f'name TEXT, ' \
                  f'memo TEXT, ' \
                  f'checknum TEXT, ' \
                  f'category TEXT' \
                  f');'
            result = self.execute(sql)
            logging.debug(f'Create Table Result: {result}')
            sql = f'CREATE UNIQUE INDEX acct_fitid ON {table_name} (fitid, account);'
            result = self.execute(sql)
            logging.debug(f'Create Unique Index: {result}')

    def execute(self, sql):
        cursor = self.connection.cursor()
        logging.debug(f'EXECUTE: {sql}')
        return cursor.execute(sql)

    def _open_database(self):
        logging.debug(f'Opening {self.db_path}')
        self.connection = sqlite3.connect(self.db_path)
        self._create_table_if_missing(self.TABLE_NAME)

    def get_record_by_fitid(self, fitid, account):
        sql = f'SELECT * from {self.TABLE_NAME} WHERE fitid = {fitid} AND account = "{account}";'
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
            'category': row[8]
        }

    def insert_record(self, record):
        checknum = "" if record['checknum'] is None else record['checknum']
        sql = f'INSERT INTO {self.TABLE_NAME} (fitid, account, type, posted, amount, name, memo, checknum, category) ' \
              f'VALUEs ({record["fitid"]}, "{record["account"]}", "{record["type"]}", "{record["posted"]}", ' \
              f'{record["amount"]}, "{record["name"]}", "{record["memo"]}", "{checknum}", "{record["category"]}" );'
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
        sql = f'SELECT COUNT(*) FROM {self.TABLE_NAME}'
        result = self.execute(sql)
        count = 0
        if result is not None:
            logging.debug(result)
            for row in result:
                return(row[0])
        return 0

    def get_report(self):
        sql = ('SELECT STRFTIME("%Y", posted) AS year, STRFTIME("%m", posted) AS month, SUM(amount) AS expences FROM transactions '
               'WHERE amount < 0 GROUP BY year, month ORDER BY year, month DESC;')
        print(sql)
        result = self.execute(sql)
        data = []
        if result is not None:
            for row in result:
                data.append({
                    'year': row[0],
                    'month': row[1],
                    'expenses': row[2]
                })
        return data

    def all_records(self):
        sql = f'SELECT fitid, account, type, posted, amount, name, memo, checknum, category FROM {self.TABLE_NAME} ORDER BY posted'
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
                    'category': record[8]
                })
        return records

    def delete_all_records(self):
        sql = f'DELETE FROM {self.TABLE_NAME}'
        result = self.execute(sql)

    def merge_records(self, newrecords):
        result = {
            'merged': 0
        }
        for record in newrecords:
            self.merge_record(record)
