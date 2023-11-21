#! /usr/bin/env python3
import os
import logging

logging.basicConfig(handlers=[logging.StreamHandler()], level=logging.INFO)
logging.info(f'path: {os.getcwd()}')

from budgy import BudgyDatabase, load_ofx_file

dbpath = '../simpletest.db'
if os.path.exists(dbpath):
    os.remove(dbpath)

db = BudgyDatabase(dbpath)

records = load_ofx_file('tests/testdata/checking.qfx')

db.merge_records(records)
db.merge_records(records)