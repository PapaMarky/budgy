#! /usr/bin/env python3
import os
import logging

logging.basicConfig(handlers=[logging.StreamHandler()], level=logging.INFO)
logging.info(f'path: {os.getcwd()}')

from budgy.core import load_ofx_file
from budgy.core.database import BudgyDatabase

dbpath = 'simpletest.db'
if os.path.exists(dbpath):
    os.remove(dbpath)

db = BudgyDatabase(dbpath)

records = load_ofx_file('src/budgy/core/tests/testdata/checking.qfx')

db.merge_records(records)
db.merge_records(records)