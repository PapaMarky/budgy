from pathlib import Path

import sqlite3
import logging

import ofxtools
from ofxtools.Parser import OFXTree

class BudgyDatabase(object):
    MAX_COMMIT = 10000 # maximum number of records in single commit
    TABLE_NAME = 'transactions'

    def __init__(self, path):
        self.db_path = path
        self.connection = None
        self._open_database()

    def table_exists(self, table_name):
        cursor = self.connection.cursor()
        sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';"
        result = self.execute(sql)
        rows = result.fetchall()
        return len(rows) > 0

    def _create_table_if_missing(self, table_name):
        sql = f'CREATE TABLE IF NOT EXISTS {table_name} (' \
              f'fitid INT PRIMARY KEY, ' \
              f'type TEXT, ' \
              f'posted TEXT, ' \
              f'amount FLOAT, ' \
              f'name TEXT, ' \
              f'memo TEXT, ' \
              f'checknum TEXT ' \
              f');'
        result = self.execute(sql)
        logging.debug(f'Create Table Result: {result}')

    def execute(self, sql):
        cursor = self.connection.cursor()
        logging.debug(f'EXECUTE: {sql}')
        return cursor.execute(sql)

    def _open_database(self):
        logging.debug(f'Opening {self.db_path}')
        self.connection = sqlite3.connect(self.db_path)
        self._create_table_if_missing(self.TABLE_NAME)

    def get_record_by_fitid(self, fitid):
        sql = f'SELECT * from {self.TABLE_NAME} WHERE fitid = {fitid};'
        result = self.execute(sql)
        rows = result.fetchall()
        output = []
        for row in rows:
            output.append(row)
            logging.debug(f'Posted: {row[2]} ({type(row[2])})')
        return output

    def record_from_row(self, row):
        checknum = "" if row[6] is None else row[6]
        return {
            'fitid': row[0],
            'type': row[1],
            'posted': row[2], # datetime.datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S%z') ,
            'amount': row[3],
            'name': row[4],
            'memo': row[5],
            'checknum': checknum
        }

    def insert_record(self, record):
        checknum = "" if record['checknum'] is None else record['checknum']
        sql = f'INSERT INTO {self.TABLE_NAME} (fitid, type, posted, amount, name, memo, checknum) ' \
              f'VALUEs ({record["fitid"]}, "{record["type"]}", "{record["posted"]}", {record["amount"]}, ' \
              f'"{record["name"]}", "{record["memo"]}", "{checknum}" );'
        result = self.execute(sql)
        self.connection.commit()

    def merge_record(self, record):
        result = self.get_record_by_fitid(record['fitid'])
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


    def count_records(self):
        sql = f'SELECT COUNT(*) FROM {self.TABLE_NAME}'
        result = self.execute(sql)
        count = 0
        if result is not None:
            logging.debug(result)
            for row in result:
                return(row[0])
        return 0

    def merge_records(self, newrecords):
        result = {
            'merged': 0
        }
        for record in newrecords:
            self.merge_record(record)
